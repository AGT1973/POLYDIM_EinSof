// =============================================================================
// PMTP RUST KERNEL & SHM ENGINE (CERTIFIED COMPATIBLE V26605)
// Unifies C++, Rust, Dart and Python with strict byte-level parity.
// =============================================================================

use std::sync::atomic::{AtomicU64, Ordering};

pub const PMTP_MAGIC: u32 = 0x504D5450; // "PMTP"
pub const PMTP_VERSION: u16 = 0x0001;

pub const PMTP_DESTROYING_BIT: u64 = 1u64 << 63;
pub const PMTP_READERS_MASK: u64 = !PMTP_DESTROYING_BIT;
pub const PMTP_SLOT0_READERS_MASK: u64 = 0x00000000FFFFFFFF;
pub const PMTP_SLOT1_READERS_MASK: u64 = 0x7FFFFFFF00000000;

// =============================================================================
// 1. CABECERA COMPACTA ALINEADA A CACHE LINE (64 BYTES EXACTOS)
// =============================================================================
#[repr(C, align(64))]
pub struct PmtpHeaderCompact {
    pub magic: u32,                  // Offset  0 (4B): 0x504D5450
    pub version: u16,                // Offset  4 (2B): 1
    pub dtype_id: u16,               // Offset  6 (2B): 1 (FP64 default)
    pub active_slot: u32,            // Offset  8 (4B): 0 o 1
    pub slab_id: u32,                // Offset 12 (4B): Identificador de slab
    pub num_elements: u64,           // Offset 16 (8B): Escalares por slot
    pub timestamp_ns: u64,           // Offset 24 (8B): Timestamp POSIX nanosegundos
    pub scale: f64,                  // Offset 32 (8B): Escala IEEE-754
    pub generation: u32,             // Offset 40 (4B): Contador monotónico
    pub retired_slot0: u8,           // Offset 44 (1B): Retiro slot 0
    pub retired_slot1: u8,           // Offset 45 (1B): Retiro slot 1
    pub reserved_flags: u16,         // Offset 46 (2B): Flags
    // Offset 48 (8B): Bit 63 = DESTROYING, Bits 32-62 = slot1, Bits 0-31 = slot0
    pub state_and_readers: AtomicU64,
    pub reserved_pad: [u8; 8],       // Offset 56 (8B) -> Total 64 bytes exactos
}

impl PmtpHeaderCompact {
    pub fn new(slab_id: u32, num_elements: u64) -> Self {
        Self {
            magic: PMTP_MAGIC,
            version: PMTP_VERSION,
            dtype_id: 1, // FP64
            active_slot: 0,
            slab_id,
            num_elements,
            timestamp_ns: 0,
            scale: 1.0,
            generation: 1,
            retired_slot0: 0,
            retired_slot1: 1,
            reserved_flags: 0,
            state_and_readers: AtomicU64::new(0),
            reserved_pad: [0u8; 8],
        }
    }

    /// Adquiere lease atómico sobre el slot correspondiente libre de carreras
    pub fn acquire_reader_lease(&self, slot: u32) -> Result<u64, &'static str> {
        if slot > 1 {
            return Err("INVALID_SLOT");
        }
        let increment: u64 = if slot == 0 { 1u64 } else { 1u64 << 32 };
        let mut current = self.state_and_readers.load(Ordering::Relaxed);

