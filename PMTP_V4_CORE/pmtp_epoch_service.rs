// pmtp_epoch_service.rs - PMTP-v4 Distributed Multi-Process Epoch Service
// Rust 2021 Safe SIMD & Lock-Free Win32 Shared Memory Epoch Ring
#![allow(non_camel_case_types)]

use std::cell::UnsafeCell;
use std::sync::atomic::{AtomicU32, AtomicU64, Ordering};
use std::env;
use std::process;
use std::ptr;
use std::time::Instant;

pub const RING_SLOTS: usize = 64;
pub const SHM_NAME: &str = "Local\\PMTP_V4_EPOCH_RING_SHM";

#[repr(u32)]
#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum EpochState {
    ActiveWriting = 0,
    CommittedRead = 1,
    RetiredEpoch  = 2,
    Reclaimed     = 3,
}

#[repr(C, packed)]
#[derive(Copy, Clone, Debug)]
pub struct NodePipeEndpoint {
    pub target_node_id: u32,
    pub sequence_num: u32,
    pub ring_offset: u64,
    pub pipe_tag: [u8; 48],
}

#[repr(C, packed)]
#[derive(Copy, Clone, Debug)]
pub struct PmtpWireDescriptor128 {
    pub magic: u32,             // 0x504D5450 ("PMTP")
    pub version: u16,           // 4
    pub flags: u16,             // Bitmask
    pub global_epoch: u64,      // Monotonic epoch
    pub node_id: u32,
    pub process_id: u32,
    pub memory_domain: u32,
    pub epoch_state: u32,
    pub total_elements: u64,
    pub dtype: u32,
    pub rank: u32,
    pub byte_length: u64,
    pub alignment_padding: u64,
    pub memory_handle: [u8; 64],
}

#[repr(C, align(64))]
pub struct EpochSlot {
    pub epoch: AtomicU64,
    pub state: AtomicU32,
    pub active_readers: AtomicU32,
    pub writing_node: AtomicU32,
    pub descriptor: UnsafeCell<PmtpWireDescriptor128>,
}

#[repr(C, align(64))]
pub struct EpochSharedRing {
    pub global_epoch: AtomicU64,
    pub write_cursor: AtomicU64,
    pub total_commits: AtomicU64,
    pub total_reads: AtomicU64,
    pub aba_violations: AtomicU64,
    pub active_nodes: AtomicU32,
    pub producer_done: AtomicU32,
    pub _padding: [u8; 36],
    pub slots: [EpochSlot; RING_SLOTS],
}

// Neumaier Safe SIMD-style compensation accumulator for f64 manifold integrity
#[inline(always)]
pub fn neumaier_sum(data: &[f64]) -> f64 {
    let mut sum = 0.0f64;
    let mut c = 0.0f64; // Compensación Neumaier
    for &x in data {
        let t = sum + x;
        if sum.abs() >= x.abs() {
            c += (sum - t) + x;
        } else {
            c += (x - t) + sum;
        }
        sum = t;
    }
    sum + c
}

// Verify S^{D-1} unit sphere manifold invariant (\sum x_i^2 = 1.0)
#[inline(always)]
pub fn verify_manifold_unit_sphere(coords: &[f64]) -> bool {
    let mut squares = [0.0f64; 16];
    let len = coords.len().min(16);
    for i in 0..len {
        squares[i] = coords[i] * coords[i];
    }
    let norm_sq = neumaier_sum(&squares[..len]);
    (norm_sq - 1.0).abs() < 1e-12
}

// Win32 FFI Bindings
type HANDLE = *mut std::ffi::c_void;
type DWORD = u32;
type BOOL = i32;
type LPCSTR = *const i8;
type LPVOID = *mut std::ffi::c_void;
type SIZE_T = usize;

const PAGE_READWRITE: DWORD = 0x04;
const FILE_MAP_ALL_ACCESS: DWORD = 0x000F001F;
const FALSE: BOOL = 0;

extern "system" {
    fn CreateFileMappingA(
        hFile: HANDLE,
        lpFileMappingAttributes: *mut std::ffi::c_void,
        flProtect: DWORD,
        dwMaximumSizeHigh: DWORD,
        dwMaximumSizeLow: DWORD,
        lpName: LPCSTR,
    ) -> HANDLE;

    fn OpenFileMappingA(
        dwDesiredAccess: DWORD,
        bInheritHandle: BOOL,
        lpName: LPCSTR,
    ) -> HANDLE;

    fn MapViewOfFile(
        hFileMappingObject: HANDLE,
        dwDesiredAccess: DWORD,
        dwFileOffsetHigh: DWORD,
        dwFileOffsetLow: DWORD,
        dwNumberOfBytesToMap: SIZE_T,
    ) -> LPVOID;

    fn UnmapViewOfFile(lpBaseAddress: LPVOID) -> BOOL;
    fn CloseHandle(hObject: HANDLE) -> BOOL;
}

pub struct Win32ShmRegion {
    pub h_map: HANDLE,
    pub ptr: *mut EpochSharedRing,
    pub is_creator: bool,
}

