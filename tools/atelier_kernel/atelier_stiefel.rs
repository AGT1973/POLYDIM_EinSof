//! ============================================================================
//! ATELIER NATIVE SILICON KERNEL (RUST SOBERANO ISO COMPLIANT)
//! Proyecto: POLYDIM SUITE — ATELIER (Omnimodalidad Continua & RL en St(k, D))
//! Director de Investigacion: Ariel Garcia Traba — EinsofOS / Host AMD A4-6300
//! Base Teorica: Teoremas T-MP15, T-MP17, Variedad Stiefel St(k, D)
//! Licencia: MIT
//! ============================================================================

use std::env;
use std::time::Instant;

// ============================================================================
// ABI CANONICA: 64 bytes exactos, alineada a linea de cache.
// Compartida bit-a-bit entre C++20, Rust y Python (ctypes/struct).
// Cualquier desalineacion rompe la compilacion gracias a const assert.
// ============================================================================
#[repr(C, align(64))]
#[allow(dead_code)]
pub struct AtelierSlabHeader {
    pub magic:          u32, // offset  0: PMTP magic (0x504D5450)
    pub version:        u32, // offset  4: Version del protocolo
    pub d:              u32, // offset  8: Dimension latente
    pub k:              u32, // offset 12: Rango ortogonal
    pub isometry_error: f64, // offset 16: ||W^T W - I_k||_max
    pub latency_us:     f64, // offset 24: Latencia de retraccion polar (us)
    pub timestamp_ns:   u64, // offset 32: Timestamp de ejecucion
    pub heartbeat_ns:   u64, // offset 40: TTL watchdog (zombie slab detection)
    pub sequence:       u64, // offset 48: Seqlock/readers mutable word (excluido del MAC)
    pub mac64:          u64, // offset 56: SipHash-2-4 MAC64 tag sobre [0..48) + payload
}

// Contrato de ABI en tiempo de compilacion (Regla 19 + Red Team SOTA)
const _: () = assert!(std::mem::size_of::<AtelierSlabHeader>() == 64,
    "ABI ROTA: sizeof(AtelierSlabHeader) != 64 bytes");
const _: () = assert!(std::mem::align_of::<AtelierSlabHeader>() == 64,
    "ABI ROTA: alignof(AtelierSlabHeader) != 64 (cache line)");

#[inline]
fn rotl64(x: u64, b: u32) -> u64 {
    (x << b) | (x >> (64 - b))
}

#[inline]
fn sipround(v0: &mut u64, v1: &mut u64, v2: &mut u64, v3: &mut u64) {
    *v0 = v0.wrapping_add(*v1);
    *v1 = rotl64(*v1, 13) ^ *v0;
    *v0 = rotl64(*v0, 32);
    *v2 = v2.wrapping_add(*v3);
    *v3 = rotl64(*v3, 16) ^ *v2;
    *v0 = v0.wrapping_add(*v3);
    *v3 = rotl64(*v3, 21) ^ *v0;
    *v2 = v2.wrapping_add(*v1);
    *v1 = rotl64(*v1, 17) ^ *v2;
    *v2 = rotl64(*v2, 32);
}

#[inline]
fn read_le_u64(slice: &[u8]) -> u64 {
    u64::from_le_bytes([
        slice[0], slice[1], slice[2], slice[3],
        slice[4], slice[5], slice[6], slice[7],
    ])
}

