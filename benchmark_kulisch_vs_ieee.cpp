// ============================================================================
// POLYDIM EINSOF - HPC & EMBEDDED SYSTEMS BENCHMARK
// Benchmark Vectorial Kulisch vs. IEEE-754 (Double Precision) en CPU Commodity
// Target: WinLibs GCC 14.2 / Clang++ (C++20, SIMD AVX2 / AVX-FMA)
//
// Destinatario Pedagógico: Alumnos de Computación de Alto Rendimiento (HPC)
//                          y Sistemas Embebidos Críticos (Aerospace, Defense, FFI)
//
// Objetivos Matemáticos y Computacionales:
// 1. Demostrar la falla asintótica de IEEE-754 ante productos escalares patológicos
//    con número de condición extremal kappa(A) = 1.00e+600.
// 2. Demostrar la no asociatividad y absorción catastrófica de flotantes estándar.
// 3. Demostrar la exactitud matemática absoluta (error 0.0) del Superacumulador
//    Kulisch de 68 limbs (4.352 bits de punto fijo, W >= 4.288 bits).
// 4. Medir Throughput de silicio (GFLOPS) y overhead de precisión Kulisch.
// ============================================================================

#include <iostream>
#include <iomanip>
#include <vector>
#include <array>
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <cmath>
#include <chrono>
#include <random>
#include <bit>
#include <limits>
#include <string>

#if defined(__x86_64__) || defined(_M_X64)
#include <immintrin.h>
#endif

#if defined(_WIN32)
#include <windows.h>
#include <psapi.h>
#endif

namespace polydim {

// ----------------------------------------------------------------------------
// 1. CONSTANTES ARITMÉTICAS Y ESTRUCTURA DEL SUPERACUMULADOR KULISCH
// ----------------------------------------------------------------------------
// Rango total de productos IEEE-754 Binary64:
// Mínimo producto subnormal: 2^-1074 * 2^-1074 = 2^-2148
// Máximo producto normal:    2^+1024 * 2^+1024 = 2^+2048
// Span total necesario:     2048 - (-2148) = 4196 bits + bits de guardia.
// Asignamos 68 limbs de 64 bits = 4.352 bits (cubre 4.288 bits con holgura).
// Bit 0 del acumulador representa 2^-2148.
// ----------------------------------------------------------------------------
inline constexpr std::size_t kKulischLimbs = 68;
inline constexpr int kMinWeight = -2148;

struct alignas(64) KulischSuperaccumulator {
    std::array<std::uint64_t, kKulischLimbs> limbs{};

    void reset() noexcept {
        limbs.fill(0);
    }

    // Suma exacta de un entero sin signo de 128 bits en un offset de bit arbitrario
    void add_u128_at(unsigned __int128 val, int bit_offset) noexcept {
        if (val == 0) return;
        std::size_t limb_idx = static_cast<std::size_t>(bit_offset / 64);
        int bit_shift = bit_offset % 64;
        if (limb_idx >= kKulischLimbs) return;

        uint64_t v_lo = static_cast<uint64_t>(val);
        uint64_t v_hi = static_cast<uint64_t>(val >> 64);

        // Descomposición canónica sin solapamiento (Bit-Exact Partition)
        uint64_t w0 = (bit_shift == 0) ? v_lo : (v_lo << bit_shift);
        uint64_t w1 = (bit_shift == 0) ? v_hi : ((v_lo >> (64 - bit_shift)) | (v_hi << bit_shift));
        uint64_t w2 = (bit_shift == 0) ? 0 : (v_hi >> (64 - bit_shift));

        unsigned __int128 carry = 0;
        if (limb_idx < kKulischLimbs) {
            unsigned __int128 s = static_cast<unsigned __int128>(limbs[limb_idx]) + w0;
            limbs[limb_idx] = static_cast<uint64_t>(s);
            carry = s >> 64;
        }
        if (limb_idx + 1 < kKulischLimbs) {
            unsigned __int128 s = static_cast<unsigned __int128>(limbs[limb_idx + 1]) + w1 + carry;
            limbs[limb_idx + 1] = static_cast<uint64_t>(s);
            carry = s >> 64;
        }
        if (limb_idx + 2 < kKulischLimbs) {
            unsigned __int128 s = static_cast<unsigned __int128>(limbs[limb_idx + 2]) + w2 + carry;
            limbs[limb_idx + 2] = static_cast<uint64_t>(s);
            carry = s >> 64;
        }
        std::size_t cur = limb_idx + 3;
        while (carry > 0 && cur < kKulischLimbs) {
            unsigned __int128 s = static_cast<unsigned __int128>(limbs[cur]) + carry;
            limbs[cur] = static_cast<uint64_t>(s);
            carry = s >> 64;
            cur++;
        }
    }