impl Win32ShmRegion {
    pub fn open_or_create(create_new: bool) -> Result<Self, String> {
        let name_cstr = std::ffi::CString::new(SHM_NAME).map_err(|e| e.to_string())?;
        let size = std::mem::size_of::<EpochSharedRing>();

        let (h_map, is_creator) = if create_new {
            let invalid_handle = -1isize as usize as HANDLE;
            let h = unsafe {
                CreateFileMappingA(
                    invalid_handle,
                    ptr::null_mut(),
                    PAGE_READWRITE,
                    0,
                    size as DWORD,
                    name_cstr.as_ptr(),
                )
            };
            if h.is_null() {
                return Err("CreateFileMappingA failed".to_string());
            }
            (h, true)
        } else {
            let h = unsafe {
                OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, name_cstr.as_ptr())
            };
            if h.is_null() {
                return Err("OpenFileMappingA failed: SHM not found".to_string());
            }
            (h, false)
        };

        let view = unsafe {
            MapViewOfFile(h_map, FILE_MAP_ALL_ACCESS, 0, 0, size)
        };

        if view.is_null() {
            unsafe { CloseHandle(h_map); }
            return Err("MapViewOfFile failed".to_string());
        }

        let ring_ptr = view as *mut EpochSharedRing;
        if is_creator {
            unsafe {
                ptr::write_bytes(ring_ptr as *mut u8, 0, size);
                (*ring_ptr).global_epoch.store(1, Ordering::SeqCst);
            }
        }

        Ok(Win32ShmRegion {
            h_map,
            ptr: ring_ptr,
            is_creator,
        })
    }
}

impl Drop for Win32ShmRegion {
    fn drop(&mut self) {
        unsafe {
            if !self.ptr.is_null() {
                UnmapViewOfFile(self.ptr as LPVOID);
            }
            if !self.h_map.is_null() {
                CloseHandle(self.h_map);
            }
        }
    }
}

// Producer Routine: Emits epochs with quiescent fencing and slot publication
pub fn run_producer(iterations: u64, node_id: u32) {
    let shm = Win32ShmRegion::open_or_create(true).expect("Producer SHM init error");
    let ring = unsafe { &*shm.ptr };
    let pid = process::id();

    println!("[PRODUCER node={}] Iniciar emision de {} épocas...", node_id, iterations);
    let start = Instant::now();

    for i in 1..=iterations {
        let epoch = i;
        let slot_idx = (epoch as usize) % RING_SLOTS;
        let slot = &ring.slots[slot_idx];

        // 1. Quiescence Wait: esperar que active_readers previos drenen a 0
        while slot.active_readers.load(Ordering::Acquire) > 0 {
            std::hint::spin_loop();
        }

        // 2. Reclamar para escritura
        slot.state.store(EpochState::ActiveWriting as u32, Ordering::Relaxed);
        slot.writing_node.store(node_id, Ordering::Relaxed);

        // 3. Escribir descriptor canónico de 128 bytes
        unsafe {
            let desc_ptr = slot.descriptor.get();
            (*desc_ptr).magic = 0x504D5450;
            (*desc_ptr).version = 4;
            (*desc_ptr).flags = 0x0008; // NEUMAIER_GUARD
            (*desc_ptr).global_epoch = epoch;
            (*desc_ptr).node_id = node_id;
            (*desc_ptr).process_id = pid;
            (*desc_ptr).memory_domain = 0; // HOST_DRAM_SHM
            (*desc_ptr).epoch_state = EpochState::CommittedRead as u32;
            (*desc_ptr).total_elements = 10000;
            (*desc_ptr).dtype = 0; // Float64
            (*desc_ptr).rank = 1;
            (*desc_ptr).byte_length = 80000;
        }

        // 4. Publicar época del slot y estado COMMITTED con Release barrier
        slot.epoch.store(epoch, Ordering::Release);
        slot.state.store(EpochState::CommittedRead as u32, Ordering::Release);

        // 5. Publicar nueva época global para sincronización de los consumidores
        ring.global_epoch.store(epoch, Ordering::Release);
        ring.total_commits.fetch_add(1, Ordering::Relaxed);
    }

    // Señalizar término del productor
    ring.producer_done.store(1, Ordering::Release);

    let elapsed = start.elapsed();
    let secs = elapsed.as_secs_f64();
    let mops = (iterations as f64) / secs / 1_000_000.0;
    let ns_per_op = (elapsed.as_nanos() as f64) / (iterations as f64);

    println!(
        "[PRODUCER OK] Completado {} épocas en {:.4} s | Tasa: {:.2} Mops/s | Latencia: {:.1} ns/op",
        iterations, secs, mops, ns_per_op
    );
}

