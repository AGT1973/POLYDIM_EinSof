#pragma once
// ============================================================================
// ATELIER ABI v1 + QDWH PRIMARY POLAR SOLVER + ZEROIZATION / MAC64 (C++20)
// ============================================================================

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <mutex>
#include <vector>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt.lib")
#else
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#endif

constexpr uint32_t PMTP_MAGIC_ATELIER = 0x504D5450; // "PMTP"
constexpr uint32_t PMTP_ABI_MIN_VERSION = 1;
constexpr uint32_t PMTP_ABI_MAX_VERSION = 1;
constexpr uint32_t PMTP_MAX_DIM_D = (1U << 20);
constexpr uint32_t PMTP_MAX_RANK_K = 4096U;

// ABI CANONICA: 64 bytes exactos alineados a linea de cache (paridad C++20 / Rust / Python)
struct alignas(64) AtelierSlabHeader {
    uint32_t magic;          // offset  0: PMTP magic (0x504D5450)
    uint32_t version;        // offset  4: Version del protocolo ABI (= 1)
    uint32_t D;              // offset  8: Dimension latente
    uint32_t k;              // offset 12: Rango ortogonal
    double   isometry_error; // offset 16: ||W^T W - I_k||_max
    double   latency_us;     // offset 24: Latencia de retraccion polar (us)
    uint64_t timestamp_ns;   // offset 32: Timestamp de ejecucion
    uint64_t heartbeat_ns;   // offset 40: TTL watchdog (zombie slab detection)
    uint64_t sequence;       // offset 48: Seqlock/readers mutable word (EXCLUIDO del MAC)
    uint64_t mac64;          // offset 56: Tag MAC keyed SipHash-2-4 (64-bit) sobre [0..48) + payload
};

static_assert(sizeof(AtelierSlabHeader) == 64, "ABI ROTA: sizeof(AtelierSlabHeader) != 64 bytes");
static_assert(alignof(AtelierSlabHeader) == 64, "ABI ROTA: alignof(AtelierSlabHeader) != 64");

enum class PolarSolverUsed {
    QDWH_PRIMARY = 0,
    MGS_QR_FALLBACK = 1,
    REJECTED_INVALID = 2
};

inline void explicit_zeroize(void* ptr, size_t len) {
    if (!ptr || len == 0) return;
#if defined(_WIN32)
    SecureZeroMemory(ptr, len);
#else
    volatile uint8_t* p = reinterpret_cast<volatile uint8_t*>(ptr);
    while (len--) {
        *p++ = 0;
    }
#endif
}

inline void neumaier_accumulate(double val, double& sum, double& comp) {
    double t = sum + val;
    if (std::abs(sum) >= std::abs(val)) {
        comp += (sum - t) + val;
    } else {
        comp += (val - t) + sum;
    }
    sum = t;
}

inline uint64_t siphash24_u64(const uint8_t key[16], const uint8_t* data, size_t len) {
    auto rotl64 = [](uint64_t x, int b) -> uint64_t { return (x << b) | (x >> (64 - b)); };
    auto read_le64 = [](const uint8_t* p) -> uint64_t {
        uint64_t v = 0;
        for (int i = 0; i < 8; ++i) v |= static_cast<uint64_t>(p[i]) << (8 * i);
        return v;
    };
    uint64_t k0 = read_le64(key);
    uint64_t k1 = read_le64(key + 8);
    uint64_t v0 = 0x736f6d6570736575ULL ^ k0;
    uint64_t v1 = 0x646f72616e646f6dULL ^ k1;
    uint64_t v2 = 0x6c7967656e657261ULL ^ k0;
    uint64_t v3 = 0x7465646279746573ULL ^ k1;
    auto sipround = [&]() {
        v0 += v1; v1 = rotl64(v1, 13); v1 ^= v0; v0 = rotl64(v0, 32);
        v2 += v3; v3 = rotl64(v3, 16); v3 ^= v2;
        v0 += v3; v3 = rotl64(v3, 21); v3 ^= v0;
        v2 += v1; v1 = rotl64(v1, 17); v1 ^= v2; v2 = rotl64(v2, 32);
    };
    const uint8_t* end = data + (len & ~static_cast<size_t>(7));
    for (; data < end; data += 8) {
        uint64_t m = read_le64(data);
        v3 ^= m;
        for (int i = 0; i < 2; ++i) sipround();
        v0 ^= m;
    }
    uint64_t b = static_cast<uint64_t>(len) << 56;
    switch (len & 7) {
        case 7: b |= static_cast<uint64_t>(data[6]) << 48; [[fallthrough]];
        case 6: b |= static_cast<uint64_t>(data[5]) << 40; [[fallthrough]];
        case 5: b |= static_cast<uint64_t>(data[4]) << 32; [[fallthrough]];
        case 4: b |= static_cast<uint64_t>(data[3]) << 24; [[fallthrough]];
        case 3: b |= static_cast<uint64_t>(data[2]) << 16; [[fallthrough]];
        case 2: b |= static_cast<uint64_t>(data[1]) << 8;  [[fallthrough]];
        case 1: b |= static_cast<uint64_t>(data[0]); break;
        case 0: break;
    }
    v3 ^= b;
    for (int i = 0; i < 2; ++i) sipround();
    v0 ^= b;
    v2 ^= 0xff;
    for (int i = 0; i < 4; ++i) sipround();
    return (v0 ^ v1) ^ (v2 ^ v3);
}