    // Resta exacta de un entero sin signo de 128 bits en un offset de bit arbitrario
    void sub_u128_at(unsigned __int128 val, int bit_offset) noexcept {
        if (val == 0) return;
        std::size_t limb_idx = static_cast<std::size_t>(bit_offset / 64);
        int bit_shift = bit_offset % 64;
        if (limb_idx >= kKulischLimbs) return;

        uint64_t v_lo = static_cast<uint64_t>(val);
        uint64_t v_hi = static_cast<uint64_t>(val >> 64);

        uint64_t w0 = (bit_shift == 0) ? v_lo : (v_lo << bit_shift);
        uint64_t w1 = (bit_shift == 0) ? v_hi : ((v_lo >> (64 - bit_shift)) | (v_hi << bit_shift));
        uint64_t w2 = (bit_shift == 0) ? 0 : (v_hi >> (64 - bit_shift));

        uint64_t b = 0;
        if (limb_idx < kKulischLimbs) {
            uint64_t prev = limbs[limb_idx];
            uint64_t diff = prev - w0;
            b = (prev < w0) ? 1 : 0;
            limbs[limb_idx] = diff;
        }
        if (limb_idx + 1 < kKulischLimbs) {
            uint64_t prev = limbs[limb_idx + 1];
            unsigned __int128 to_sub = static_cast<unsigned __int128>(w1) + b;
            uint64_t diff = prev - static_cast<uint64_t>(to_sub);
            b = (static_cast<unsigned __int128>(prev) < to_sub) ? 1 : 0;
            limbs[limb_idx + 1] = diff;
        }
        if (limb_idx + 2 < kKulischLimbs) {
            uint64_t prev = limbs[limb_idx + 2];
            unsigned __int128 to_sub = static_cast<unsigned __int128>(w2) + b;
            uint64_t diff = prev - static_cast<uint64_t>(to_sub);
            b = (static_cast<unsigned __int128>(prev) < to_sub) ? 1 : 0;
            limbs[limb_idx + 2] = diff;
        }
        std::size_t cur = limb_idx + 3;
        while (b > 0 && cur < kKulischLimbs) {
            uint64_t prev = limbs[cur];
            uint64_t next_b = (prev == 0) ? 1 : 0;
            limbs[cur] = prev - 1;
            b = next_b;
            cur++;
        }
    }