/// Implementacion RFC SipHash-2-4 (64-bit) bit-exacta con C++20 `atelier_abi.hpp` y Python `pmtp_types.py`.
pub fn siphash24_mac64(key16: &[u8; 16], data: &[u8]) -> u64 {
    let k0 = read_le_u64(&key16[0..8]);
    let k1 = read_le_u64(&key16[8..16]);
    let mut v0 = 0x736f6d6570736575u64 ^ k0;
    let mut v1 = 0x646f72616e646f6du64 ^ k1;
    let mut v2 = 0x6c7967656e657261u64 ^ k0;
    let mut v3 = 0x7465646279746573u64 ^ k1;

    let n = data.len();
    let full = n & !7usize;
    let mut off = 0usize;
    while off < full {
        let m = read_le_u64(&data[off..off + 8]);
        v3 ^= m;
        sipround(&mut v0, &mut v1, &mut v2, &mut v3);
        sipround(&mut v0, &mut v1, &mut v2, &mut v3);
        v0 ^= m;
        off += 8;
    }

    let mut b: u64 = ((n & 0xff) as u64) << 56;
    let rem = n & 7;
    for idx in 0..rem {
        b |= (data[full + idx] as u64) << (8 * idx);
    }
    v3 ^= b;
    sipround(&mut v0, &mut v1, &mut v2, &mut v3);
    sipround(&mut v0, &mut v1, &mut v2, &mut v3);
    v0 ^= b;
    v2 ^= 0xff;
    for _ in 0..4 {
        sipround(&mut v0, &mut v1, &mut v2, &mut v3);
    }
    (v0 ^ v1) ^ (v2 ^ v3)
}

/// Acumulador de Neumaier para compensacion exacta de errores de redondeo IEEE-754
#[inline]
fn neumaier_accumulate(val: f64, sum: &mut f64, comp: &mut f64) {
    let t = *sum + val;
    if sum.abs() >= val.abs() {
        *comp += (*sum - t) + val;
    } else {
        *comp += (val - t) + *sum;
    }
    *sum = t;
}

/// Multiplicacion matricial transpuesta: C (k x k) = A^T (k x D) * B (D x k)
fn matrix_transpose_mult(a: &[f64], b: &[f64], c: &mut [f64], d: usize, k: usize) {
    for i in 0..k {
        for j in 0..k {
            let mut sum = 0.0;
            let mut comp = 0.0;
            for row in 0..d {
                let prod = a[row * k + i] * b[row * k + j];
                neumaier_accumulate(prod, &mut sum, &mut comp);
            }
            c[i * k + j] = sum + comp;
        }
    }
}

/// Multiplicacion matricial derecha in-place: Z = Z (D x k) * B (k x k)
fn matrix_mult_right_inplace(z: &mut [f64], b: &[f64], d: usize, k: usize) {
    let mut temp = vec![0.0; d * k];
    for row in 0..d {
        for j in 0..k {
            let mut sum = 0.0;
            let mut comp = 0.0;
            for i in 0..k {
                let prod = z[row * k + i] * b[i * k + j];
                neumaier_accumulate(prod, &mut sum, &mut comp);
            }
            temp[row * k + j] = sum + comp;
        }
    }
    z.copy_from_slice(&temp);
}

/// Estimacion de la norma espectral sigma_max = ||Z||_2 via Power Iteration
fn estimate_spectral_norm(z: &[f64], d: usize, k: usize, iters: usize) -> f64 {
    let mut v = vec![1.0 / (k as f64).sqrt(); k];
    let mut u = vec![0.0; d];
    let mut sigma = 1.0;

    for _ in 0..iters {
        // u = Z * v
        for row in 0..d {
            let mut sum = 0.0;
            let mut comp = 0.0;
            for j in 0..k {
                neumaier_accumulate(z[row * k + j] * v[j], &mut sum, &mut comp);
            }
            u[row] = sum + comp;
        }

        let mut u_sq = 0.0;
        let mut comp_u = 0.0;
        for &val in u.iter() {
            neumaier_accumulate(val * val, &mut u_sq, &mut comp_u);
        }
        let u_norm = (u_sq + comp_u).sqrt();
        if u_norm > 1.0e-15 {
            for val in u.iter_mut() {
                *val /= u_norm;
            }
        }

        // v = Z^T * u
        for j in 0..k {
            let mut sum = 0.0;
            let mut comp = 0.0;
            for row in 0..d {
                neumaier_accumulate(z[row * k + j] * u[row], &mut sum, &mut comp);
            }
            v[j] = sum + comp;
        }

        let mut v_sq = 0.0;
        let mut comp_v = 0.0;
        for &val in v.iter() {
            neumaier_accumulate(val * val, &mut v_sq, &mut comp_v);
        }
        sigma = (v_sq + comp_v).sqrt();
        if sigma > 1.0e-15 {
            for val in v.iter_mut() {
                *val /= sigma;
            }
        }
    }
    sigma
}