// Streaming zero-copy SipHash-2-4 sobre cabecera inmutable [0..48) + payload (48 % 8 == 0)
inline uint64_t siphash24_slab_u64(
    const uint8_t key[16],
    const uint8_t* hdr48,
    const uint8_t* payload,
    size_t payload_bytes
) {
    auto rotl64 = [](uint64_t x, int b) -> uint64_t { return (x << b) | (x >> (64 - b)); };
    auto read_le64 = [](const uint8_t* p) -> uint64_t {
        uint64_t v = 0;
        for (int i = 0; i < 8; ++i) v |= static_cast<uint64_t>(p[i]) << (8 * i);
        return v;
    };
    uint64_t k0 = read_le64(key);
    uint64_t k1 = read_le64(key + 8);
    uint64_t v0 = 0x736f6d6570736575ULL ^ k0;
    uint64_t v1 = 0x646f72616e646f6dULL ^ k1;
    uint64_t v2 = 0x6c7967656e657261ULL ^ k0;
    uint64_t v3 = 0x7465646279746573ULL ^ k1;
    auto sipround = [&]() {
        v0 += v1; v1 = rotl64(v1, 13); v1 ^= v0; v0 = rotl64(v0, 32);
        v2 += v3; v3 = rotl64(v3, 16); v3 ^= v2;
        v0 += v3; v3 = rotl64(v3, 21); v3 ^= v0;
        v2 += v1; v1 = rotl64(v1, 17); v1 ^= v2; v2 = rotl64(v2, 32);
    };
    for (size_t off = 0; off < 48; off += 8) {
        uint64_t m = read_le64(hdr48 + off);
        v3 ^= m;
        for (int i = 0; i < 2; ++i) sipround();
        v0 ^= m;
    }
    const size_t total_len = 48 + (payload ? payload_bytes : 0);
    if (payload && payload_bytes > 0) {
        const uint8_t* p = payload;
        const uint8_t* end = p + (payload_bytes & ~static_cast<size_t>(7));
        for (; p < end; p += 8) {
            uint64_t m = read_le64(p);
            v3 ^= m;
            for (int i = 0; i < 2; ++i) sipround();
            v0 ^= m;
        }
        uint64_t b = static_cast<uint64_t>(total_len) << 56;
        switch (payload_bytes & 7) {
            case 7: b |= static_cast<uint64_t>(p[6]) << 48; [[fallthrough]];
            case 6: b |= static_cast<uint64_t>(p[5]) << 40; [[fallthrough]];
            case 5: b |= static_cast<uint64_t>(p[4]) << 32; [[fallthrough]];
            case 4: b |= static_cast<uint64_t>(p[3]) << 24; [[fallthrough]];
            case 3: b |= static_cast<uint64_t>(p[2]) << 16; [[fallthrough]];
            case 2: b |= static_cast<uint64_t>(p[1]) << 8;  [[fallthrough]];
            case 1: b |= static_cast<uint64_t>(p[0]); break;
            case 0: break;
        }
        v3 ^= b;
        for (int i = 0; i < 2; ++i) sipround();
        v0 ^= b;
    } else {
        uint64_t b = static_cast<uint64_t>(total_len) << 56;
        v3 ^= b;
        for (int i = 0; i < 2; ++i) sipround();
        v0 ^= b;
    }
    v2 ^= 0xff;
    for (int i = 0; i < 4; ++i) sipround();
    return (v0 ^ v1) ^ (v2 ^ v3);
}