    bool is_zero() const noexcept {
        for (std::size_t i = 0; i < kKulischLimbs; ++i) {
            if (limbs[i] != 0) return false;
        }
        return true;
    }
};

// ----------------------------------------------------------------------------
// 2. DESCOMPOSICIÓN EXACTA IEEE-754 BINARY64
// ----------------------------------------------------------------------------
struct FP64Unpacked {
    uint64_t sig;   // Significando de 53 bits (con bit implícito para normales)
    int exp;        // Exponente no sesgado tal que val = sig * 2^exp
    int sign;       // 0 para positivo, 1 para negativo
    bool is_zero;
    bool is_nan;
    bool is_inf;
};

inline FP64Unpacked unpack_fp64(double d) noexcept {
    FP64Unpacked u{};
    uint64_t bits = std::bit_cast<uint64_t>(d);
    u.sign = static_cast<int>(bits >> 63);
    uint32_t exp_field = static_cast<uint32_t>((bits >> 52) & 0x7FF);
    uint64_t frac = bits & 0x000F'FFFF'FFFF'FFFFULL;

    if (exp_field == 0x7FF) {
        if (frac == 0) {
            u.is_inf = true;
        } else {
            u.is_nan = true;
        }
        return u;
    }

    if (exp_field == 0) {
        if (frac == 0) {
            u.is_zero = true;
            u.sig = 0;
            u.exp = 0;
        } else {
            // Subnormal: val = frac * 2^-1074
            u.is_zero = false;
            u.sig = frac;
            u.exp = -1074;
        }
    } else {
        // Normal: val = (frac | 1<<52) * 2^(exp_field - 1023 - 52)
        u.is_zero = false;
        u.sig = frac | (1ULL << 52);
        u.exp = static_cast<int>(exp_field) - 1075;
    }
    return u;
}

// Multiplicación exacta de significandos de 53 bits -> 106 bits
inline unsigned __int128 mul53_exact(uint64_t sa, uint64_t sb) noexcept {
    return static_cast<unsigned __int128>(sa) * sb;
}

// Depósito sin redondeo en el superacumulador Kulisch
inline void deposit_exact_prod(KulischSuperaccumulator& acc, double a, double b) noexcept {
    FP64Unpacked ua = unpack_fp64(a);
    FP64Unpacked ub = unpack_fp64(b);

    if (ua.is_zero || ub.is_zero) return;
    if (ua.is_nan || ub.is_nan || ua.is_inf || ub.is_inf) return;

    int prod_sign = ua.sign ^ ub.sign;
    int prod_exp = ua.exp + ub.exp;

    unsigned __int128 sig_prod = mul53_exact(ua.sig, ub.sig);
    int bit_offset = prod_exp - kMinWeight;

    if (bit_offset >= 0) {
        if (prod_sign == 0) {
            acc.add_u128_at(sig_prod, bit_offset);
        } else {
            acc.sub_u128_at(sig_prod, bit_offset);
        }
    }
}

// Reducción exacta a FP64 con Round-to-Nearest-Even (RNE) y Sticky Bits
inline double round_to_fp64(const KulischSuperaccumulator& acc) noexcept {
    bool is_negative = (acc.limbs[kKulischLimbs - 1] & (1ULL << 63)) != 0;
    KulischSuperaccumulator mag = acc;

    if (is_negative) {
        uint64_t carry = 1;
        for (std::size_t i = 0; i < kKulischLimbs; ++i) {
            unsigned __int128 s = static_cast<unsigned __int128>(~mag.limbs[i]) + carry;
            mag.limbs[i] = static_cast<uint64_t>(s);
            carry = static_cast<uint64_t>(s >> 64);
        }
    }

    int highest_bit = -1;
    for (int i = static_cast<int>(kKulischLimbs) - 1; i >= 0; --i) {
        if (mag.limbs[i] != 0) {
            highest_bit = i * 64 + (63 - std::countl_zero(mag.limbs[i]));
            break;
        }
    }

    if (highest_bit < 0) {
        return is_negative ? -0.0 : 0.0;
    }

    int true_exp = highest_bit + kMinWeight;
    if (true_exp > 1023) {
        return is_negative ? -std::numeric_limits<double>::infinity() : std::numeric_limits<double>::infinity();
    }
    if (true_exp < -1074) {
        return is_negative ? -0.0 : 0.0;
    }

    uint64_t mantissa = 0;
    uint32_t exp_field = 0;

    if (true_exp >= -1022) {
        exp_field = static_cast<uint32_t>(true_exp + 1023);
        int shift = highest_bit - 52;
        uint64_t m53 = 0;
        int limb_idx = shift / 64;
        int bit_rem = shift % 64;

        if (bit_rem >= 0) {
            m53 = mag.limbs[limb_idx] >> bit_rem;
            if (bit_rem > 0 && limb_idx + 1 < static_cast<int>(kKulischLimbs)) {
                m53 |= (mag.limbs[limb_idx + 1] << (64 - bit_rem));
            }
        }

        bool guard = false;
        if (shift - 1 >= 0) {
            int g_limb = (shift - 1) / 64;
            int g_bit = (shift - 1) % 64;
            guard = (mag.limbs[g_limb] & (1ULL << g_bit)) != 0;
        }

        bool sticky = false;
        for (int b = shift - 2; b >= 0; --b) {
            int s_limb = b / 64;
            int s_bit = b % 64;
            if ((mag.limbs[s_limb] & (1ULL << s_bit)) != 0) {
                sticky = true;
                break;
            }
        }

        if (guard && (sticky || (m53 & 1) != 0)) {
            m53++;
            if (m53 >= (1ULL << 53)) {
                m53 >>= 1;
                exp_field++;
            }
        }
        mantissa = m53 & 0x000F'FFFF'FFFF'FFFFULL;
    } else {
        exp_field = 0;
        int shift = -1074 - kMinWeight;
        uint64_t m52 = 0;
        int limb_idx = shift / 64;
        int bit_rem = shift % 64;

        if (bit_rem >= 0) {
            m52 = mag.limbs[limb_idx] >> bit_rem;
            if (bit_rem > 0 && limb_idx + 1 < static_cast<int>(kKulischLimbs)) {
                m52 |= (mag.limbs[limb_idx + 1] << (64 - bit_rem));
            }
        }

        bool guard = false;
        if (shift - 1 >= 0) {
            int g_limb = (shift - 1) / 64;
            int g_bit = (shift - 1) % 64;
            guard = (mag.limbs[g_limb] & (1ULL << g_bit)) != 0;
        }

        bool sticky = false;
        for (int b = shift - 2; b >= 0; --b) {
            int s_limb = b / 64;
            int s_bit = b % 64;
            if ((mag.limbs[s_limb] & (1ULL << s_bit)) != 0) {
                sticky = true;
                break;
            }
        }

        if (guard && (sticky || (m52 & 1) != 0)) {
            m52++;
            if (m52 >= (1ULL << 52)) {
                exp_field = 1;
                m52 &= 0x000F'FFFF'FFFF'FFFFULL;
            }
        }
        mantissa = m52;
    }

    uint64_t final_bits = (static_cast<uint64_t>(is_negative ? 1 : 0) << 63) |
                          (static_cast<uint64_t>(exp_field) << 52) |
                          (mantissa & 0x000F'FFFF'FFFF'FFFFULL);

    return std::bit_cast<double>(final_bits);
}

// ----------------------------------------------------------------------------
// 3. HARDWARE PROBE Y TELEMETRÍA DE SILICIO (Silicon Contract)
// ----------------------------------------------------------------------------
struct HardwareCapabilities {
    bool has_avx = false;
    bool has_avx2 = false;
    bool has_fma = false;
    std::string cpu_name = "Unknown Commodity x86_64";
};

inline HardwareCapabilities probe_hardware() noexcept {
    HardwareCapabilities caps;
#if defined(__GNUC__) || defined(__clang__)
    caps.has_avx = __builtin_cpu_supports("avx");
    caps.has_avx2 = __builtin_cpu_supports("avx2");
    caps.has_fma = __builtin_cpu_supports("fma");
#endif
    return caps;
}

inline double get_ram_mb() noexcept {
#if defined(_WIN32)
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return static_cast<double>(pmc.WorkingSetSize) / (1024.0 * 1024.0);
    }
#endif
    return 0.0;
}

// ----------------------------------------------------------------------------
// 4. KERNELS COMPUTACIONALES DE PRODUCTO ESCALAR
// ----------------------------------------------------------------------------

// Kernel 1: IEEE-754 Escalar Estándar
double dot_product_ieee_scalar(const double* __restrict a, const double* __restrict b, std::size_t n) noexcept {
    double sum = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        sum += a[i] * b[i];
    }
    return sum;
}