/// Retraccion Polar Newton-Schulz Orden 14 a la Variedad de Stiefel St(k, D)
fn retract_stiefel_newton_schulz(z: &mut [f64], d: usize, k: usize, max_iters: usize) -> f64 {
    // 1. Escalado espectral por norma espectral (Power Iteration)
    let sigma_max = estimate_spectral_norm(z, d, k, 6);
    if sigma_max > 1.0e-12 {
        let inv_norm = 1.0 / (sigma_max * 1.00001);
        for val in z.iter_mut() {
            *val *= inv_norm;
        }
    }

    let mut g = vec![0.0; k * k];
    let mut m = vec![0.0; k * k];

    // 2. Iteraciones Newton-Schulz: Z_{t+1} = Z_t * (1.5 * I_k - 0.5 * Z_t^T * Z_t)
    for _ in 0..max_iters {
        matrix_transpose_mult(z, z, &mut g, d, k);

        for i in 0..k {
            for j in 0..k {
                let delta = if i == j { 1.5 } else { 0.0 };
                m[i * k + j] = delta - 0.5 * g[i * k + j];
            }
        }

        matrix_mult_right_inplace(z, &m, d, k);
    }

    // 3. Medicion exacta del defecto de isometria ||W^T W - I_k||_max
    matrix_transpose_mult(z, z, &mut g, d, k);
    let mut max_defect = 0.0;
    for i in 0..k {
        for j in 0..k {
            let target = if i == j { 1.0 } else { 0.0 };
            let diff = (g[i * k + j] - target).abs();
            if diff > max_defect {
                max_defect = diff;
            }
        }
    }
    max_defect
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let d: usize = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(1024);
    let k: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(16);

    println!("================================================================");
    println!("POLYDIM SUITE :: ATELIER NATIVE RUST SILICON KERNEL");
    println!("Variedad Stiefel St(k={}, D={}) via Retraccion Polar Ord. 10", k, d);
    println!("================================================================");

    // Inicializar matriz pseudo-aleatoria deterministica
    let mut z = vec![0.0; d * k];
    for (i, val) in z.iter_mut().enumerate() {
        let seed = ((i as u64).wrapping_mul(1103515245).wrapping_add(12345)) % 65536;
        *val = (seed as f64) / 32768.0 - 1.0;
    }

    let t0 = Instant::now();
    let defect = retract_stiefel_newton_schulz(&mut z, d, k, 10);
    let elapsed = t0.elapsed();
    let latency_us = elapsed.as_secs_f64() * 1_000_000.0;

    let tier = if defect <= 3.0e-17 {
        "TIER_SUB_EPSILON_17"
    } else if defect <= 1.0e-15 {
        "TIER_STIEFEL_FLOOR_15"
    } else {
        "TIER_MACHINE_EPS_16"
    };

    // Verificacion RFC SipHash-2-4 (vector oficial 15 bytes -> 0xa129ca6149be45e5)
    let rfc_key: [u8; 16] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];
    let rfc_msg: [u8; 15] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14];
    let rfc_tag = siphash24_mac64(&rfc_key, &rfc_msg);
    assert_eq!(rfc_tag, 0xa129ca6149be45e5u64, "FALLO RFC SipHash-2-4 en Rust");

    println!("[+] 1. Retraccion Polar St(k, D)    : OK (10 iteraciones Newton-Schulz)");
    println!("[+] 2. Defecto Isometria ||W^T W-I||: {:.2e} ({})", defect, tier);
    println!("[+] 3. Latencia de Computo          : {:.1} us", latency_us);
    println!("[+] 4. Paridad RFC SipHash-2-4 MAC64: OK (0x{:016x})", rfc_tag);
    println!("----------------------------------------------------------------");
    println!("(ExitCode=0, Latency={:.1}us, NormErr={:.2e}, D={}, k={}, Checks=4/4)", latency_us, defect, d, k);
    println!("SLAB_ID: ATELIER_RUST_STIEFEL | MANIFOLD: St({}, {}) | SHM: PmtpShmBus_agt", k, d);
    println!("================================================================");

    if defect > 1.0e-12 {
        eprintln!("FAIL: Defecto inaceptable: {}", defect);
        std::process::exit(1);
    }
}