inline void sha256_bytes(const uint8_t* data, size_t len, uint8_t out32[32]) {
    static constexpr uint32_t K[64] = {
        0x428a2f98U,0x71374491U,0xb5c0fbcfU,0xe9b5dba5U,0x3956c25bU,0x59f111f1U,0x923f82a4U,0xab1c5ed5U,
        0xd807aa98U,0x12835b01U,0x243185beU,0x550c7dc3U,0x72be5d74U,0x80deb1feU,0x9bdc06a7U,0xc19bf174U,
        0xe49b69c1U,0xefbe4786U,0x0fc19dc6U,0x240ca1ccU,0x2de92c6fU,0x4a7484aaU,0x5cb0a9dcU,0x76f988daU,
        0x983e5152U,0xa831c66dU,0xb00327c8U,0xbf597fc7U,0xc6e00bf3U,0xd5a79147U,0x06ca6351U,0x14292967U,
        0x27b70a85U,0x2e1b2138U,0x4d2c6dfcU,0x53380d13U,0x650a7354U,0x766a0abbU,0x81c2c92eU,0x92722c85U,
        0xa2bfe8a1U,0xa81a664bU,0xc24b8b70U,0xc76c51a3U,0xd192e819U,0xd6990624U,0xf40e3585U,0x106aa070U,
        0x19a4c116U,0x1e376c08U,0x2748774cU,0x34b0bcb5U,0x391c0cb3U,0x4ed8aa4aU,0x5b9cca4fU,0x682e6ff3U,
        0x748f82eeU,0x78a5636fU,0x84c87814U,0x8cc70208U,0x90befffaU,0xa4506cebU,0xbef9a3f7U,0xc67178f2U
    };
    uint32_t state[8] = {
        0x6a09e667U,0xbb67ae85U,0x3c6ef372U,0xa54ff53aU,
        0x510e527fU,0x9b05688cU,0x1f83d9abU,0x5be0cd19U
    };
    auto rotr = [](uint32_t x, int n) -> uint32_t { return (x >> n) | (x << (32 - n)); };
    auto transform = [&](const uint8_t blk[64]) {
        uint32_t w[64];
        for (int i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(blk[4*i]) << 24) |
                   (static_cast<uint32_t>(blk[4*i+1]) << 16) |
                   (static_cast<uint32_t>(blk[4*i+2]) << 8) |
                   static_cast<uint32_t>(blk[4*i+3]);
        }
        for (int i = 16; i < 64; ++i) {
            uint32_t s0 = rotr(w[i-15], 7) ^ rotr(w[i-15], 18) ^ (w[i-15] >> 3);
            uint32_t s1 = rotr(w[i-2], 17) ^ rotr(w[i-2], 19) ^ (w[i-2] >> 10);
            w[i] = w[i-16] + s0 + w[i-7] + s1;
        }
        uint32_t a=state[0], b=state[1], c=state[2], d=state[3], e=state[4], f=state[5], g=state[6], h=state[7];
        for (int i = 0; i < 64; ++i) {
            uint32_t S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
            uint32_t ch = (e & f) ^ ((~e) & g);
            uint32_t tmp1 = h + S1 + ch + K[i] + w[i];
            uint32_t S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
            uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
            uint32_t tmp2 = S0 + maj;
            h = g; g = f; f = e; e = d + tmp1;
            d = c; c = b; b = a; a = tmp1 + tmp2;
        }
        state[0]+=a; state[1]+=b; state[2]+=c; state[3]+=d;
        state[4]+=e; state[5]+=f; state[6]+=g; state[7]+=h;
        explicit_zeroize(w, sizeof(w));
    };

    uint8_t buf[64];
    size_t blen = 0;
    for (size_t i = 0; i < len; ++i) {
        buf[blen++] = data[i];
        if (blen == 64) {
            transform(buf);
            blen = 0;
        }
    }
    buf[blen++] = 0x80;
    if (blen > 56) {
        while (blen < 64) buf[blen++] = 0;
        transform(buf);
        blen = 0;
    }
    while (blen < 56) buf[blen++] = 0;
    uint64_t bitlen = static_cast<uint64_t>(len) * 8ULL;
    for (int i = 0; i < 8; ++i) {
        buf[56 + i] = static_cast<uint8_t>((bitlen >> (56 - 8 * i)) & 0xFFU);
    }
    transform(buf);
    for (int i = 0; i < 8; ++i) {
        out32[4*i]   = static_cast<uint8_t>((state[i] >> 24) & 0xFFU);
        out32[4*i+1] = static_cast<uint8_t>((state[i] >> 16) & 0xFFU);
        out32[4*i+2] = static_cast<uint8_t>((state[i] >> 8) & 0xFFU);
        out32[4*i+3] = static_cast<uint8_t>(state[i] & 0xFFU);
    }
    explicit_zeroize(buf, sizeof(buf));
    explicit_zeroize(state, sizeof(state));
}