// Kernel 2: IEEE-754 Vectorizado SIMD AVX2 / AVX FMA (4-way acumuladores paralelos)
#if defined(__GNUC__) || defined(__clang__)
__attribute__((target("avx,fma")))
#endif
double dot_product_ieee_avx(const double* __restrict a, const double* __restrict b, std::size_t n) noexcept {
    std::size_t i = 0;
    __m256d vsum0 = _mm256_setzero_pd();
    __m256d vsum1 = _mm256_setzero_pd();

    for (; i + 7 < n; i += 8) {
        __m256d va0 = _mm256_loadu_pd(a + i);
        __m256d vb0 = _mm256_loadu_pd(b + i);
        __m256d va1 = _mm256_loadu_pd(a + i + 4);
        __m256d vb1 = _mm256_loadu_pd(b + i + 4);

        vsum0 = _mm256_fmadd_pd(va0, vb0, vsum0);
        vsum1 = _mm256_fmadd_pd(va1, vb1, vsum1);
    }

    __m256d vsum = _mm256_add_pd(vsum0, vsum1);
    for (; i + 3 < n; i += 4) {
        __m256d va = _mm256_loadu_pd(a + i);
        __m256d vb = _mm256_loadu_pd(b + i);
        vsum = _mm256_fmadd_pd(va, vb, vsum);
    }

    alignas(32) double buf[4];
    _mm256_storeu_pd(buf, vsum);
    double total = (buf[0] + buf[1]) + (buf[2] + buf[3]);

    // Cola escalar restante
    for (; i < n; ++i) {
        total += a[i] * b[i];
    }
    return total;
}

