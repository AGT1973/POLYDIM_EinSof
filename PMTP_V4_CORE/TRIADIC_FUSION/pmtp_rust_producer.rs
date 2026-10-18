// pmtp_rust_producer.rs - PMTP-v4 Triadic Fusion Pillar 1: Rust 2021 Safe SIMD Producer
// Generates S^{D-1} tensors (D=100,000 FP64) with Neumaier Compensated Stiefel Retraction
// Writes directly into Win32 Shared Memory Slab with 128-byte Canonical Wire Descriptor
#![allow(non_camel_case_types)]
#![allow(dead_code)]

use std::env;
use std::process;
use std::ptr;
use std::time::Instant;

pub const DEFAULT_DIMENSION: usize = 100_000;
pub const HEADER_SIZE: usize = 128;
pub const TOTAL_SLAB_SIZE: usize = HEADER_SIZE + (DEFAULT_DIMENSION * std::mem::size_of::<f64>());
pub const DEFAULT_SLAB_NAME: &str = "polydim_v4_triadic_slab";

// ABI exact representation of PmtpWireDescriptor128 (128 bytes)
#[repr(C, packed)]
#[derive(Copy, Clone, Debug)]
pub struct PmtpWireDescriptor128 {
    pub magic: u32,             // 0x504D5450 ("PMTP")
    pub version: u16,           // 4
    pub flags: u16,             // Bitmask: 0x0001 (READ_ONLY_LEASE) | 0x0008 (NEUMAIER_GUARD)
    pub global_epoch: u64,      // Monotonic Epoch
    pub node_id: u32,           // Node ID (1 = Rust Producer)
    pub process_id: u32,        // Process ID
    pub memory_domain: u32,     // 0 = HOST_DRAM_SHM
    pub epoch_state: u32,       // 1 = COMMITTED_READ
    pub total_elements: u64,    // 100,000 elements
    pub dtype: u32,             // 0 = Float64
    pub rank: u32,              // 1
    pub byte_length: u64,       // 800,000 bytes
    pub alignment_padding: u64, // 0
    pub memory_handle: [u8; 64],// Handle / Endpoint
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

pub struct Win32Slab {
    pub h_map: HANDLE,
    pub base_ptr: *mut u8,
    pub is_creator: bool,
    pub size: usize,
}

impl Win32Slab {
    pub fn open_or_create(slab_name: &str, size: usize) -> Result<Self, String> {
        let name_cstr = std::ffi::CString::new(slab_name).map_err(|e| e.to_string())?;
        let invalid_handle = -1isize as usize as HANDLE;

        // Intentar primero OpenFileMappingA
        let mut h = unsafe { OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, name_cstr.as_ptr()) };
        let mut is_creator = false;

        if h.is_null() {
            // Crear si no existe
            h = unsafe {
                CreateFileMappingA(
                    invalid_handle,
                    ptr::null_mut(),
                    PAGE_READWRITE,
                    (size >> 32) as DWORD,
                    (size & 0xFFFFFFFF) as DWORD,
                    name_cstr.as_ptr(),
                )
            };
            if h.is_null() {
                return Err(format!("CreateFileMappingA falló para slab: {}", slab_name));
            }
            is_creator = true;
        }

        let view = unsafe {
            MapViewOfFile(h, FILE_MAP_ALL_ACCESS, 0, 0, size)
        };
        if view.is_null() {
            unsafe { CloseHandle(h); }
            return Err(format!("MapViewOfFile falló para slab: {}", slab_name));
        }

        Ok(Win32Slab {
            h_map: h,
            base_ptr: view as *mut u8,
            is_creator,
            size,
        })
    }
}

impl Drop for Win32Slab {
    fn drop(&mut self) {
        unsafe {
            if !self.base_ptr.is_null() {
                UnmapViewOfFile(self.base_ptr as LPVOID);
            }
            if !self.h_map.is_null() {
                CloseHandle(self.h_map);
            }
        }
    }
}