inline bool fill_csprng_bytes(uint8_t* dst, size_t len) {
    if (!dst || len == 0) return false;
#if defined(_WIN32)
    return BCryptGenRandom(NULL, dst, static_cast<ULONG>(len), BCRYPT_USE_SYSTEM_PREFERRED_RNG) == 0;
#else
    int rfd = open("/dev/urandom", O_RDONLY | O_CLOEXEC);
    if (rfd < 0) return false;
    size_t got = 0;
    while (got < len) {
        ssize_t n = read(rfd, dst + got, len - got);
        if (n > 0) {
            got += static_cast<size_t>(n);
        } else if (n < 0 && errno == EINTR) {
            continue;
        } else {
            close(rfd);
            return false;
        }
    }
    close(rfd);
    return true;
#endif
}

inline bool constant_time_eq64(uint64_t a, uint64_t b) {
    volatile uint64_t va = a;
    volatile uint64_t vb = b;
    return (va ^ vb) == 0ULL;
}

inline void get_process_key16(uint8_t out_k16[16]) {
    char key_buf[512] = {};
    bool has_env = false;
    size_t key_len = 0;
#if defined(_WIN32)
    size_t env_len = 0;
    if (getenv_s(&env_len, key_buf, sizeof(key_buf), "PMTP_SHM_KEY") == 0 && env_len > 1) {
        key_len = env_len - 1;
        has_env = true;
    }
#else
    const char* env_key = std::getenv("PMTP_SHM_KEY");
    if (env_key && env_key[0] != '\0') {
        key_len = (std::min)(std::strlen(env_key), sizeof(key_buf));
        std::memcpy(key_buf, env_key, key_len);
        has_env = true;
    }
#endif
    if (has_env) {
        uint8_t digest[32] = {};
        sha256_bytes(reinterpret_cast<const uint8_t*>(key_buf), key_len, digest);
        std::memcpy(out_k16, digest, 16);
        explicit_zeroize(digest, sizeof(digest));
        explicit_zeroize(key_buf, sizeof(key_buf));
        return;
    }
    explicit_zeroize(key_buf, sizeof(key_buf));

    static std::array<uint8_t, 16> s_ephem_k16{};
    static bool s_csprng_ok = false;
    static std::once_flag s_init_flag;
    std::call_once(s_init_flag, [&]() {
        s_csprng_ok = fill_csprng_bytes(s_ephem_k16.data(), s_ephem_k16.size());
    });
    if (!s_csprng_ok) {
        std::abort(); // Fail-closed: no hay fuente CSPRNG para clave efimera
    }
    std::memcpy(out_k16, s_ephem_k16.data(), 16);
}