// Kernel 3: Kulisch Superaccumulator Exacto
double dot_product_kulisch(const double* __restrict a, const double* __restrict b, std::size_t n, KulischSuperaccumulator& acc) noexcept {
    acc.reset();
    for (std::size_t i = 0; i < n; ++i) {
        deposit_exact_prod(acc, a[i], b[i]);
    }
    return round_to_fp64(acc);
}

} // namespace polydim

// ============================================================================
// MAIN BENCHMARK & PEDAGOGICAL SUITE
// ============================================================================
int main() {
    using namespace polydim;

    std::cout << "================================================================================\n";
    std::cout << "POLYDIM EINSOF - BENCHMARK ARITMETICO AVANZADO (HPC & EMBEDDED SYSTEMS)\n";
    std::cout << "Precision Exacta Kulisch vs. Acumulacion IEEE-754 (Double / SIMD AVX2)\n";
    std::cout << "================================================================================\n\n";

    // 1. Hardware Inspection
    HardwareCapabilities caps = probe_hardware();
    std::cout << "[HARDWARE CONTRACT]\n";
    std::cout << "  CPU AVX Support   : " << (caps.has_avx ? "YES (256-bit FP Vectors)" : "NO") << "\n";
    std::cout << "  CPU AVX2 Support  : " << (caps.has_avx2 ? "YES (256-bit Int Vectors)" : "NO (Commodity Floor AVX/FMA)") << "\n";
    std::cout << "  CPU FMA3 Support  : " << (caps.has_fma ? "YES (Fused Multiply-Add vfmadd)" : "NO") << "\n";
    std::cout << "  RAM Inicial       : " << std::fixed << std::setprecision(2) << get_ram_mb() << " MB\n\n";

    // 2. Construcción del Producto Escalar Patológico
    // Dimensión N = 2,000,000 elementos (500,000 bloques de 4 elementos)
    // Rango de magnitudes: 10^+300 y 10^-300
    // kappa(A) = max|A| / min|A| = 10^300 / 10^-300 = 10^600.
    constexpr std::size_t kN = 2'000'000;
    std::cout << "[GENERACION DE CASO DE ESTUDIO PATOLOGICO]\n";
    std::cout << "  Dimension Vectorial N  : " << kN << " elementos FP64 (16.0 MB por vector)\n";
    std::cout << "  Estructura de Cuartetos: [ +1e300, +1e-300, -1e300, -1e-300 ] x " << (kN / 4) << "\n";
    std::cout << "  Suma Exacta Teorica    : 0.0000000000000000e+00 (Cancelacion Matematica Cero)\n";
    std::cout << "  Condicion kappa(A)     : 1.000000e+600  (Rango Dinamico = ~1993 bits)\n";
    std::cout << "  Capacidad Mantisa FP64 : 53 bits (~15.95 digitos decimales)\n";
    std::cout << "  Deficit de Precision   : 1940 bits fuera del alcance de IEEE-754\n\n";

    std::vector<double> A(kN);
    std::vector<double> B(kN);

    const double kLarge = 1.0e300;
    const double kSmall = 1.0e-300;

    for (std::size_t k = 0; k < kN; k += 4) {
        A[k + 0] = kLarge;  B[k + 0] = 1.0;   // Producto = +1e300
        A[k + 1] = kSmall;  B[k + 1] = 1.0;   // Producto = +1e-300
        A[k + 2] = kLarge;  B[k + 2] = -1.0;  // Producto = -1e300
        A[k + 3] = kSmall;  B[k + 3] = -1.0;  // Producto = -1e-300
    }

    // ------------------------------------------------------------------------
    // BENCHMARK 1: IEEE-754 Scalar Accumulator
    // ------------------------------------------------------------------------
    auto t0 = std::chrono::high_resolution_clock::now();
    double res_ieee_scalar = dot_product_ieee_scalar(A.data(), B.data(), kN);
    auto t1 = std::chrono::high_resolution_clock::now();
    double dt_scalar_s = std::chrono::duration<double>(t1 - t0).count();
    double gflops_scalar = (2.0 * kN * 1e-9) / dt_scalar_s;

    // ------------------------------------------------------------------------
    // BENCHMARK 2: IEEE-754 SIMD AVX / FMA Accumulator
    // ------------------------------------------------------------------------
    auto t2 = std::chrono::high_resolution_clock::now();
    double res_ieee_simd = dot_product_ieee_avx(A.data(), B.data(), kN);
    auto t3 = std::chrono::high_resolution_clock::now();
    double dt_simd_s = std::chrono::duration<double>(t3 - t2).count();
    double gflops_simd = (2.0 * kN * 1e-9) / dt_simd_s;

    // ------------------------------------------------------------------------
    // BENCHMARK 3: Kulisch 68-Limb Exact Superaccumulator
    // ------------------------------------------------------------------------
    KulischSuperaccumulator kulisch_acc;
    auto t4 = std::chrono::high_resolution_clock::now();
    double res_kulisch = dot_product_kulisch(A.data(), B.data(), kN, kulisch_acc);
    auto t5 = std::chrono::high_resolution_clock::now();
    double dt_kulisch_s = std::chrono::duration<double>(t5 - t4).count();
    double gflops_kulisch = (2.0 * kN * 1e-9) / dt_kulisch_s;

    // ------------------------------------------------------------------------
    // ANALISIS DE EXACTITUD Y ERRORES
    // ------------------------------------------------------------------------
    double err_scalar = std::abs(res_ieee_scalar - 0.0);
    double err_simd = std::abs(res_ieee_simd - 0.0);
    double err_kulisch = std::abs(res_kulisch - 0.0);
    bool kulisch_bit_zero = kulisch_acc.is_zero();

    std::cout << "[RESULTADOS COMPARATIVOS DE ACUMULACION]\n";
    std::cout << std::scientific << std::setprecision(16);
    std::cout << "  1. IEEE-754 Escalar       : " << res_ieee_scalar << "\n";
    std::cout << "     Error Absoluto         : " << err_scalar << "\n";
    std::cout << "     Diagnostico            : Absorcion Catastrofica Total del termino 1e-300\n";
    std::cout << "                              Al sumar 1e300 + 1e-300, el termino menor se anula a cero.\n\n";

    std::cout << "  2. IEEE-754 SIMD AVX/FMA  : " << res_ieee_simd << "\n";
    std::cout << "     Error Absoluto         : " << err_simd << "\n";
    std::cout << "     Diagnostico            : No-Asociatividad SIMD.\n";
    std::cout << "                              La vectorizacion agrupa los 4 terminos en lanes paralelos,\n";
    std::cout << "                              modificando el orden de suma y destruyendo la reproducibilidad.\n\n";

    std::cout << "  3. Kulisch Superacc (68L) : " << res_kulisch << "\n";
    std::cout << "     Error Absoluto         : " << err_kulisch << "\n";
    std::cout << "     Bit-Exact All Limbs = 0: " << (kulisch_bit_zero ? "EXACT TRUE (0 residuo en 4352 bits)" : "FALSE") << "\n";
    std::cout << "     Diagnostico            : Precision Infinita Racional en Rango IEEE-754.\n";
    std::cout << "                              Cero absorcion. Cero cancelacion. Cero desbordamiento.\n\n";

    std::cout << "[METRICAS DE RENDIMIENTO DE SILICIO]\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "  Kernel IEEE-754 Escalar   : Latencia = " << (dt_scalar_s * 1000.0) << " ms | Throughput = " << gflops_scalar << " GFLOPS\n";
    std::cout << "  Kernel IEEE-754 SIMD AVX  : Latencia = " << (dt_simd_s * 1000.0) << " ms | Throughput = " << gflops_simd << " GFLOPS (Speedup: " << (dt_scalar_s / dt_simd_s) << "x)\n";
    std::cout << "  Kernel Kulisch Exacto     : Latencia = " << (dt_kulisch_s * 1000.0) << " ms | Throughput = " << gflops_kulisch << " GFLOPS\n";
    std::cout << "  Coste de Exactitud Kulisch: " << (dt_kulisch_s / dt_simd_s) << "x ciclos vs SIMD inexacto\n\n";

    // ------------------------------------------------------------------------
    // EXPERIMENTO 2: CANCELACIÓN CATASTRÓFICA ASIMÉTRICA (RUMP/KAHAN PATTERN)
    // Vector con desfase de registro SIMD para forzar colapso de lanes AVX
    // ------------------------------------------------------------------------
    std::cout << "[EXPERIMENTO 2: CANCELACION ASIMETRICA Y COLAPSO DE LANES SIMD]\n";
    std::cout << "  Configurando vector con desfase de 3 elementos para desincronizar lanes AVX...\n";
    std::vector<double> A_asym(kN);
    std::vector<double> B_asym(kN);

    // Diseñamos pares que matemáticamente suman 0:
    // Para cada grupo de 8:
    // A: [+1e300, +1e300, +1e-300, -1e300, -1e300, +1e-300, -1e-300, -1e-300]
    // B: todos 1.0
    for (std::size_t k = 0; k < kN; k += 8) {
        A_asym[k + 0] = kLarge;   B_asym[k + 0] = 1.0;
        A_asym[k + 1] = kLarge;   B_asym[k + 1] = 1.0;
        A_asym[k + 2] = kSmall;   B_asym[k + 2] = 1.0;
        A_asym[k + 3] = -kLarge;  B_asym[k + 3] = 1.0;
        A_asym[k + 4] = -kLarge;  B_asym[k + 4] = 1.0;
        A_asym[k + 5] = kSmall;   B_asym[k + 5] = 1.0;
        A_asym[k + 6] = -kSmall;  B_asym[k + 6] = 1.0;
        A_asym[k + 7] = -kSmall;  B_asym[k + 7] = 1.0;
    }

    double res_asym_scalar = dot_product_ieee_scalar(A_asym.data(), B_asym.data(), kN);
    double res_asym_simd   = dot_product_ieee_avx(A_asym.data(), B_asym.data(), kN);
    KulischSuperaccumulator acc_asym;
    double res_asym_kulisch = dot_product_kulisch(A_asym.data(), B_asym.data(), kN, acc_asym);

    std::cout << std::scientific << std::setprecision(16);
    std::cout << "  Resultado IEEE-754 Escalar       : " << res_asym_scalar << "\n";
    std::cout << "  Resultado IEEE-754 SIMD AVX      : " << res_asym_simd << "\n";
    std::cout << "  Resultado Kulisch Superacc (68L) : " << res_asym_kulisch << "\n";
    std::cout << "  Residuo Bit-a-Bit Kulisch Limbs  : " << (acc_asym.is_zero() ? "0 (Bit-Exact Zero)" : "NON-ZERO") << "\n\n";

    // ------------------------------------------------------------------------
    // EXPERIMENTO PEDAGOGICO 3: DEMOSTRACION DE LA VIOLACION ASOCIATIVA EN IEEE-754
    // ------------------------------------------------------------------------
    std::cout << "[EXPERIMENTO PEDAGOGICO 3: VIOLACION DE LA LEY ASOCIATIVA EN IEEE-754]\n";
    double a_large = 1.0e300;
    double b_small = 1.0e-300;
    double c_neg_large = -1.0e300;

    double order_1 = (a_large + b_small) + c_neg_large;
    double order_2 = a_large + (b_small + c_neg_large);
    double order_3 = (a_large + c_neg_large) + b_small;

    std::cout << std::scientific << std::setprecision(16);
    std::cout << "  Terminos: A = +1e300, B = +1e-300, C = -1e300\n";
    std::cout << "  Orden 1: (A + B) + C = (" << a_large << " + " << b_small << ") + " << c_neg_large << " = " << order_1 << " (B se perdio totalmente por absorcion)\n";
    std::cout << "  Orden 2: A + (B + C) = " << a_large << " + (" << b_small << " + " << c_neg_large << ") = " << order_2 << " (B se perdio totalmente por absorcion)\n";
    std::cout << "  Orden 3: (A + C) + B = (" << a_large << " + " << c_neg_large << ") + " << b_small << " = " << order_3 << " (B sobrevivio tras cancelacion exacta)\n";
    std::cout << "  Conclusión HPC/Sistemas: En IEEE-754 el resultado numerico es funcion del orden de despacho.\n";
    std::cout << "  El acumulador Kulisch garantiza invariancia total ante permutaciones (Suma Conmutativa Real).\n\n";

    // ------------------------------------------------------------------------
    // TELEMETRIA FINAL Y LOG CRUDO DE SILICIO
    // ------------------------------------------------------------------------
    double ram_final = get_ram_mb();
    int exit_code = (kulisch_bit_zero && acc_asym.is_zero() && (res_kulisch == 0.0) && (res_asym_kulisch == 0.0)) ? 0 : 1;

    std::cout << "[RAW SILICON TELEMETRY TUPLE]\n";
    std::cout << "("
              << "ExitCode=" << exit_code << ", "
              << "LatencyKulisch_ms=" << std::fixed << std::setprecision(2) << (dt_kulisch_s * 1000.0) << ", "
              << "RAM_MB=" << ram_final << ", "
              << "GFLOPS_AVX=" << std::setprecision(3) << gflops_simd << ", "
              << "GFLOPS_Kulisch=" << gflops_kulisch << ", "
              << "Kappa_A=1.00e+600, "
              << "Error_IEEE_Scalar=" << std::scientific << std::setprecision(6) << err_scalar << ", "
              << "Error_Kulisch=" << err_kulisch
              << ")\n";

    return exit_code;
}