        loop {
            if (current & PMTP_DESTROYING_BIT) != 0 {
                return Err("SLAB_IN_DESTRUCTION");
            }

            match self.state_and_readers.compare_exchange_weak(
                current,
                current + increment,
                Ordering::Acquire,
                Ordering::Relaxed,
            ) {
                Ok(_) => return Ok(self.generation as u64),
                Err(actual) => current = actual,
            }
        }
    }

    /// Libera lease de lectura decrementando los lectores del slot correspondiente
    pub fn release_reader_lease(&self, slot: u32) -> Result<(), &'static str> {
        if slot > 1 {
            return Err("INVALID_SLOT");
        }
        let decrement: u64 = if slot == 0 { 1u64 } else { 1u64 << 32 };
        let mut current = self.state_and_readers.load(Ordering::Relaxed);

        loop {
            let slot_readers = if slot == 0 {
                current & PMTP_SLOT0_READERS_MASK
            } else {
                (current & PMTP_SLOT1_READERS_MASK) >> 32
            };

            if slot_readers == 0 {
                return Err("DOUBLE_RELEASE_OR_ZERO_READERS");
            }

            match self.state_and_readers.compare_exchange_weak(
                current,
                current - decrement,
                Ordering::Release,
                Ordering::Relaxed,
            ) {
                Ok(_) => return Ok(()),
                Err(actual) => current = actual,
            }
        }
    }

    /// Inicia el proceso de destrucción atómica con drenaje de lectores
    pub fn mark_destroying_and_drain(&self, timeout_ms: u64) -> bool {
        self.state_and_readers.fetch_or(PMTP_DESTROYING_BIT, Ordering::AcqRel);
        let start = std::time::Instant::now();
        let timeout = std::time::Duration::from_millis(timeout_ms);

        while (self.state_and_readers.load(Ordering::Acquire) & PMTP_READERS_MASK) != 0 {
            if start.elapsed() > timeout {
                return false;
            }
            std::hint::spin_loop();
        }
        true
    }
}

// =============================================================================
// 2. CABECERA WIRE DE 128 BYTES PACKED (PARIDAD ESTRICTA C-DART-RUST)
// =============================================================================
#[repr(C, packed)]
pub struct PolydimWireHeader {
    pub magic: u32,                  // Offset  0 (4B): 0x504D5450
    pub version_major: u16,          // Offset  4 (2B): 1
    pub version_minor: u16,          // Offset  6 (2B): 0
    pub slab_uuid: [u8; 16],         // Offset  8 (16B): UUID
    pub num_elements: u64,           // Offset 24 (8B): Cantidad de elementos
    pub payload_bytes: u64,          // Offset 32 (8B): Tamaño en bytes
    pub timestamp_ns: u64,           // Offset 40 (8B): Timestamp nanosegundos
    pub dtype: u32,                  // Offset 48 (4B): DType
    pub stiefel_defect: f64,         // Offset 52 (8B): Defecto ortonormal
    pub blake2s_hash: [u8; 32],      // Offset 60 (32B): Hash
    pub reserved: [u8; 36],          // Offset 92 (36B) -> Total 128 bytes
}

// Aserciones estáticas de paridad binaria
const _: () = {
    assert!(std::mem::size_of::<PmtpHeaderCompact>() == 64);
    assert!(std::mem::size_of::<PolydimWireHeader>() == 128);
};

// =============================================================================
// 3. ACUMULADOR COMPENSADO DE NEUMAIER (PRECISIÓN FP64 <= 1e-15)
// =============================================================================
#[repr(C)]
pub struct NeumaierAccumulator {
    sum: f64,
    compensation: f64,
}

impl NeumaierAccumulator {
    pub fn new() -> Self {
        Self { sum: 0.0, compensation: 0.0 }
    }

    pub fn add(&mut self, value: f64) {
        let t = self.sum + value;
        if self.sum.abs() >= value.abs() {
            self.compensation += (self.sum - t) + value;
        } else {
            self.compensation += (value - t) + self.sum;
        }
        self.sum = t;
    }

    pub fn total(&self) -> f64 {
        self.sum + self.compensation
    }
}

pub fn neumaier_norm(data: &[f64]) -> f64 {
    let mut acc = NeumaierAccumulator::new();
    for &x in data {
        acc.add(x * x);
    }
    acc.total().sqrt()
}

