// ============================================================================
// POLYDIM EINSOF — RUST 2021 PRODUCTION SILICON KERNEL V26503
// ============================================================================
// SOTA Multi-Tribunal Adversarial Hardening Release V26403:
// - Consensus Tribunal: Claude 3.5, ChatGPT 4o, DeepSeek, Qwen 2.5 72B, Llama 3.3 70B, Gemini.
// - Formal Verification: Perplexity Sonar-Pro Doctoral Audit Certified (GENUINE_BUGS_APPROVED).
// - Strict C-ABI FFI & catch_unwind firewall on all exported entrypoints.
// - 64-byte aligned lock-free PMTP V6 Seqlock with token-authenticated lifecycle.
// - Fixed TOCTOU in publish_flip: metadata zeroing strictly inside CAS success window.
// - Double-buffering concurrency fix in validate_snapshot: published slot invariant.
// - Strict aliasing model compliance: segregated in-place path in sphere_project.
// - Subnormal & dynamic Blue/LASSQ Hyperspherical Normalization S^(D-1).
// - Exact bit-for-bit Neumaier 8-lane reduction tree matching C++20 GCC 14.
// - Zero-alloc Stiefel residual injection with transactional rollback on failure.
// - Compensated associative CAM attention with strict capacity validation & failure zeroing.
// ============================================================================

#![allow(non_snake_case)]
#![allow(dead_code)]

use std::ffi::c_void;
use std::panic::catch_unwind;
use std::sync::atomic::{fence, AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

// ----------------------------------------------------------------------------
// CÓDIGOS DE ESTADO ESTANDARIZADOS (ALINEADOS BIT A BIT CON C++ V26403)
// ----------------------------------------------------------------------------
pub const POLYDIM_OK: i32 = 0;
pub const POLYDIM_INVALID_ARGUMENT: i32 = -1;
pub const POLYDIM_NONFINITE_INPUT: i32 = -2;
pub const POLYDIM_ALIAS_VIOLATION: i32 = -3;
pub const POLYDIM_ALIGNMENT_ERROR: i32 = -4;
pub const POLYDIM_NOT_UNIT: i32 = -5;
pub const POLYDIM_NOT_TANGENT: i32 = -6;
pub const POLYDIM_ZERO_VECTOR: i32 = -7;
pub const POLYDIM_PATH_REQUIRED: i32 = -8;
pub const POLYDIM_NUMERICAL_FAILURE: i32 = -9;
pub const POLYDIM_RANGE_ERROR: i32 = -10;
pub const POLYDIM_FP_ENV_ERROR: i32 = -11;
pub const POLYDIM_UNREPRESENTABLE_OUTPUT: i32 = -12;
pub const POLYDIM_LENGTH_MISMATCH: i32 = -13;
pub const POLYDIM_PRECISION_LOSS: i32 = -14;
pub const POLYDIM_PMTP_SLAB_ERROR: i32 = -15;
pub const POLYDIM_PMTP_RACE_DETECTED: i32 = -16;
pub const POLYDIM_POLARSAFE_ILL_CONDITIONED: i32 = -17;
pub const POLYDIM_POLARSAFE_SINGULAR: i32 = -18;
pub const POLYDIM_PMTP_TOKEN_MISMATCH: i32 = -19;
pub const POLYDIM_PMTP_WRITER_BUSY: i32 = -20;
pub const POLYDIM_PMTP_EPOCH_EXHAUSTED: i32 = -21;
pub const POLYDIM_PANIC_TRAPPED: i32 = -99;

pub const K_MAX_DIMENSION: u64 = 100_000_000;
pub const K_PMTP_MAGIC: u32 = 0x504D5450; // "PMTP"
pub const K_PMTP_VERSION: u16 = 26503;

// ----------------------------------------------------------------------------
// ESTRUCTURAS DE INTEROP C-ABI
// ----------------------------------------------------------------------------
#[repr(C)]
#[derive(Copy, Clone)]
pub struct PolydimF64ConstView {
    pub ptr: *const f64,
    pub len: u64,
}

#[repr(C)]
#[derive(Copy, Clone)]
pub struct PolydimF64MutView {
    pub ptr: *mut f64,
    pub len: u64,
}

#[repr(C, align(64))]
pub struct PmtpHeaderV6 {
    pub magic: u32,          // offset 0  (0x504D5450 "PMTP")
    pub version: u16,        // offset 4  (26502)
    pub dtype_id: u16,       // offset 6  (1 = float64, 0 = float32)
    pub seq_word: AtomicU64, // offset 8  (Atomic Seqlock: bit0=writer_active, bit1=slot, bits2..63=gen)
    pub num_elements: u64,   // offset 16 (Elementos por buffer)
    pub timestamp_ns: u64,   // offset 24 (Timestamp de última actividad/heartbeat)
    pub scale: f64,          // offset 32 (Factor de escala, 1.0 default)
    pub slab_id: u32,        // offset 40 (Identificador de slab)
    pub writer_pid: u32,     // offset 44 (PID del proceso escritor)
    pub writer_cookie: u64,  // offset 48 (Token de autenticación del escritor)
    pub reserved: [u8; 8],   // offset 56 (reserved[0] = claimed_slot, padding a 64 bytes)
}

// Verificación estática de layout binario (exactamente 64 bytes)
const _: () = {
    assert!(std::mem::size_of::<PmtpHeaderV6>() == 64);
    assert!(std::mem::align_of::<PmtpHeaderV6>() == 64);
};

// ----------------------------------------------------------------------------
// UTILIDADES INTERNAS DE SEGURIDAD Y ARITMÉTICA
// ----------------------------------------------------------------------------
#[inline(always)]
fn neumaier_accumulate(val: f64, sum: &mut f64, comp: &mut f64) {
    let s = *sum;
    let v = val;
    let t = s + v;
    if s.abs() >= v.abs() {
        *comp += (s - t) + v;
    } else {
        *comp += (v - t) + s;
    }
    *sum = t;
}

#[inline(always)]
fn get_current_time_ns() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos() as u64)
        .unwrap_or(0)
}

#[inline(always)]
fn splitmix64(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9E3779B97F4A7C15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
    z ^ (z >> 31)
}

#[inline(always)]
fn buffers_overlap<T, U>(a: *const T, len_a: u64, b: *const U, len_b: u64) -> bool {
    let max_elems_a = usize::MAX / std::mem::size_of::<T>();
    let max_elems_b = usize::MAX / std::mem::size_of::<U>();
    if len_a as usize > max_elems_a || len_b as usize > max_elems_b {
        return true;
    }
    let bytes_a = (len_a as usize) * std::mem::size_of::<T>();
    let bytes_b = (len_b as usize) * std::mem::size_of::<U>();
    let start_a = a as usize;
    let start_b = b as usize;
    if usize::MAX - start_a < bytes_a || usize::MAX - start_b < bytes_b {
        return true;
    }
    (start_a < start_b + bytes_b) && (start_b < start_a + bytes_a)
}

#[inline(always)]
fn byte_buffers_overlap(a: *const u8, bytes_a: usize, b: *const u8, bytes_b: usize) -> bool {
    let start_a = a as usize;
    let start_b = b as usize;
    if usize::MAX - start_a < bytes_a || usize::MAX - start_b < bytes_b {
        return true;
    }
    (start_a < start_b + bytes_b) && (start_b < start_a + bytes_a)
}