// PRF criptografica keyed SipHash-2-4 (64-bit) sobre cabecera inmutable [0..48) + payload
inline uint64_t compute_slab_mac64(const AtelierSlabHeader& hdr, const double* payload, size_t elems) {
    uint8_t k16[16] = {};
    get_process_key16(k16);
    uint64_t tag64 = siphash24_slab_u64(
        k16,
        reinterpret_cast<const uint8_t*>(&hdr),
        reinterpret_cast<const uint8_t*>(payload),
        payload ? (elems * sizeof(double)) : 0
    );
    explicit_zeroize(k16, sizeof(k16));
    return tag64;
}

// Validacion estricta anti-fuzzing de cabecera ABI versionada y limites de memoria
inline bool validate_slab_header(
    const void* raw_slab,
    size_t mapped_bytes,
    bool verify_mac = true
) {
    if (!raw_slab || mapped_bytes < sizeof(AtelierSlabHeader)) {
        return false;
    }
    AtelierSlabHeader hdr;
    std::memcpy(&hdr, raw_slab, sizeof(AtelierSlabHeader));

    if (hdr.magic != PMTP_MAGIC_ATELIER) return false;
    if (hdr.version < PMTP_ABI_MIN_VERSION || hdr.version > PMTP_ABI_MAX_VERSION) return false;
    if (hdr.D == 0 || hdr.D > PMTP_MAX_DIM_D) return false;
    if (hdr.k == 0 || hdr.k > hdr.D || hdr.k > PMTP_MAX_RANK_K) return false;
    if ((hdr.sequence & 1ULL) != 0ULL) return false; // Seqlock write in progress
    if (!std::isfinite(hdr.isometry_error) || hdr.isometry_error < 0.0) return false;
    if (!std::isfinite(hdr.latency_us) || hdr.latency_us < 0.0) return false;

    uint64_t elems = static_cast<uint64_t>(hdr.D) * static_cast<uint64_t>(hdr.k);
    uint64_t avail_payload_bytes = static_cast<uint64_t>(mapped_bytes - sizeof(AtelierSlabHeader));
    if (elems > avail_payload_bytes / sizeof(double)) {
        return false; // Anti-overflow / OOB read
    }

    if (verify_mac) {
        const double* payload = reinterpret_cast<const double*>(
            static_cast<const uint8_t*>(raw_slab) + sizeof(AtelierSlabHeader)
        );
        uint64_t expected = compute_slab_mac64(hdr, payload, static_cast<size_t>(elems));
        if (!constant_time_eq64(expected, hdr.mac64)) return false;
    }
    return true;
}

inline void matrix_transpose_mult(const double* A, const double* B, double* C, uint32_t D, uint32_t k) {
    for (uint32_t i = 0; i < k; ++i) {
        for (uint32_t j = 0; j < k; ++j) {
            double sum = 0.0;
            double comp = 0.0;
            for (uint32_t d = 0; d < D; ++d) {
                neumaier_accumulate(A[d * k + i] * B[d * k + j], sum, comp);
            }
            C[i * k + j] = sum + comp;
        }
    }
}

inline double compute_stiefel_defect(const double* Z, uint32_t D, uint32_t k) {
    std::vector<double> G(static_cast<size_t>(k) * k, 0.0);
    matrix_transpose_mult(Z, Z, G.data(), D, k);
    double max_defect = 0.0;
    for (uint32_t i = 0; i < k; ++i) {
        for (uint32_t j = 0; j < k; ++j) {
            double target = (i == j) ? 1.0 : 0.0;
            double diff = std::abs(G[i * k + j] - target);
            if (!std::isfinite(diff)) return std::numeric_limits<double>::infinity();
            if (diff > max_defect) max_defect = diff;
        }
    }
    return max_defect;
}

// Cholesky L * L^T = A (k x k SPD). Retorna false si no es SPD.
inline bool cholesky_decompose(const std::vector<double>& A, std::vector<double>& L, uint32_t k) {
    L.assign(static_cast<size_t>(k) * k, 0.0);
    for (uint32_t i = 0; i < k; ++i) {
        for (uint32_t j = 0; j <= i; ++j) {
            double sum = 0.0, comp = 0.0;
            for (uint32_t p = 0; p < j; ++p) {
                neumaier_accumulate(L[i * k + p] * L[j * k + p], sum, comp);
            }
            double val = A[i * k + j] - (sum + comp);
            if (i == j) {
                if (val <= 1e-18 || !std::isfinite(val)) return false;
                L[i * k + i] = std::sqrt(val);
            } else {
                L[i * k + j] = val / L[j * k + j];
            }
        }
    }
    return true;
}