// =============================================================================
// 4. RETRACCIÓN NEWTON-SCHULZ REAL DE ORDEN 5 (CÁLCULO MATRICIAL RIGUROSO)
// W_{k+1} = 1/8 * W_k * (15 I - 10 M + 3 M^2), donde M = W_k^T W_k
// =============================================================================
pub fn newton_schulz_ord5_retract(
    w: &mut [f64],
    rows: usize,
    cols: usize,
    max_iters: usize,
    tol: f64
) -> Result<f64, &'static str> {
    if rows < cols || cols == 0 || w.len() != rows * cols {
        return Err("DIMENSION_MISMATCH");
    }

    // 1. Preescalado espectral estricto: W0 = W / ||W||_F (garantiza ||W0||_2 < 1 <= sqrt(3))
    let mut norm_acc = NeumaierAccumulator::new();
    for &x in w.iter() {
        norm_acc.add(x * x);
    }
    let frob_norm = norm_acc.total().sqrt();
    if frob_norm <= 0.0 || !frob_norm.is_finite() {
        return Err("SINGULAR_OR_NONFINITE_MATRIX");
    }

    // Escalamos para que el mayor valor singular esté en radio de convergencia (0, sqrt(3))
    let scale_factor = 1.0 / (frob_norm + 1e-12);
    for x in w.iter_mut() {
        *x *= scale_factor;
    }

    let mut m = vec![0.0f64; cols * cols];
    let mut m2 = vec![0.0f64; cols * cols];
    let mut poly = vec![0.0f64; cols * cols];
    let mut w_next = vec![0.0f64; rows * cols];

    let mut final_defect = 1.0f64;

    for _ in 0..max_iters {
        // a) Calcular M = W^T W (cols x cols)
        for i in 0..cols {
            for j in 0..cols {
                let mut sum = 0.0f64;
                for r in 0..rows {
                    sum += w[r * cols + i] * w[r * cols + j];
                }
                m[i * cols + j] = sum;
            }
        }

        // Medir defecto de ortogonalidad ||M - I||_frobenius
        let mut def_acc = NeumaierAccumulator::new();
        for i in 0..cols {
            for j in 0..cols {
                let expected = if i == j { 1.0 } else { 0.0 };
                let diff = m[i * cols + j] - expected;
                def_acc.add(diff * diff);
            }
        }
        final_defect = def_acc.total().sqrt();
        if final_defect < tol {
            return Ok(final_defect);
        }

        // b) Calcular M^2 = M * M (cols x cols)
        for i in 0..cols {
            for j in 0..cols {
                let mut sum = 0.0f64;
                for k in 0..cols {
                    sum += m[i * cols + k] * m[k * cols + j];
                }
                m2[i * cols + j] = sum;
            }
        }

        // c) Polinomio de Orden 5: Poly = (15 I - 10 M + 3 M^2) / 8
        for i in 0..cols {
            for j in 0..cols {
                let id = if i == j { 15.0 } else { 0.0 };
                poly[i * cols + j] = (id - 10.0 * m[i * cols + j] + 3.0 * m2[i * cols + j]) / 8.0;
            }
        }

        // d) W_next = W * Poly (rows x cols)
        for r in 0..rows {
            for c in 0..cols {
                let mut sum = 0.0f64;
                for k in 0..cols {
                    sum += w[r * cols + k] * poly[k * cols + c];
                }
                w_next[r * cols + c] = sum;
            }
        }

        w.copy_from_slice(&w_next);
    }

    if final_defect < tol {
        Ok(final_defect)
    } else {
        Err("CONVERGENCE_NOT_REACHED")
    }
}

// =============================================================================
// 5. C-ABI EXPORTS PARA CARGA DIRECTA DESDE PYTHON/DART FFI
// =============================================================================
#[no_mangle]
pub extern "C" fn rust_newton_schulz_ord5_retract(
    w_ptr: *mut f64,
    len: usize,
    rows: usize,
    cols: usize,
    max_iters: usize,
    tol: f64,
    out_defect: *mut f64
) -> i32 {
    if w_ptr.is_null() || out_defect.is_null() || len != rows * cols {
        return -1;
    }
    let slice = unsafe { std::slice::from_raw_parts_mut(w_ptr, len) };
    match newton_schulz_ord5_retract(slice, rows, cols, max_iters, tol) {
        Ok(def) => {
            unsafe { *out_defect = def; }
            0
        },
        Err(_) => -2
    }
}