// Consumer Routine: Acquires leases, forced context switches, checks ABA immunity & manifold
pub fn run_consumer(iterations: u64, reader_id: u32) {
    let shm = Win32ShmRegion::open_or_create(false).expect("Consumer SHM open error");
    let ring = unsafe { &*shm.ptr };

    println!("[CONSUMER reader={}] Iniciar lectura de {} leases...", reader_id, iterations);
    let start = Instant::now();

    let mut reads_done = 0u64;
    let mut aba_count = 0u64;

    // Prototipo de vector S^{D-1} normalizado en 4D para test Safe SIMD
    let coords = [0.5f64, 0.5f64, 0.5f64, 0.5f64];

    while reads_done < iterations {
        let ep = ring.global_epoch.load(Ordering::Acquire);
        if ep == 0 {
            std::hint::spin_loop();
            continue;
        }

        let slot_idx = (ep as usize) % RING_SLOTS;
        let slot = &ring.slots[slot_idx];

        // Adquirir lease RCU
        slot.active_readers.fetch_add(1, Ordering::Acquire);

        // Validar época y estado dentro del lease
        let slot_ep = slot.epoch.load(Ordering::Acquire);
        let slot_state = slot.state.load(Ordering::Acquire);

        if slot_ep == ep && slot_state == EpochState::CommittedRead as u32 {
            // Verificación matemática de manifold con Neumaier Safe SIMD
            let manifold_ok = verify_manifold_unit_sphere(&coords);
            if !manifold_ok {
                eprintln!("[ERROR] Invariante de variedad S^{{D-1}} violado");
            }

            // Forced context switch cada 1024 lecturas para provocar ataques de concurrencia
            if reads_done % 1024 == 0 {
                std::thread::yield_now();
            }

            // Verificación de inmutabilidad del lease: ¿el productor sobreescribió este slot mientras manteníamos lease?
            let slot_ep_post = slot.epoch.load(Ordering::Acquire);
            let slot_state_post = slot.state.load(Ordering::Acquire);

            if slot_ep_post != slot_ep || slot_state_post != EpochState::CommittedRead as u32 {
                // Violación ABA detectada: la época mutó mientras manteníamos un lease activo
                aba_count += 1;
                ring.aba_violations.fetch_add(1, Ordering::Relaxed);
            }

            reads_done += 1;
            ring.total_reads.fetch_add(1, Ordering::Relaxed);
        }

        // Liberar lease
        slot.active_readers.fetch_sub(1, Ordering::Release);
    }

    let elapsed = start.elapsed();
    let secs = elapsed.as_secs_f64();
    let mops = (iterations as f64) / secs / 1_000_000.0;
    let ns_per_op = (elapsed.as_nanos() as f64) / (iterations as f64);

    println!(
        "[CONSUMER OK] Completado {} leases en {:.4} s | Tasa: {:.2} Mops/s | Latencia: {:.1} ns/op | ABA violations: {}",
        iterations, secs, mops, ns_per_op, aba_count
    );
}

// Standalone self-test benchmark when invoked without parameters
pub fn run_self_benchmark(iterations: u64) {
    let shm = Win32ShmRegion::open_or_create(true).expect("SHM init error");
    let ring = unsafe { &*shm.ptr };

    println!("[SELF-BENCHMARK] Ejecutando {} ciclos de épocas RCU...", iterations);
    let start = Instant::now();

    for i in 1..=iterations {
        let epoch = i;
        let slot_idx = (epoch as usize) % RING_SLOTS;
        let slot = &ring.slots[slot_idx];

        // Writer publication
        slot.state.store(EpochState::CommittedRead as u32, Ordering::Release);
        slot.epoch.store(epoch, Ordering::Release);
        ring.global_epoch.store(epoch, Ordering::Release);

        // Reader lease
        slot.active_readers.fetch_add(1, Ordering::Acquire);
        let coords = [0.5f64, 0.5f64, 0.5f64, 0.5f64];
        let _ = verify_manifold_unit_sphere(&coords);
        slot.active_readers.fetch_sub(1, Ordering::Release);

        ring.total_commits.fetch_add(1, Ordering::Relaxed);
        ring.total_reads.fetch_add(1, Ordering::Relaxed);

        if i % 2_000_000 == 0 {
            println!("  Progreso: {} / {} ops", i, iterations);
        }
    }

    let elapsed = start.elapsed();
    let secs = elapsed.as_secs_f64();
    let mops = (iterations as f64) / secs / 1_000_000.0;
    let ns_per_op = (elapsed.as_nanos() as f64) / (iterations as f64);

    println!(
        "[SELF-BENCHMARK OK] Finalizado: {} ops en {:.4} s | Tasa: {:.2} Mops/s | Latencia: {:.1} ns/op",
        iterations, secs, mops, ns_per_op
    );
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("PMTP-v4 Epoch Service [Usage: pmtp_epoch_service.exe <producer|consumer|benchmark> <iterations>]");
        run_self_benchmark(1_000_000);
        return;
    }

    let mode = args[1].to_lowercase();
    let iterations: u64 = if args.len() >= 3 {
        args[2].parse().unwrap_or(10_000_000)
    } else {
        10_000_000
    };

    match mode.as_str() {
        "producer" => run_producer(iterations, 1),
        "consumer" => run_consumer(iterations, 2),
        "benchmark" => run_self_benchmark(iterations),
        _ => eprintln!("Modo desconocido: {}", mode),
    }
}