// Resuelve (L * L^T) * X^T = Q^T => retorna W = Q * (L * L^T)^{-1} en Q_out (D x k)
inline void cholesky_solve_right(
    const double* Q,
    const std::vector<double>& L,
    double* Q_out,
    uint32_t D,
    uint32_t k
) {
    std::vector<double> y(k);
    std::vector<double> x(k);
    for (uint32_t d = 0; d < D; ++d) {
        // Forward substitution: L * y = row_d(Q)
        for (uint32_t i = 0; i < k; ++i) {
            double sum = 0.0, comp = 0.0;
            for (uint32_t j = 0; j < i; ++j) {
                neumaier_accumulate(L[i * k + j] * y[j], sum, comp);
            }
            y[i] = (Q[d * k + i] - (sum + comp)) / L[i * k + i];
        }
        // Backward substitution: L^T * x = y
        for (int ii = static_cast<int>(k) - 1; ii >= 0; --ii) {
            uint32_t i = static_cast<uint32_t>(ii);
            double sum = 0.0, comp = 0.0;
            for (uint32_t j = i + 1; j < k; ++j) {
                neumaier_accumulate(L[j * k + i] * x[j], sum, comp);
            }
            x[i] = (y[i] - (sum + comp)) / L[i * k + i];
            Q_out[d * k + i] = x[i];
        }
    }
}

// Factor QR reducido en sitio con Re-ortogonalizacion Modificada Gram-Schmidt (MGS-2)
inline bool mgs_qr(std::vector<double>& Q_mat, std::vector<double>& R_mat, uint32_t rows, uint32_t cols) {
    R_mat.assign(static_cast<size_t>(cols) * cols, 0.0);
    for (uint32_t j = 0; j < cols; ++j) {
        for (int pass = 0; pass < 2; ++pass) {
            for (uint32_t i = 0; i < j; ++i) {
                double dot_s = 0.0, dot_c = 0.0;
                for (uint32_t r = 0; r < rows; ++r) {
                    neumaier_accumulate(Q_mat[r * cols + i] * Q_mat[r * cols + j], dot_s, dot_c);
                }
                double rij = dot_s + dot_c;
                R_mat[i * cols + j] += rij;
                for (uint32_t r = 0; r < rows; ++r) {
                    Q_mat[r * cols + j] -= rij * Q_mat[r * cols + i];
                }
            }
        }
        double nrm_s = 0.0, nrm_c = 0.0;
        for (uint32_t r = 0; r < rows; ++r) {
            double v = Q_mat[r * cols + j];
            neumaier_accumulate(v * v, nrm_s, nrm_c);
        }
        double nrm = std::sqrt(nrm_s + nrm_c);
        if (!std::isfinite(nrm) || nrm <= 1e-18) return false;
        R_mat[j * cols + j] = nrm;
        double inv = 1.0 / nrm;
        for (uint32_t r = 0; r < rows; ++r) {
            Q_mat[r * cols + j] *= inv;
        }
    }
    return true;
}

// Fallback Modified Gram-Schmidt QR (MGS-2) para ortogonalizacion sin LAPACK externo
inline double retract_qr_fallback(double* Z, uint32_t D, uint32_t k) {
    std::vector<double> Q(Z, Z + static_cast<size_t>(D) * k);
    std::vector<double> R;
    if (!mgs_qr(Q, R, D, k)) {
        return std::numeric_limits<double>::infinity();
    }
    std::memcpy(Z, Q.data(), static_cast<size_t>(D) * k * sizeof(double));
    return compute_stiefel_defect(Z, D, k);
}