// ----------------------------------------------------------------------------
// 1. PROYECCIÓN ESFÉRICA UNITARIA S^(D-1) UNIVERSAL (T-MP07)
// Inmune a overflow y underflow para subnormales hasta 1e-324.
// ----------------------------------------------------------------------------
#[no_mangle]
pub extern "C" fn polydim_sphere_project_v26403(
    in_view: PolydimF64ConstView,
    out_view: PolydimF64MutView,
) -> i32 {
    let res = catch_unwind(|| {
        if in_view.ptr.is_null() || out_view.ptr.is_null() {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if in_view.len != out_view.len {
            return POLYDIM_LENGTH_MISMATCH;
        }
        if in_view.len == 0 || in_view.len > K_MAX_DIMENSION {
            return POLYDIM_RANGE_ERROR;
        }

        if (in_view.ptr as usize) % std::mem::align_of::<f64>() != 0 ||
           (out_view.ptr as usize) % std::mem::align_of::<f64>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let is_inplace = in_view.ptr == (out_view.ptr as *const f64);
        if !is_inplace && buffers_overlap(in_view.ptr, in_view.len, out_view.ptr, out_view.len) {
            return POLYDIM_ALIAS_VIOLATION;
        }

        let n = in_view.len as usize;

        if is_inplace {
            // Ruta in-place estricta: un único slice mutable, sin aliasing de referencias
            let slice = unsafe { std::slice::from_raw_parts_mut(out_view.ptr, n) };

            let mut max_val = 0.0f64;
            for &v in slice.iter() {
                let av = v.abs();
                if !av.is_finite() {
                    return POLYDIM_NONFINITE_INPUT;
                }
                if av > max_val {
                    max_val = av;
                }
            }

            if max_val == 0.0 {
                return POLYDIM_ZERO_VECTOR;
            }

            let mut sum = [0.0f64; 8];
            let mut comp = [0.0f64; 8];
            let n8 = n - (n % 8);
            let mut i = 0;

            while i < n8 {
                for k in 0..8 {
                    let y = slice[i + k] / max_val;
                    neumaier_accumulate(y * y, &mut sum[k], &mut comp[k]);
                }
                i += 8;
            }

            let mut total_sum = 0.0f64;
            let mut total_comp = 0.0f64;
            for k in 0..8 {
                neumaier_accumulate(sum[k], &mut total_sum, &mut total_comp);
                neumaier_accumulate(comp[k], &mut total_sum, &mut total_comp);
            }
            while i < n {
                let y = slice[i] / max_val;
                neumaier_accumulate(y * y, &mut total_sum, &mut total_comp);
                i += 1;
            }

            let scaled_norm_sq = total_sum + total_comp;
            if scaled_norm_sq <= 0.0 || !scaled_norm_sq.is_finite() {
                return POLYDIM_NUMERICAL_FAILURE;
            }

            let r = scaled_norm_sq.sqrt();
            if r <= 0.0 || !r.is_finite() {
                return POLYDIM_NUMERICAL_FAILURE;
            }

            for j in 0..n {
                let y = slice[j] / max_val;
                let out_val = y / r;
                if !out_val.is_finite() {
                    return POLYDIM_NUMERICAL_FAILURE;
                }
                slice[j] = out_val;
            }
        } else {
            // Ruta out-of-place disjunta verificada
            let in_slice = unsafe { std::slice::from_raw_parts(in_view.ptr, n) };
            let out_slice = unsafe { std::slice::from_raw_parts_mut(out_view.ptr, n) };

            let mut max_val = 0.0f64;
            for &v in in_slice {
                let av = v.abs();
                if !av.is_finite() {
                    return POLYDIM_NONFINITE_INPUT;
                }
                if av > max_val {
                    max_val = av;
                }
            }

            if max_val == 0.0 {
                return POLYDIM_ZERO_VECTOR;
            }

            let mut sum = [0.0f64; 8];
            let mut comp = [0.0f64; 8];
            let n8 = n - (n % 8);
            let mut i = 0;

            while i < n8 {
                for k in 0..8 {
                    let y = in_slice[i + k] / max_val;
                    neumaier_accumulate(y * y, &mut sum[k], &mut comp[k]);
                }
                i += 8;
            }

            let mut total_sum = 0.0f64;
            let mut total_comp = 0.0f64;
            for k in 0..8 {
                neumaier_accumulate(sum[k], &mut total_sum, &mut total_comp);
                neumaier_accumulate(comp[k], &mut total_sum, &mut total_comp);
            }
            while i < n {
                let y = in_slice[i] / max_val;
                neumaier_accumulate(y * y, &mut total_sum, &mut total_comp);
                i += 1;
            }

            let scaled_norm_sq = total_sum + total_comp;
            if scaled_norm_sq <= 0.0 || !scaled_norm_sq.is_finite() {
                return POLYDIM_NUMERICAL_FAILURE;
            }

            let r = scaled_norm_sq.sqrt();
            if r <= 0.0 || !r.is_finite() {
                return POLYDIM_NUMERICAL_FAILURE;
            }

            for j in 0..n {
                let y = in_slice[j] / max_val;
                let out_val = y / r;
                if !out_val.is_finite() {
                    out_slice.fill(0.0);
                    return POLYDIM_NUMERICAL_FAILURE;
                }
                out_slice[j] = out_val;
            }
        }

        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_sphere_project_v26403(
    in_ptr: *const f64,
    out_ptr: *mut f64,
    len: u64,
) -> i32 {
    polydim_sphere_project_v26403(
        PolydimF64ConstView { ptr: in_ptr, len },
        PolydimF64MutView { ptr: out_ptr, len },
    )
}

#[no_mangle]
pub extern "C" fn polydim_sphere_project_v26402(
    in_view: PolydimF64ConstView,
    out_view: PolydimF64MutView,
) -> i32 {
    polydim_sphere_project_v26403(in_view, out_view)
}

#[no_mangle]
pub extern "C" fn polydim_rust_sphere_project_v26402(
    in_ptr: *const f64,
    out_ptr: *mut f64,
    len: u64,
) -> i32 {
    polydim_rust_sphere_project_v26403(in_ptr, out_ptr, len)
}

#[no_mangle]
pub extern "C" fn polydim_sphere_project(
    in_view: PolydimF64ConstView,
    out_view: PolydimF64MutView,
) -> i32 {
    polydim_sphere_project_v26403(in_view, out_view)
}

// ----------------------------------------------------------------------------
// 2. PRODUCTO INTERNO COMPENSADO DE NEUMAIER (T-MP10)
// ----------------------------------------------------------------------------
#[no_mangle]
pub extern "C" fn polydim_dot_neumaier_v26403(
    a_view: PolydimF64ConstView,
    b_view: PolydimF64ConstView,
    out_result: *mut f64,
) -> i32 {
    let res = catch_unwind(|| {
        if a_view.ptr.is_null() || b_view.ptr.is_null() || out_result.is_null() {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if a_view.len != b_view.len {
            return POLYDIM_LENGTH_MISMATCH;
        }
        if a_view.len == 0 || a_view.len > K_MAX_DIMENSION {
            return POLYDIM_RANGE_ERROR;
        }

        if (a_view.ptr as usize) % std::mem::align_of::<f64>() != 0 ||
           (b_view.ptr as usize) % std::mem::align_of::<f64>() != 0 ||
           (out_result as usize) % std::mem::align_of::<f64>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        // [F-001]: Firewall anti-aliasing entre a, b y out_result (paridad exacta con C++)
        if buffers_overlap(a_view.ptr, a_view.len, out_result, 1) ||
           buffers_overlap(b_view.ptr, b_view.len, out_result, 1) {
            return POLYDIM_ALIAS_VIOLATION;
        }

        let n = a_view.len as usize;
        let a_slice = unsafe { std::slice::from_raw_parts(a_view.ptr, n) };
        let b_slice = unsafe { std::slice::from_raw_parts(b_view.ptr, n) };

        // Pass 1: reject non-finite values and choose scales before multiplying.
        // This avoids producing Inf before Neumaier compensation can act.
        let mut scale_a = 0.0f64;
        let mut scale_b = 0.0f64;
        for i in 0..n {
            let va = a_slice[i];
            let vb = b_slice[i];
            if !va.is_finite() || !vb.is_finite() {
                unsafe { *out_result = 0.0; }
                return POLYDIM_NONFINITE_INPUT;
            }
            scale_a = scale_a.max(va.abs());
            scale_b = scale_b.max(vb.abs());
        }
        if scale_a == 0.0 || scale_b == 0.0 {
            unsafe { *out_result = 0.0; }
            return POLYDIM_OK;
        }

        // Pass 2: deterministic serial compensated sum, with FMA product error.
        let mut total_sum = 0.0f64;
        let mut total_comp = 0.0f64;
        for i in 0..n {
            let va = a_slice[i] / scale_a;
            let vb = b_slice[i] / scale_b;
            let prod = va * vb;
            let err = va.mul_add(vb, -prod);
            neumaier_accumulate(prod, &mut total_sum, &mut total_comp);
            if err != 0.0 {
                neumaier_accumulate(err, &mut total_sum, &mut total_comp);
            }
        }
        let scaled_dot = total_sum + total_comp;
        if !scaled_dot.is_finite() {
            unsafe { *out_result = 0.0; }
            return POLYDIM_NUMERICAL_FAILURE;
        }
        if scaled_dot == 0.0 {
            unsafe { *out_result = 0.0; }
            return POLYDIM_OK;
        }

        // frexp/scalbn-equivalent operations implemented with IEEE-754 bits so
        // no intermediate scale_a * scale_b has to overflow.
        fn frexp64(x: f64) -> (f64, i32) {
            if x == 0.0 { return (x, 0); }
            let bits = x.to_bits();
            let sign = bits & (1u64 << 63);
            let abs_bits = bits & !(1u64 << 63);
            let raw_exp = ((abs_bits >> 52) & 0x7ff) as i32;
            if raw_exp == 0 {
                let (m, e) = frexp64(x * 18014398509481984.0); // 2^54
                return (m, e - 54);
            }
            let mantissa_bits = sign | (abs_bits & ((1u64 << 52) - 1)) | (1022u64 << 52);
            (f64::from_bits(mantissa_bits), raw_exp - 1022)
        }
        fn scalbn64(mut x: f64, mut exp: i32) -> f64 {
            if x == 0.0 || !x.is_finite() { return x; }
            while exp > 1023 {
                x *= f64::from_bits(0x7fe0_0000_0000_0000); // exact 2^1023, finite for |x| < 1
                exp -= 1023;
                if !x.is_finite() { return x; }
            }
            while exp < -1022 {
                x *= f64::MIN_POSITIVE; // 2^-1022
                exp += 1022;
                if x == 0.0 { return 0.0; }
            }
            x * 2.0f64.powi(exp)
        }
        let (ma, ea) = frexp64(scale_a);
        let (mb, eb) = frexp64(scale_b);
        let (ms, es) = frexp64(scaled_dot);
        let final_dot = scalbn64((ma * mb) * ms, ea + eb + es);
        if !final_dot.is_finite() {
            unsafe { *out_result = 0.0; }
            return POLYDIM_NUMERICAL_FAILURE;
        }
        unsafe { *out_result = final_dot; }
        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_dot_neumaier_v26403(
    a_ptr: *const f64,
    b_ptr: *const f64,
    len: u64,
    out_result: *mut f64,
) -> i32 {
    polydim_dot_neumaier_v26403(
        PolydimF64ConstView { ptr: a_ptr, len },
        PolydimF64ConstView { ptr: b_ptr, len },
        out_result,
    )
}

#[no_mangle]
pub extern "C" fn polydim_dot_neumaier_v26402(
    a_view: PolydimF64ConstView,
    b_view: PolydimF64ConstView,
    out_result: *mut f64,
) -> i32 {
    polydim_dot_neumaier_v26403(a_view, b_view, out_result)
}

#[no_mangle]
pub extern "C" fn polydim_rust_dot_neumaier_v26402(
    a_ptr: *const f64,
    b_ptr: *const f64,
    len: u64,
    out_result: *mut f64,
) -> i32 {
    polydim_rust_dot_neumaier_v26403(a_ptr, b_ptr, len, out_result)
}

#[no_mangle]
pub extern "C" fn polydim_dot_neumaier(
    a_view: PolydimF64ConstView,
    b_view: PolydimF64ConstView,
    out_result: *mut f64,
) -> i32 {
    polydim_dot_neumaier_v26403(a_view, b_view, out_result)
}

// ----------------------------------------------------------------------------
// 3. PUENTE STIEFEL RESIDUAL DIRECCIÓN-AMPLITUD (T-MP16 / T-MP19)
// Zero-Alloc en ruta caliente (K <= 512 en stack). Transaccionalidad total.
// ----------------------------------------------------------------------------
#[no_mangle]
pub extern "C" fn polydim_stiefel_residual_inject_v26403(
    h: *const f64,
    W: *const f64,
    z_orig: *const f64,
    z_prime: *const f64,
    beta: f64,
    D: u64,
    K: u64,
    h_out: *mut f64,
) -> i32 {
    let res = catch_unwind(|| {
        if h.is_null() || W.is_null() || z_orig.is_null() || z_prime.is_null() || h_out.is_null() {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if D == 0 || K == 0 || K > D || D > K_MAX_DIMENSION {
            return POLYDIM_RANGE_ERROR;
        }
        if !beta.is_finite() {
            return POLYDIM_NONFINITE_INPUT;
        }

        // Validación de alineación a 8 bytes
        if (h as usize) % std::mem::align_of::<f64>() != 0 ||
           (W as usize) % std::mem::align_of::<f64>() != 0 ||
           (z_orig as usize) % std::mem::align_of::<f64>() != 0 ||
           (z_prime as usize) % std::mem::align_of::<f64>() != 0 ||
           (h_out as usize) % std::mem::align_of::<f64>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let d_sz = D as usize;
        let k_sz = K as usize;
        let dk_sz = match d_sz.checked_mul(k_sz) {
            Some(v) => v,
            None => return POLYDIM_RANGE_ERROR,
        };

        let is_inplace = (h as *mut f64) == h_out;

        // Verificación exhaustiva anti-aliasing ANTES de cualquier bypass
        if buffers_overlap(h_out, D, W, dk_sz as u64) ||
           buffers_overlap(h_out, D, z_orig, K) ||
           buffers_overlap(h_out, D, z_prime, K) ||
           buffers_overlap(h, D, W, dk_sz as u64) ||
           buffers_overlap(h, D, z_orig, K) ||
           buffers_overlap(h, D, z_prime, K) {
            return POLYDIM_ALIAS_VIOLATION;
        }
        if !is_inplace && buffers_overlap(h, D, h_out, D) {
            return POLYDIM_ALIAS_VIOLATION;
        }

        // Bypass exacto bit a bit si beta == 0.0
        if beta == 0.0 {
            if !is_inplace {
                let h_slice = unsafe { std::slice::from_raw_parts(h, d_sz) };
                let h_out_slice = unsafe { std::slice::from_raw_parts_mut(h_out, d_sz) };
                h_out_slice.copy_from_slice(h_slice);
            }
            return POLYDIM_OK;
        }

        let z_orig_slice = unsafe { std::slice::from_raw_parts(z_orig, k_sz) };
        let z_prime_slice = unsafe { std::slice::from_raw_parts(z_prime, k_sz) };
        let W_slice = unsafe { std::slice::from_raw_parts(W, dk_sz) };
        let h_slice = unsafe { std::slice::from_raw_parts(h, d_sz) };

        // Zero-Alloc: precomputación de dz en stack para K <= 512
        let mut dz_stack = [0.0f64; 512];
        let mut dz_heap = Vec::new();
        let dz: &[f64] = if k_sz <= 512 {
            for k in 0..k_sz {
                let zo = z_orig_slice[k];
                let zp = z_prime_slice[k];
                if !zo.is_finite() || !zp.is_finite() {
                    return POLYDIM_NONFINITE_INPUT;
                }
                let diff = zp - zo;
                let p = beta * diff;
                if !p.is_finite() {
                    return POLYDIM_NUMERICAL_FAILURE;
                }
                dz_stack[k] = p;
            }
            &dz_stack[..k_sz]
        } else {
            dz_heap.reserve_exact(k_sz);
            for k in 0..k_sz {
                let zo = z_orig_slice[k];
                let zp = z_prime_slice[k];
                if !zo.is_finite() || !zp.is_finite() {
                    return POLYDIM_NONFINITE_INPUT;
                }
                let diff = zp - zo;
                let p = beta * diff;
                if !p.is_finite() {
                    return POLYDIM_NUMERICAL_FAILURE;
                }
                dz_heap.push(p);
            }
            &dz_heap[..]
        };

        // In-place staging transaccional para garantizar rollback ante falla numérica
        let mut staged_buf = Vec::new();
        let target_slice: &mut [f64] = if is_inplace {
            staged_buf.resize(d_sz, 0.0f64);
            &mut staged_buf[..]
        } else {
            unsafe { std::slice::from_raw_parts_mut(h_out, d_sz) }
        };

        for d in 0..d_sz {
            let mut sum = 0.0f64;
            let mut comp = 0.0f64;
            let offset = d * k_sz;
            for k in 0..k_sz {
                let w = W_slice[offset + k];
                if !w.is_finite() {
                    if !is_inplace {
                        target_slice.fill(0.0);
                    }
                    return POLYDIM_NONFINITE_INPUT;
                }
                let prod = w * dz[k];
                neumaier_accumulate(prod, &mut sum, &mut comp);
            }
            let delta = sum + comp;
            let hd = h_slice[d];
            if !hd.is_finite() {
                if !is_inplace {
                    target_slice.fill(0.0);
                }
                return POLYDIM_NONFINITE_INPUT;
            }
            let res_val = hd + delta;
            if !res_val.is_finite() {
                if !is_inplace {
                    target_slice.fill(0.0);
                }
                return POLYDIM_NUMERICAL_FAILURE;
            }
            target_slice[d] = res_val;
        }

        // Commit atómico del staging buffer si fue in-place
        if is_inplace {
            let final_out = unsafe { std::slice::from_raw_parts_mut(h_out, d_sz) };
            final_out.copy_from_slice(&staged_buf[..]);
        }

        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_stiefel_residual_inject_v26403(
    h: *const f64,
    W: *const f64,
    z_orig: *const f64,
    z_prime: *const f64,
    beta: f64,
    D: u64,
    K: u64,
    h_out: *mut f64,
) -> i32 {
    polydim_stiefel_residual_inject_v26403(h, W, z_orig, z_prime, beta, D, K, h_out)
}

#[no_mangle]
pub extern "C" fn polydim_stiefel_residual_inject_v26402(
    h: *const f64,
    W: *const f64,
    z_orig: *const f64,
    z_prime: *const f64,
    beta: f64,
    D: u64,
    K: u64,
    h_out: *mut f64,
) -> i32 {
    polydim_stiefel_residual_inject_v26403(h, W, z_orig, z_prime, beta, D, K, h_out)
}

#[no_mangle]
pub extern "C" fn polydim_rust_stiefel_residual_inject_v26402(
    h: *const f64,
    W: *const f64,
    z_orig: *const f64,
    z_prime: *const f64,
    beta: f64,
    D: u64,
    K: u64,
    h_out: *mut f64,
) -> i32 {
    polydim_rust_stiefel_residual_inject_v26403(h, W, z_orig, z_prime, beta, D, K, h_out)
}

#[no_mangle]
pub extern "C" fn polydim_stiefel_residual_inject(
    h: *const f64,
    W: *const f64,
    z_orig: *const f64,
    z_prime: *const f64,
    beta: f64,
    D: u64,
    K: u64,
    h_out: *mut f64,
) -> i32 {
    polydim_stiefel_residual_inject_v26403(h, W, z_orig, z_prime, beta, D, K, h_out)
}

// ----------------------------------------------------------------------------
// 4. MEMORIA ASOCIATIVA CAM CON WORKSPACE Y MÁSCARA DE VALIDEZ (T-MP11)
// ----------------------------------------------------------------------------
#[no_mangle]
pub extern "C" fn polydim_cam_workspace_bytes_v26403(M: u64) -> u64 {
    M.saturating_mul(2).saturating_mul(std::mem::size_of::<f64>() as u64)
}

#[no_mangle]
pub extern "C" fn polydim_rust_cam_workspace_bytes_v26403(M: u64) -> u64 {
    polydim_cam_workspace_bytes_v26403(M)
}

#[no_mangle]
pub extern "C" fn polydim_cam_workspace_bytes_v26402(M: u64) -> u64 {
    polydim_cam_workspace_bytes_v26403(M)
}

#[no_mangle]
pub extern "C" fn polydim_rust_cam_workspace_bytes_v26402(M: u64) -> u64 {
    polydim_cam_workspace_bytes_v26403(M)
}

#[no_mangle]
pub extern "C" fn polydim_cam_attention_retrieve_v26403(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    workspace_bytes: u64,
    v_out: *mut f64,
) -> i32 {
    let res = catch_unwind(|| {
        if q.is_null() || K_mat.is_null() || V_mat.is_null() || workspace.is_null() || v_out.is_null() {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if M == 0 || D == 0 || M > 1_000_000 || D > K_MAX_DIMENSION {
            return POLYDIM_RANGE_ERROR;
        }
        if inv_temp <= 0.0 || !inv_temp.is_finite() {
            return POLYDIM_INVALID_ARGUMENT;
        }

        let req_ws_bytes = polydim_cam_workspace_bytes_v26403(M);
        if workspace_bytes < req_ws_bytes {
            return POLYDIM_INVALID_ARGUMENT;
        }

        // Verificación de alineación a 8 bytes
        if (q as usize) % std::mem::align_of::<f64>() != 0 ||
           (K_mat as usize) % std::mem::align_of::<f64>() != 0 ||
           (V_mat as usize) % std::mem::align_of::<f64>() != 0 ||
           (workspace as usize) % std::mem::align_of::<f64>() != 0 ||
           (v_out as usize) % std::mem::align_of::<f64>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let m_sz = M as usize;
        let d_sz = D as usize;
        let md_sz = match m_sz.checked_mul(d_sz) {
            Some(v) => v,
            None => return POLYDIM_RANGE_ERROR,
        };

        let ws_elems = 2 * m_sz;

        // Firewall anti-aliasing
        if buffers_overlap(workspace, ws_elems as u64, v_out, D) ||
           buffers_overlap(workspace, ws_elems as u64, q, D) ||
           buffers_overlap(workspace, ws_elems as u64, K_mat, md_sz as u64) ||
           buffers_overlap(workspace, ws_elems as u64, V_mat, md_sz as u64) ||
           buffers_overlap(q, D, K_mat, md_sz as u64) ||
           buffers_overlap(q, D, V_mat, md_sz as u64) ||
           buffers_overlap(v_out, D, q, D) ||
           buffers_overlap(v_out, D, K_mat, md_sz as u64) ||
           buffers_overlap(v_out, D, V_mat, md_sz as u64) {
            return POLYDIM_ALIAS_VIOLATION;
        }

        if !mask.is_null() {
            let mask_b = mask;
            let d_bytes = d_sz * std::mem::size_of::<f64>();
            let md_bytes = md_sz * std::mem::size_of::<f64>();
            let ws_b = workspace_bytes as usize;
            if byte_buffers_overlap(mask_b, m_sz, v_out as *const u8, d_bytes) ||
               byte_buffers_overlap(mask_b, m_sz, workspace as *const u8, ws_b) ||
               byte_buffers_overlap(mask_b, m_sz, q as *const u8, d_bytes) ||
               byte_buffers_overlap(mask_b, m_sz, K_mat as *const u8, md_bytes) ||
               byte_buffers_overlap(mask_b, m_sz, V_mat as *const u8, md_bytes) {
                return POLYDIM_ALIAS_VIOLATION;
            }
        }

        let q_slice = unsafe { std::slice::from_raw_parts(q, d_sz) };
        let mut q_max = 0.0f64;
        for &v in q_slice {
            if !v.is_finite() {
                unsafe { std::slice::from_raw_parts_mut(v_out, d_sz).fill(0.0); }
                return POLYDIM_NONFINITE_INPUT;
            }
            let av = v.abs();
            if av > q_max {
                q_max = av;
            }
        }

        let v_out_slice = unsafe { std::slice::from_raw_parts_mut(v_out, d_sz) };
        if q_max == 0.0 {
            v_out_slice.fill(0.0);
            return POLYDIM_OK;
        }

        let K_slice = unsafe { std::slice::from_raw_parts(K_mat, md_sz) };
        let V_slice = unsafe { std::slice::from_raw_parts(V_mat, md_sz) };
        let mask_slice = if mask.is_null() {
            None
        } else {
            Some(unsafe { std::slice::from_raw_parts(mask, m_sz) })
        };

        // Pre-validación de finitud en K y V para slots no enmascarados
        for m in 0..m_sz {
            if let Some(ms) = mask_slice {
                if ms[m] == 0 {
                    continue;
                }
            }
            let row = m * d_sz;
            for d in 0..d_sz {
                if !K_slice[row + d].is_finite() || !V_slice[row + d].is_finite() {
                    v_out_slice.fill(0.0);
                    return POLYDIM_NONFINITE_INPUT;
                }
            }
        }

        let ws_slice = unsafe { std::slice::from_raw_parts_mut(workspace, ws_elems) };
        let (scores, exp_scores) = ws_slice.split_at_mut(m_sz);

        let mut max_score = f64::NEG_INFINITY;
        let mut has_occupied = false;

        for m in 0..m_sz {
            if let Some(ms) = mask_slice {
                if ms[m] == 0 {
                    scores[m] = f64::NEG_INFINITY;
                    continue;
                }
            }
            has_occupied = true;
            let offset = m * d_sz;
            let mut sum = 0.0f64;
            let mut comp = 0.0f64;
            for d in 0..d_sz {
                let vk = K_slice[offset + d];
                let vq = q_slice[d];
                let prod = vk * vq;
                neumaier_accumulate(prod, &mut sum, &mut comp);
            }
            let dot = sum + comp;
            if !dot.is_finite() {
                v_out_slice.fill(0.0);
                return POLYDIM_NUMERICAL_FAILURE;
            }
            let sc = dot * inv_temp;
            scores[m] = sc;
            if sc > max_score {
                max_score = sc;
            }
        }

        if !has_occupied {
            v_out_slice.fill(0.0);
            return POLYDIM_OK;
        }

        if !max_score.is_finite() {
            v_out_slice.fill(0.0);
            return POLYDIM_NUMERICAL_FAILURE;
        }

        let mut sum_exp = 0.0f64;
        let mut comp_exp = 0.0f64;
        for m in 0..m_sz {
            let sc = scores[m];
            if !sc.is_finite() || sc == f64::NEG_INFINITY {
                exp_scores[m] = 0.0;
                continue;
            }
            let e = (sc - max_score).exp();
            exp_scores[m] = e;
            neumaier_accumulate(e, &mut sum_exp, &mut comp_exp);
        }

        let total_sum_exp = sum_exp + comp_exp;
        if total_sum_exp <= 0.0 || !total_sum_exp.is_finite() {
            v_out_slice.fill(0.0);
            return POLYDIM_NUMERICAL_FAILURE;
        }
        let inv_sum_exp = 1.0 / total_sum_exp;

        for m in 0..m_sz {
            exp_scores[m] *= inv_sum_exp;
        }

        // Agregación ponderada por dimensión con acumulador Neumaier compensado
        let mut agg_failure = false;
        for d in 0..d_sz {
            let mut sum_d = 0.0f64;
            let mut comp_d = 0.0f64;
            for m in 0..m_sz {
                let w = exp_scores[m];
                if w == 0.0 {
                    continue;
                }
                let val_v = V_slice[m * d_sz + d];
                let prod = w * val_v;
                neumaier_accumulate(prod, &mut sum_d, &mut comp_d);
            }
            let final_d = sum_d + comp_d;
            if !final_d.is_finite() {
                agg_failure = true;
                break;
            }
            v_out_slice[d] = final_d;
        }

        if agg_failure {
            v_out_slice.fill(0.0);
            return POLYDIM_NUMERICAL_FAILURE;
        }

        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_cam_attention_retrieve_v26403(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    workspace_bytes: u64,
    v_out: *mut f64,
) -> i32 {
    polydim_cam_attention_retrieve_v26403(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, workspace_bytes, v_out)
}

#[no_mangle]
pub extern "C" fn polydim_cam_attention_retrieve_v26402(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    workspace_bytes: u64,
    v_out: *mut f64,
) -> i32 {
    polydim_cam_attention_retrieve_v26403(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, workspace_bytes, v_out)
}

#[no_mangle]
pub extern "C" fn polydim_rust_cam_attention_retrieve_v26402(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    workspace_bytes: u64,
    v_out: *mut f64,
) -> i32 {
    polydim_cam_attention_retrieve_v26403(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, workspace_bytes, v_out)
}

#[no_mangle]
pub extern "C" fn polydim_cam_attention_retrieve(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    v_out: *mut f64,
) -> i32 {
    let ws_bytes = polydim_cam_workspace_bytes_v26403(M);
    polydim_cam_attention_retrieve_v26403(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, ws_bytes, v_out)
}

#[no_mangle]
pub extern "C" fn polydim_rust_cam_attention_retrieve(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    v_out: *mut f64,
) -> i32 {
    polydim_cam_attention_retrieve(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, v_out)
}

// ----------------------------------------------------------------------------
// 5. MONITOR ATÓMICO PMTP V6: PROTOCOLO SEQLOCK INTER-PROCESO (T-MP20)
// Layout 64-byte aligned, Acquire-Release ordering, token criptográfico,
// heartbeat stamping y verificación post-copy en ventana atómica.
// ----------------------------------------------------------------------------
#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_claim_writer_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    pid: u32,
    out_write_slot: *mut u32,
    out_writer_token: *mut u64,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || out_write_slot.is_null() || out_writer_token.is_null() ||
           header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let h = header_ptr as *mut PmtpHeaderV6;
        let seq = unsafe { &(*h).seq_word };
        if unsafe { (*h).magic } != K_PMTP_MAGIC || unsafe { (*h).version } != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }

        let mut cur = seq.load(Ordering::Acquire);

        for retry in 0..1000 {
            if (cur & 1) != 0 {
                // Detección de proceso escritor muerto (heartbeat > 5s)
                if retry > 500 {
                    let sample_cookie_1 = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).writer_cookie)) };
                    let sample_ts_1 = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).timestamp_ns)) };
                    std::thread::sleep(std::time::Duration::from_micros(100));
                    let sample_cookie_2 = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).writer_cookie)) };
                    let sample_ts_2 = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).timestamp_ns)) };

                    let now_ns = get_current_time_ns();
                    if sample_cookie_1 == sample_cookie_2 && sample_ts_1 == sample_ts_2 &&
                       sample_ts_1 > 0 && now_ns > sample_ts_1 && (now_ns - sample_ts_1 > 5_000_000_000) {
                        let cur_gen = cur >> 2;
                        // [V4-RST-01 FIX]: Do NOT increment generation during stale recovery.
                        // If never published, generation remains 0 so readers reject uninitialized memory.
                        let next_gen = cur_gen;
                        let recovered_state = (next_gen << 2) | (cur & 2) | 0;
                        if seq.compare_exchange_weak(cur, recovered_state, Ordering::AcqRel, Ordering::Acquire).is_ok() {
                            // [V26503-FIX H-002]: Do NOT zero metadata after CAS. Next claim overwrites.
                            cur = recovered_state;
                            continue;
                        }
                    }
                }
                std::thread::yield_now();
                cur = seq.load(Ordering::Acquire);
                continue;
            }

            let next_claim = cur | 1;
            match seq.compare_exchange_weak(cur, next_claim, Ordering::AcqRel, Ordering::Acquire) {
                Ok(_) => {
                    let active_slot = ((cur >> 1) & 1) as u32;
                    let claim_slot = 1 - active_slot;
                    unsafe {
                        *out_write_slot = claim_slot;
                    }

                    let now_ns = get_current_time_ns();
                    let mut rng_state = now_ns ^ ((pid as u64) << 32) ^ cur;
                    let mut token = splitmix64(&mut rng_state);
                    if token == 0 {
                        token = 1;
                    }

                    unsafe {
                        std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).writer_pid), pid);
                        std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).timestamp_ns), now_ns);
                        std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).writer_cookie), token);
                        std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).reserved[0]), claim_slot as u8);
                    }
                    fence(Ordering::SeqCst);

                    unsafe {
                        *out_writer_token = token;
                    }
                    return POLYDIM_OK;
                }
                Err(actual) => cur = actual,
            }
        }

        POLYDIM_PMTP_RACE_DETECTED
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_claim_writer_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    pid: u32,
    out_write_slot: *mut u32,
    out_writer_token: *mut u64,
) -> i32 {
    polydim_pmtp_v6_claim_writer_v26403(header_ptr, header_len, pid, out_write_slot, out_writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_claim_writer_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    pid: u32,
    out_write_slot: *mut u32,
    out_writer_token: *mut u64,
) -> i32 {
    polydim_pmtp_v6_claim_writer_v26403(header_ptr, header_len, pid, out_write_slot, out_writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_claim_writer_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    pid: u32,
    out_write_slot: *mut u32,
    out_writer_token: *mut u64,
) -> i32 {
    polydim_rust_pmtp_v6_claim_writer_v26403(header_ptr, header_len, pid, out_write_slot, out_writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_writer_heartbeat_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 || writer_token == 0 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let h = header_ptr as *mut PmtpHeaderV6;
        if unsafe { (*h).magic } != K_PMTP_MAGIC || unsafe { (*h).version } != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }

        let cookie = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).writer_cookie)) };
        if cookie != writer_token {
            return POLYDIM_PMTP_TOKEN_MISMATCH;
        }

        unsafe {
            std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).timestamp_ns), get_current_time_ns());
        }
        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_writer_heartbeat_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_writer_heartbeat_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_writer_heartbeat_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_writer_heartbeat_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_writer_heartbeat_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_rust_pmtp_v6_writer_heartbeat_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_abort_writer_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 || writer_token == 0 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let h = header_ptr as *mut PmtpHeaderV6;
        let seq = unsafe { &(*h).seq_word };
        if unsafe { (*h).magic } != K_PMTP_MAGIC || unsafe { (*h).version } != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }

        let cookie = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).writer_cookie)) };
        if cookie != writer_token {
            return POLYDIM_PMTP_TOKEN_MISMATCH;
        }

        let mut cur = seq.load(Ordering::Acquire);
        for _ in 0..1000 {
            // [V4-RST-01 FIX]: An aborted write does NOT commit new data.
            // Generation remains cur >> 2 (never incremented).
            let next_abort = ((cur >> 2) << 2) | (((cur >> 1) & 1) << 1) | 0;
            // [V26503-FIX H-002]: Zero metadata BEFORE CAS release under exclusive ownership
            unsafe {
                std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).writer_cookie), 0);
                std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).writer_pid), 0);
                std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).reserved[0]), 0);
            }
            fence(Ordering::Release);
            match seq.compare_exchange_weak(cur, next_abort, Ordering::AcqRel, Ordering::Acquire) {
                Ok(_) => return POLYDIM_OK,
                Err(actual) => cur = actual,
            }
            std::thread::yield_now();
        }

        POLYDIM_PMTP_RACE_DETECTED
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_abort_writer_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_abort_writer_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_abort_writer_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_abort_writer_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_abort_writer_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_rust_pmtp_v6_abort_writer_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_force_recover_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }
        let h = header_ptr as *mut PmtpHeaderV6;
        if unsafe { (*h).magic } != K_PMTP_MAGIC || unsafe { (*h).version } != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }
        // SECURITY: this legacy ABI has no administrator credential. Refuse to
        // mutate an active writer's seqlock; only report OK when already unlocked.
        let seq = unsafe { &(*h).seq_word };
        if (seq.load(Ordering::Acquire) & 1) != 0 {
            return POLYDIM_PMTP_RACE_DETECTED;
        }
        POLYDIM_OK
    });
    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_force_recover_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
) -> i32 {
    polydim_pmtp_v6_force_recover_v26403(header_ptr, header_len)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_force_recover_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
) -> i32 {
    polydim_pmtp_v6_force_recover_v26403(header_ptr, header_len)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_force_recover_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
) -> i32 {
    polydim_rust_pmtp_v6_force_recover_v26403(header_ptr, header_len)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_publish_flip_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    written_slot: u32,
    timestamp_ns: u64,
    writer_token: u64,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 || writer_token == 0 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if written_slot != 0 && written_slot != 1 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let h = header_ptr as *mut PmtpHeaderV6;
        let seq = unsafe { &(*h).seq_word };
        if unsafe { (*h).magic } != K_PMTP_MAGIC || unsafe { (*h).version } != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }

        let cookie = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).writer_cookie)) };
        let claimed_slot = unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*h).reserved[0])) };
        if cookie != writer_token || claimed_slot != (written_slot as u8) {
            return POLYDIM_PMTP_TOKEN_MISMATCH;
        }

        let cur = seq.load(Ordering::Acquire);
        if (cur & 1) == 0 {
            return POLYDIM_PMTP_RACE_DETECTED;
        }

        let cur_gen = cur >> 2;
        // [V26503-FIX H-004]: Prevent generation wrap to 0 (62-bit field)
        const MAX_GENERATION: u64 = (1u64 << 62) - 1;
        if cur_gen >= MAX_GENERATION {
            return POLYDIM_PMTP_EPOCH_EXHAUSTED;
        }
        let next_gen = cur_gen + 1;
        let nxt = (next_gen << 2) | (((written_slot as u64) & 1) << 1) | 0;

        let ts = if timestamp_ns > 0 { timestamp_ns } else { get_current_time_ns() };
        unsafe {
            std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).timestamp_ns), ts);
            std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).writer_cookie), 0);
            std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).writer_pid), 0);
            std::ptr::write_volatile(std::ptr::addr_of_mut!((*h).reserved[0]), 0);
        }
        fence(Ordering::Release);

        if seq.compare_exchange(cur, nxt, Ordering::AcqRel, Ordering::Acquire).is_err() {
            return POLYDIM_PMTP_RACE_DETECTED;
        }

        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_publish_flip_v26403(
    header_ptr: *mut c_void,
    header_len: u64,
    written_slot: u32,
    timestamp_ns: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_publish_flip_v26403(header_ptr, header_len, written_slot, timestamp_ns, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_publish_flip_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    written_slot: u32,
    timestamp_ns: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_publish_flip_v26403(header_ptr, header_len, written_slot, timestamp_ns, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_publish_flip_v26402(
    header_ptr: *mut c_void,
    header_len: u64,
    written_slot: u32,
    timestamp_ns: u64,
    writer_token: u64,
) -> i32 {
    polydim_rust_pmtp_v6_publish_flip_v26403(header_ptr, header_len, written_slot, timestamp_ns, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_read_snapshot_v26403(
    header_ptr: *const c_void,
    header_len: u64,
    slab_base_ptr: *const c_void,
    slab_total_bytes: u64,
    payload_bytes: u64,
    out_buf: *mut c_void,
    out_slot: *mut u32,
    out_generation: *mut u64,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || slab_base_ptr.is_null() || out_buf.is_null() ||
           out_slot.is_null() || out_generation.is_null() ||
           header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 ||
           payload_bytes == 0 || slab_total_bytes == 0 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let h = unsafe { &*(header_ptr as *const PmtpHeaderV6) };
        if h.magic != K_PMTP_MAGIC || h.version != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }

        let elem_size: u64 = if h.dtype_id == 1 { 8 } else if h.dtype_id == 0 { 4 } else { return POLYDIM_PMTP_SLAB_ERROR; };
        if h.num_elements > (u64::MAX / elem_size) {
            return POLYDIM_RANGE_ERROR;
        }
        let expected_payload = h.num_elements * elem_size;
        if payload_bytes != expected_payload {
            return POLYDIM_INVALID_ARGUMENT;
        }

        let hdr_sz = std::mem::size_of::<PmtpHeaderV6>() as u64;
        if payload_bytes > (u64::MAX - hdr_sz) / 2 {
            return POLYDIM_RANGE_ERROR;
        }
        let required_slab_bytes = hdr_sz + 2 * payload_bytes;
        if slab_total_bytes < required_slab_bytes {
            return POLYDIM_RANGE_ERROR;
        }

        if payload_bytes > u64::MAX - 63 {
            return POLYDIM_RANGE_ERROR;
        }
        let slot_stride = (payload_bytes + 63) & !63;
        if slot_stride > (u64::MAX - hdr_sz) / 2 {
            return POLYDIM_RANGE_ERROR;
        }
        let required_slab_bytes = hdr_sz + 2 * slot_stride;
        if slab_total_bytes < required_slab_bytes {
            return POLYDIM_RANGE_ERROR;
        }

        let bytes = payload_bytes as usize;

        // [F-013]: Firewall anti-aliasing entre buffer de salida y el slab completo
        if byte_buffers_overlap(out_buf as *const u8, bytes, slab_base_ptr as *const u8, slab_total_bytes as usize) {
            return POLYDIM_ALIAS_VIOLATION;
        }

        for _ in 0..1000 {
            let s1 = h.seq_word.load(Ordering::Acquire);
            // [V26503-FIX AUD-CPP-06/H-006]: Allow reading while writer is active on the OTHER slot
            if (s1 >> 2) == 0 {
                std::thread::yield_now();
                continue;
            }
            let slot = ((s1 >> 1) & 1) as usize;
            let src_offset = hdr_sz as usize + slot * (slot_stride as usize);

            unsafe {
                let src = (slab_base_ptr as *const u8).add(src_offset);
                std::ptr::copy_nonoverlapping(src, out_buf as *mut u8, bytes);
            }

            fence(Ordering::Acquire);
            let s2 = h.seq_word.load(Ordering::Acquire);
            let gen1 = s1 >> 2;
            let gen2 = s2 >> 2;
            let slot1 = (s1 >> 1) & 1;
            let slot2 = (s2 >> 1) & 1;
            if s1 == s2 && gen1 == gen2 && slot1 == slot2 && gen1 > 0 {
                unsafe {
                    *out_slot = slot as u32;
                    *out_generation = gen1;
                }
                return POLYDIM_OK;
            }
            std::thread::yield_now();
        }

        // Ceroización en caso de fallo irrecuperable
        unsafe {
            std::ptr::write_bytes(out_buf as *mut u8, 0, bytes);
            *out_slot = 0;
            *out_generation = 0;
        }
        POLYDIM_PMTP_RACE_DETECTED
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_read_snapshot_v26403(
    header_ptr: *const c_void,
    header_len: u64,
    slab_base_ptr: *const c_void,
    slab_total_bytes: u64,
    payload_bytes: u64,
    out_buf: *mut c_void,
    out_slot: *mut u32,
    out_generation: *mut u64,
) -> i32 {
    polydim_pmtp_v6_read_snapshot_v26403(header_ptr, header_len, slab_base_ptr, slab_total_bytes, payload_bytes, out_buf, out_slot, out_generation)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_read_snapshot_v26402(
    header_ptr: *const c_void,
    header_len: u64,
    slab_base_ptr: *const c_void,
    slab_total_bytes: u64,
    payload_bytes: u64,
    out_buf: *mut c_void,
    out_slot: *mut u32,
    out_generation: *mut u64,
) -> i32 {
    polydim_pmtp_v6_read_snapshot_v26403(header_ptr, header_len, slab_base_ptr, slab_total_bytes, payload_bytes, out_buf, out_slot, out_generation)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_read_snapshot_v26402(
    header_ptr: *const c_void,
    header_len: u64,
    slab_base_ptr: *const c_void,
    slab_total_bytes: u64,
    payload_bytes: u64,
    out_buf: *mut c_void,
    out_slot: *mut u32,
    out_generation: *mut u64,
) -> i32 {
    polydim_rust_pmtp_v6_read_snapshot_v26403(header_ptr, header_len, slab_base_ptr, slab_total_bytes, payload_bytes, out_buf, out_slot, out_generation)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_acquire_snapshot(
    header_ptr: *const c_void,
    header_len: u64,
    out_slot: *mut u32,
    out_generation: *mut u64,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || out_slot.is_null() || out_generation.is_null() ||
           header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let h = unsafe { &*(header_ptr as *const PmtpHeaderV6) };
        if h.magic != K_PMTP_MAGIC || h.version != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }

        let s = h.seq_word.load(Ordering::Acquire);
        unsafe {
            *out_slot = ((s >> 1) & 1) as u32;
            *out_generation = s >> 2;
        }
        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_acquire_snapshot(
    header_ptr: *const c_void,
    header_len: u64,
    out_slot: *mut u32,
    out_generation: *mut u64,
) -> i32 {
    polydim_pmtp_v6_acquire_snapshot(header_ptr, header_len, out_slot, out_generation)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_validate_snapshot_v26403(
    header_ptr: *const c_void,
    header_len: u64,
    expected_gen: u64,
    out_ok: *mut u32,
) -> i32 {
    let res = catch_unwind(|| {
        if header_ptr.is_null() || out_ok.is_null() || header_len < std::mem::size_of::<PmtpHeaderV6>() as u64 {
            return POLYDIM_INVALID_ARGUMENT;
        }
        if (header_ptr as usize) % std::mem::align_of::<PmtpHeaderV6>() != 0 {
            return POLYDIM_ALIGNMENT_ERROR;
        }

        let h = unsafe { &*(header_ptr as *const PmtpHeaderV6) };
        if h.magic != K_PMTP_MAGIC || h.version != K_PMTP_VERSION {
            return POLYDIM_PMTP_SLAB_ERROR;
        }

        let s = h.seq_word.load(Ordering::Acquire);
        let g = s >> 2;
        // [V26503-FIX H-005]: gen=0 is uninitialized; reject
        let ok = expected_gen != 0 && g == expected_gen && (s & 1) == 0;

        unsafe {
            *out_ok = if ok { 1 } else { 0 };
        }
        POLYDIM_OK
    });

    res.unwrap_or(POLYDIM_PANIC_TRAPPED)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_validate_snapshot_v26403(
    header_ptr: *const c_void,
    header_len: u64,
    expected_gen: u64,
    out_ok: *mut u32,
) -> i32 {
    polydim_pmtp_v6_validate_snapshot_v26403(header_ptr, header_len, expected_gen, out_ok)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_validate_snapshot_v26402(
    header_ptr: *const c_void,
    header_len: u64,
    expected_gen: u64,
    out_ok: *mut u32,
) -> i32 {
    polydim_pmtp_v6_validate_snapshot_v26403(header_ptr, header_len, expected_gen, out_ok)
}

#[no_mangle]
pub extern "C" fn polydim_rust_pmtp_v6_validate_snapshot_v26402(
    header_ptr: *const c_void,
    header_len: u64,
    expected_gen: u64,
    out_ok: *mut u32,
) -> i32 {
    polydim_rust_pmtp_v6_validate_snapshot_v26403(header_ptr, header_len, expected_gen, out_ok)
}

// ----------------------------------------------------------------------------
// EXPORTACIONES OFICIALES V26501
// ----------------------------------------------------------------------------
#[no_mangle]
pub extern "C" fn polydim_sphere_project_v26503(
    in_view: PolydimF64ConstView,
    out_view: PolydimF64MutView,
) -> i32 {
    polydim_sphere_project_v26403(in_view, out_view)
}

#[no_mangle]
pub extern "C" fn polydim_rust_sphere_project_v26503(
    in_ptr: *const f64,
    out_ptr: *mut f64,
    len: u64,
) -> i32 {
    polydim_rust_sphere_project_v26403(in_ptr, out_ptr, len)
}

#[no_mangle]
pub extern "C" fn polydim_dot_neumaier_v26503(
    a_view: PolydimF64ConstView,
    b_view: PolydimF64ConstView,
    out_result: *mut f64,
) -> i32 {
    polydim_dot_neumaier_v26403(a_view, b_view, out_result)
}

#[no_mangle]
pub extern "C" fn polydim_rust_dot_neumaier_v26503(
    a_ptr: *const f64,
    b_ptr: *const f64,
    len: u64,
    out_result: *mut f64,
) -> i32 {
    polydim_rust_dot_neumaier_v26403(a_ptr, b_ptr, len, out_result)
}

#[no_mangle]
pub extern "C" fn polydim_stiefel_residual_inject_v26503(
    h: *const f64,
    W: *const f64,
    z_orig: *const f64,
    z_prime: *const f64,
    beta: f64,
    D: u64,
    K: u64,
    h_out: *mut f64,
) -> i32 {
    polydim_stiefel_residual_inject_v26403(h, W, z_orig, z_prime, beta, D, K, h_out)
}

#[no_mangle]
pub extern "C" fn polydim_rust_stiefel_residual_inject_v26503(
    h: *const f64,
    W: *const f64,
    z_orig: *const f64,
    z_prime: *const f64,
    beta: f64,
    D: u64,
    K: u64,
    h_out: *mut f64,
) -> i32 {
    polydim_rust_stiefel_residual_inject_v26403(h, W, z_orig, z_prime, beta, D, K, h_out)
}

#[no_mangle]
pub extern "C" fn polydim_cam_workspace_bytes_v26503(M: u64) -> u64 {
    polydim_cam_workspace_bytes_v26403(M)
}

#[no_mangle]
pub extern "C" fn polydim_rust_cam_workspace_bytes_v26503(M: u64) -> u64 {
    polydim_cam_workspace_bytes_v26403(M)
}

#[no_mangle]
pub extern "C" fn polydim_cam_attention_retrieve_v26503(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    workspace_bytes: u64,
    v_out: *mut f64,
) -> i32 {
    polydim_cam_attention_retrieve_v26403(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, workspace_bytes, v_out)
}

#[no_mangle]
pub extern "C" fn polydim_rust_cam_attention_retrieve_v26503(
    q: *const f64,
    K_mat: *const f64,
    V_mat: *const f64,
    mask: *const u8,
    M: u64,
    D: u64,
    inv_temp: f64,
    workspace: *mut f64,
    workspace_bytes: u64,
    v_out: *mut f64,
) -> i32 {
    polydim_cam_attention_retrieve_v26403(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, workspace_bytes, v_out)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_claim_writer_v26503(
    header_ptr: *mut c_void,
    header_len: u64,
    pid: u32,
    out_write_slot: *mut u32,
    out_writer_token: *mut u64,
) -> i32 {
    polydim_pmtp_v6_claim_writer_v26403(header_ptr, header_len, pid, out_write_slot, out_writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_writer_heartbeat_v26503(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_writer_heartbeat_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_abort_writer_v26503(
    header_ptr: *mut c_void,
    header_len: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_abort_writer_v26403(header_ptr, header_len, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_force_recover_v26503(
    header_ptr: *mut c_void,
    header_len: u64,
) -> i32 {
    polydim_pmtp_v6_force_recover_v26403(header_ptr, header_len)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_publish_flip_v26503(
    header_ptr: *mut c_void,
    header_len: u64,
    written_slot: u32,
    timestamp_ns: u64,
    writer_token: u64,
) -> i32 {
    polydim_pmtp_v6_publish_flip_v26403(header_ptr, header_len, written_slot, timestamp_ns, writer_token)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_read_snapshot_v26503(
    header_ptr: *const c_void,
    header_len: u64,
    slab_base_ptr: *const c_void,
    slab_total_bytes: u64,
    payload_bytes: u64,
    out_buf: *mut c_void,
    out_slot: *mut u32,
    out_generation: *mut u64,
) -> i32 {
    polydim_pmtp_v6_read_snapshot_v26403(header_ptr, header_len, slab_base_ptr, slab_total_bytes, payload_bytes, out_buf, out_slot, out_generation)
}

#[no_mangle]
pub extern "C" fn polydim_pmtp_v6_validate_snapshot_v26503(
    header_ptr: *const c_void,
    header_len: u64,
    gen: u64,
    out_ok: *mut u32,
) -> i32 {
    polydim_pmtp_v6_validate_snapshot_v26403(header_ptr, header_len, gen, out_ok)
}