/// Neumaier Compensated Summation Algorithm
/// Garantiza error residual O(eps) para sumas de alta dimensión en FP64
#[inline(always)]
pub fn neumaier_sum(data: &[f64]) -> f64 {
    let mut sum = 0.0f64;
    let mut c = 0.0f64;
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

/// Neumaier Sum of Squares
#[inline(always)]
pub fn neumaier_sum_sq(data: &[f64]) -> f64 {
    let mut sum = 0.0f64;
    let mut c = 0.0f64;
    for &x in data {
        let x2 = x * x;
        let t = sum + x2;
        if sum.abs() >= x2.abs() {
            c += (sum - t) + x2;
        } else {
            c += (x2 - t) + sum;
        }
        sum = t;
    }
    sum + c
}

/// Retracción de Stiefel a S^{D-1} mediante acumulador Neumaier
pub fn stiefel_retract_unit_sphere(tensor: &mut [f64]) -> (f64, f64) {
    let sum_sq = neumaier_sum_sq(tensor);
    let norm = sum_sq.sqrt();
    if norm > 0.0 {
        let inv_norm = 1.0 / norm;
        for x in tensor.iter_mut() {
            *x *= inv_norm;
        }
    }
    // Verificar norma residual post-retracción
    let verified_sum_sq = neumaier_sum_sq(tensor);
    let verified_norm = verified_sum_sq.sqrt();
    let residual_deviation = (verified_norm - 1.0).abs();
    (verified_norm, residual_deviation)
}

/// Generación determinista / pseudo-aleatoria de vector inicial D-dimensional
pub fn generate_stiefel_tangent_step(dim: usize, epoch: u64, fuzz_subnormal: bool) -> Vec<f64> {
    let mut v = Vec::with_capacity(dim);
    // Generador congruencial lineal determinista para reproducibilidad estricta
    let mut state = 0x12345678_9ABCDEF0_u64 ^ (epoch.wrapping_mul(0x9E3779B97F4A7C15));
    for i in 0..dim {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        let rand_f = ((state >> 11) as f64) / ((1u64 << 53) as f64) - 0.5;
        v.push(rand_f);

        // Inyección de ataque de fuzzing subnormal si está habilitado
        if fuzz_subnormal && (i % 10_000 == 0) {
            // Flotante subnormal IEEE-754: 1e-315
            v[i] = 1.0e-315;
        }
    }
    v
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut batches = 10usize;
    let mut dimension = DEFAULT_DIMENSION;
    let mut fuzz_subnormal = false;
    let mut test_mode = false;
    let mut slab_name = DEFAULT_SLAB_NAME.to_string();

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--batches" => {
                if i + 1 < args.len() {
                    batches = args[i + 1].parse().unwrap_or(10);
                    i += 1;
                }
            }
            "--dim" => {
                if i + 1 < args.len() {
                    dimension = args[i + 1].parse().unwrap_or(DEFAULT_DIMENSION);
                    i += 1;
                }
            }
            "--fuzz-subnormal" => {
                fuzz_subnormal = true;
            }
            "--test" => {
                test_mode = true;
            }
            "--slab-name" => {
                if i + 1 < args.len() {
                    slab_name = args[i + 1].clone();
                    i += 1;
                }
            }
            _ => {}
        }
        i += 1;
    }

    // Static assertions de contrato de memoria
    assert_eq!(std::mem::size_of::<PmtpWireDescriptor128>(), 128, "Wire Descriptor DEBE ser exactamente 128B");

    let total_slab_bytes = HEADER_SIZE + (dimension * std::mem::size_of::<f64>());

    println!("============================================================");
    println!("PMTP-v4 PILLAR 1: RUST 2021 SAFE SIMD PRODUCER (STIEFEL S^{{D-1}})");
    println!("============================================================");
    println!("* Dimension D:          {}", dimension);
    println!("* Slab Name:            {}", slab_name);
    println!("* Total Slab Bytes:     {} ({} MB)", total_slab_bytes, total_slab_bytes / (1024 * 1024));
    println!("* Batches:              {}", batches);
    println!("* Fuzz Subnormal:       {}", fuzz_subnormal);
    println!("* Test Mode:            {}", test_mode);

    let start_all = Instant::now();

    // Abrir o crear Win32 Shared Memory Slab
    let slab = match Win32Slab::open_or_create(&slab_name, total_slab_bytes) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("ERROR fatal abriendo slab: {}", e);
            process::exit(1);
        }
    };

    let desc_ptr = slab.base_ptr as *mut PmtpWireDescriptor128;
    let data_ptr = unsafe { slab.base_ptr.add(HEADER_SIZE) as *mut f64 };

    let mut total_residual_dev = 0.0f64;

    for b in 0..batches {
        let epoch = (b + 1) as u64;
        let t_gen = Instant::now();

        // 1. Generar vector base con o sin subnormales
        let mut tensor = generate_stiefel_tangent_step(dimension, epoch, fuzz_subnormal);

        // 2. Aplicar retracción de Stiefel a S^{D-1} con acumulador Neumaier
        let (norm, residual_dev) = stiefel_retract_unit_sphere(&mut tensor);
        total_residual_dev += residual_dev;

        // 3. Escribir tensor directamente al slab
        unsafe {
            ptr::copy_nonoverlapping(tensor.as_ptr(), data_ptr, dimension);
        }

        // 4. Escribir Wire Descriptor canónico de 128 bytes
        let mut handle = [0u8; 64];
        let tag = format!("slab:{}:epoch:{}", slab_name, epoch);
        let tag_bytes = tag.as_bytes();
        let copy_len = tag_bytes.len().min(63);
        handle[..copy_len].copy_from_slice(&tag_bytes[..copy_len]);

        let desc = PmtpWireDescriptor128 {
            magic: 0x504D5450, // "PMTP"
            version: 4,
            flags: 0x0001 | 0x0008, // READ_ONLY_LEASE | NEUMAIER_GUARD
            global_epoch: epoch,
            node_id: 1, // Rust Producer Node
            process_id: process::id(),
            memory_domain: 0, // HOST_DRAM_SHM
            epoch_state: 1,   // COMMITTED_READ
            total_elements: dimension as u64,
            dtype: 0,         // Float64
            rank: 1,
            byte_length: (dimension * std::mem::size_of::<f64>()) as u64,
            alignment_padding: 0,
            memory_handle: handle,
        };

        unsafe {
            ptr::write_unaligned(desc_ptr, desc);
        }

        let gen_elapsed_us = t_gen.elapsed().as_micros();
        if b == 0 || b == batches - 1 || test_mode {
            println!(
                "Batch {:04} | Epoch {:04} | Norma: {:.15} | Residual Dev: {:.3e} | Latencia: {} us",
                b + 1, epoch, norm, residual_dev, gen_elapsed_us
            );
        }

        // Verificación estricta de invariante de variedad
        if residual_dev > 5.0e-15 {
            eprintln!("FALLO DE INVARIANTE: Residual deviation {:.3e} > 5.0e-15", residual_dev);
            process::exit(2);
        }
    }

    let elapsed = start_all.elapsed();
    let avg_us = elapsed.as_micros() as f64 / batches as f64;
    let avg_ms = avg_us / 1000.0;
    let mean_residual = total_residual_dev / batches as f64;

    println!("------------------------------------------------------------");
    println!("PRODUCCION RUST 2021 FINALIZADA CON EXITO");
    println!("* Total Batches:         {}", batches);
    println!("* Tiempo Total:          {:.3} ms", elapsed.as_secs_f64() * 1000.0);
    println!("* Latencia Media/Batch:  {:.3} ms ({} us)", avg_ms, avg_us as u64);
    println!("* Mean Residual Dev:     {:.3e}", mean_residual);
    println!("* Exit Code:             0");
    println!("============================================================");

    process::exit(0);
}