// ============================================================================
// SOLVER POLAR PRINCIPAL: QDWH (Nakatsukasa, Bai & Gygi 2010)
// Convergencia cubica (<= 6-8 pasos) con conmutacion QR (c>100) / Cholesky (c<=100)
// Fallback determinista solamente ante anomalia numerica / mal condicionamiento
// ============================================================================
inline double retract_stiefel_qdwh(
    double* Z,
    uint32_t D,
    uint32_t k,
    uint32_t max_iters = 8,
    uint32_t* iters_used = nullptr,
    PolarSolverUsed* solver_used = nullptr
) {
    if (!Z || D == 0 || k == 0 || k > D) {
        if (solver_used) *solver_used = PolarSolverUsed::REJECTED_INVALID;
        return std::numeric_limits<double>::infinity();
    }

    size_t n_elems = static_cast<size_t>(D) * k;
    for (size_t idx = 0; idx < n_elems; ++idx) {
        if (!std::isfinite(Z[idx])) {
            if (solver_used) *solver_used = PolarSolverUsed::REJECTED_INVALID;
            return std::numeric_limits<double>::infinity();
        }
    }

    // 1. Cota espectral superior sin SVD: ||Z||_2 <= min(||Z||_F, sqrt(||Z||_1 * ||Z||_inf))
    double fro_sq = 0.0, fro_c = 0.0;
    std::vector<double> col_l1(k, 0.0);
    double max_row_l1 = 0.0;
    for (uint32_t d = 0; d < D; ++d) {
        double row_sum = 0.0;
        for (uint32_t j = 0; j < k; ++j) {
            double v = Z[d * k + j];
            neumaier_accumulate(v * v, fro_sq, fro_c);
            double av = std::abs(v);
            col_l1[j] += av;
            row_sum += av;
        }
        if (row_sum > max_row_l1) max_row_l1 = row_sum;
    }
    double fro_norm = std::sqrt(fro_sq + fro_c);
    if (!std::isfinite(fro_norm) || fro_norm <= 1e-300) {
        if (solver_used) *solver_used = PolarSolverUsed::REJECTED_INVALID;
        return std::numeric_limits<double>::infinity();
    }
    double max_col_l1 = *std::max_element(col_l1.begin(), col_l1.end());
    double spec_bound = std::sqrt(max_col_l1 * max_row_l1);
    double alpha = std::min(fro_norm, spec_bound) * 1.000001;

    std::vector<double> Q(n_elems);
    double inv_alpha = 1.0 / alpha;
    for (size_t i = 0; i < n_elems; ++i) {
        Q[i] = Z[i] * inv_alpha;
    }

    // Estimacion rapida de cota inferior L0 <= sigma_min(Q) via potencia inversa en factor Cholesky (k x k)
    double L = 1.0 / std::max(10.0 * static_cast<double>(k), 1e2);
    {
        std::vector<double> G(static_cast<size_t>(k) * k, 0.0);
        matrix_transpose_mult(Q.data(), Q.data(), G.data(), D, k);
        std::vector<double> L_chol;
        if (cholesky_decompose(G, L_chol, k)) {
            std::vector<double> v(k, 0.0), y(k, 0.0), z(k, 0.0);
            for (uint32_t i = 0; i < k; ++i) v[i] = (i % 2 == 0 ? 1.0 : -0.7) / std::sqrt(static_cast<double>(k));
            double sigma_min_est = 1e-6;
            for (int step = 0; step < 3; ++step) {
                for (uint32_t i = 0; i < k; ++i) {
                    double s = 0.0, c_acc = 0.0;
                    for (uint32_t j = 0; j < i; ++j) neumaier_accumulate(L_chol[i * k + j] * y[j], s, c_acc);
                    y[i] = (v[i] - (s + c_acc)) / L_chol[i * k + i];
                }
                for (int ii = static_cast<int>(k) - 1; ii >= 0; --ii) {
                    uint32_t i = static_cast<uint32_t>(ii);
                    double s = 0.0, c_acc = 0.0;
                    for (uint32_t j = i + 1; j < k; ++j) neumaier_accumulate(L_chol[j * k + i] * z[j], s, c_acc);
                    z[i] = (y[i] - (s + c_acc)) / L_chol[i * k + i];
                }
                double n2 = 0.0;
                for (double val : z) n2 += val * val;
                if (!std::isfinite(n2) || n2 <= 0.0) break;
                double inv_s = std::sqrt(n2);
                sigma_min_est = 1.0 / std::sqrt(inv_s);
                double inv_n = 1.0 / inv_s;
                for (uint32_t i = 0; i < k; ++i) v[i] = z[i] * inv_n;
            }
            L = std::clamp(0.8 * sigma_min_est, 1e-8, 0.999);
        }
    }

    std::vector<double> Q_next(n_elems);
    std::vector<double> G(static_cast<size_t>(k) * k);
    std::vector<double> Z_mat(static_cast<size_t>(k) * k);
    std::vector<double> L_chol;
    std::vector<double> W_solve(n_elems);

    uint32_t it = 0;
    double defect = std::numeric_limits<double>::infinity();
    bool qdwh_converged = false;

    for (it = 1; it <= max_iters; ++it) {
        double L2 = L * L;
        double dd = std::cbrt(4.0 * (1.0 - L2) / (L2 * L2));
        double sqd = std::sqrt(1.0 + dd);
        double term = 8.0 - 4.0 * dd + (8.0 * (2.0 - L2)) / (L2 * L2 * sqd);
        double a = sqd + 0.5 * std::sqrt(std::max(0.0, term));
        double b = (a - 1.0) * (a - 1.0) * 0.25;
        double c = a + b - 1.0;
        L = std::min(1.0, L * (a + b * L2) / (1.0 + c * L2));

        bool step_ok = false;
        if (c <= 100.0) {
            matrix_transpose_mult(Q.data(), Q.data(), G.data(), D, k);
            for (uint32_t i = 0; i < k; ++i) {
                for (uint32_t j = 0; j < k; ++j) {
                    Z_mat[i * k + j] = ((i == j) ? 1.0 : 0.0) + c * G[i * k + j];
                }
            }
            if (cholesky_decompose(Z_mat, L_chol, k)) {
                cholesky_solve_right(Q.data(), L_chol, W_solve.data(), D, k);
                double coef1 = b / c;
                double coef2 = a - coef1;
                for (size_t i = 0; i < n_elems; ++i) {
                    Q_next[i] = coef1 * Q[i] + coef2 * W_solve[i];
                }
                step_ok = true;
            }
        }

        if (!step_ok) {
            // Rama QR sobre matriz apilada B = [sqrt(c)*Q; I_k] ((D+k) x k)
            uint32_t rows = D + k;
            std::vector<double> B(static_cast<size_t>(rows) * k, 0.0);
            double sc = std::sqrt(c);
            for (size_t i = 0; i < n_elems; ++i) B[i] = sc * Q[i];
            for (uint32_t j = 0; j < k; ++j) B[static_cast<size_t>(D + j) * k + j] = 1.0;
            std::vector<double> R_qr;
            if (!mgs_qr(B, R_qr, rows, k)) {
                break;
            }
            double coef1 = b / c;
            double coef2 = (a - coef1) / sc;
            for (uint32_t d = 0; d < D; ++d) {
                for (uint32_t j = 0; j < k; ++j) {
                    double s = 0.0, comp = 0.0;
                    for (uint32_t p = 0; p < k; ++p) {
                        neumaier_accumulate(B[d * k + p] * B[static_cast<size_t>(D + j) * k + p], s, comp);
                    }
                    Q_next[d * k + j] = coef1 * Q[d * k + j] + coef2 * (s + comp);
                }
            }
        }

        double diff_sq = 0.0;
        for (size_t i = 0; i < n_elems; ++i) {
            double dval = Q_next[i] - Q[i];
            diff_sq += dval * dval;
        }
        Q.swap(Q_next);
        defect = compute_stiefel_defect(Q.data(), D, k);
        if (defect <= 1e-15 && (std::sqrt(diff_sq) <= 1e-14 || L > 1.0 - 1e-13)) {
            qdwh_converged = true;
            break;
        }
    }

    if (iters_used) *iters_used = it;

    if (qdwh_converged || (std::isfinite(defect) && defect <= 1e-12)) {
        std::memcpy(Z, Q.data(), n_elems * sizeof(double));
        if (solver_used) *solver_used = PolarSolverUsed::QDWH_PRIMARY;
        return defect;
    }

    // Fallback determinista ante no convergencia de QDWH
    double fb_defect = retract_qr_fallback(Z, D, k);
    if (solver_used) *solver_used = PolarSolverUsed::MGS_QR_FALLBACK;
    return fb_defect;
}
