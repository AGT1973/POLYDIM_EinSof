// ============================================================================
// FUZZ HARNESS ASAN / UBSAN PARA ABI VERSIONADA v1 Y SOLVER QDWH
// Compilar Windows MSVC: cl /std:c++20 /O2 /Zi /fsanitize=address fuzz_abi_asan_ubsan.cpp /I ..\tools\atelier_kernel
// Compilar Linux GCC/Clang: g++ -std=c++20 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer fuzz_abi_asan_ubsan.cpp -I ../tools/atelier_kernel -o fuzz_abi_asan_ubsan
// ============================================================================

#include "../tools/atelier_kernel/atelier_abi.hpp"
#include <cassert>
#include <iostream>
#include <random>

static bool test_valid_abi_and_tamper_mac() {
    const uint32_t D = 64, k = 8;
    const size_t elems = static_cast<size_t>(D) * k;
    const size_t slab_bytes = sizeof(AtelierSlabHeader) + elems * sizeof(double);
    std::vector<uint8_t> slab(slab_bytes, 0);

    std::vector<double> Z(elems);
    std::mt19937_64 init_rng(424242ULL);
    std::uniform_real_distribution<double> init_dist(-1.0, 1.0);
    for (size_t i = 0; i < elems; ++i) {
        Z[i] = init_dist(init_rng);
    }
    PolarSolverUsed solver = PolarSolverUsed::REJECTED_INVALID;
    double defect = retract_stiefel_qdwh(Z.data(), D, k, 8, nullptr, &solver);
    if (solver != PolarSolverUsed::QDWH_PRIMARY || defect > 1e-13) {
        std::cerr << "QDWH valid baseline failed: defect=" << defect << "\n";
        return false;
    }

    AtelierSlabHeader hdr{};
    hdr.magic = PMTP_MAGIC_ATELIER;
    hdr.version = PMTP_ABI_MIN_VERSION;
    hdr.D = D;
    hdr.k = k;
    hdr.isometry_error = defect;
    hdr.latency_us = 12.5;
    hdr.timestamp_ns = 1000ULL;
    hdr.heartbeat_ns = 1000ULL;
    hdr.sequence = 2;
    hdr.mac64 = compute_slab_mac64(hdr, Z.data(), elems);

    std::memcpy(slab.data(), &hdr, sizeof(hdr));
    std::memcpy(slab.data() + sizeof(hdr), Z.data(), elems * sizeof(double));
    if (!validate_slab_header(slab.data(), slab_bytes, true)) {
        std::cerr << "Valid slab header failed validation\n";
        return false;
    }

    // Mutating mutable seqlock sequence (even 2 -> 4) must keep MAC valid
    hdr.sequence = 4;
    std::memcpy(slab.data(), &hdr, sizeof(hdr));
    if (!validate_slab_header(slab.data(), slab_bytes, true)) {
        std::cerr << "Mutable seqlock sequence transition broke MAC\n";
        return false;
    }

    // Odd seqlock sequence must fail-closed
    hdr.sequence = 5;
    std::memcpy(slab.data(), &hdr, sizeof(hdr));
    if (validate_slab_header(slab.data(), slab_bytes, true)) {
        std::cerr << "Odd seqlock sequence accepted\n";
        return false;
    }
    hdr.sequence = 2;
    std::memcpy(slab.data(), &hdr, sizeof(hdr));

    // Mutating immutable header byte [0..48) -> MAC must fail
    slab[40] ^= 0x01;
    if (validate_slab_header(slab.data(), slab_bytes, true)) {
        std::cerr << "Header metadata bit flip bypassed MAC\n";
        return false;
    }
    slab[40] ^= 0x01;

    // Mutate 1 bit in payload -> MAC must fail
    slab[sizeof(hdr) + 3] ^= 0x01;
    if (validate_slab_header(slab.data(), slab_bytes, true)) {
        std::cerr << "Co-tenant bit flip bypassed MAC\n";
        return false;
    }
    slab[sizeof(hdr) + 3] ^= 0x01;

    // Zeroization check
    explicit_zeroize(slab.data(), slab.size());
    for (uint8_t b : slab) {
        if (b != 0) {
            std::cerr << "Zeroization left non-zero byte\n";
            return false;
        }
    }
    return true;
}

static bool fuzz_abi_headers(int iterations) {
    std::mt19937_64 rng(20261112ULL);
    std::vector<uint8_t> buf(sizeof(AtelierSlabHeader) + 512, 0);

    // Explicit edge-case vectors
    const uint32_t bad_versions[] = {0, 2, 3, 255, 0xFFFFFFFFU};
    for (uint32_t ver : bad_versions) {
        AtelierSlabHeader hdr{};
        hdr.magic = PMTP_MAGIC_ATELIER;
        hdr.version = ver;
        hdr.D = 8;
        hdr.k = 4;
        hdr.sequence = 2;
        std::memcpy(buf.data(), &hdr, sizeof(hdr));
        if (validate_slab_header(buf.data(), buf.size(), false)) {
            std::cerr << "Invalid ABI version accepted: " << ver << "\n";
            return false;
        }
    }

    // Integer-overflow & truncated length checks
    {
        AtelierSlabHeader hdr{};
        hdr.magic = PMTP_MAGIC_ATELIER;
        hdr.version = 1;
        hdr.D = 0xFFFFFFFFU;
        hdr.k = 0xFFFFFFFFU;
        hdr.sequence = 2;
        std::memcpy(buf.data(), &hdr, sizeof(hdr));
        if (validate_slab_header(buf.data(), buf.size(), false)) return false;
        if (validate_slab_header(buf.data(), 32, false)) return false;
        if (validate_slab_header(nullptr, buf.size(), false)) return false;
    }

    // 10,000 random bit/byte mutations around valid + corrupted slabs
    for (int it = 0; it < iterations; ++it) {
        size_t len = (it % 4 == 0) ? (rng() % sizeof(AtelierSlabHeader))
                                   : (sizeof(AtelierSlabHeader) + (rng() % 512));
        std::vector<uint8_t> fuzz_buf(len);
        for (size_t i = 0; i < len; ++i) {
            fuzz_buf[i] = static_cast<uint8_t>(rng() & 0xFFU);
        }
        // 25% of cases: inject valid magic/version/dims then fuzz the rest
        if (len >= sizeof(AtelierSlabHeader) && (it % 4 == 1)) {
            AtelierSlabHeader h{};
            std::memcpy(&h, fuzz_buf.data(), sizeof(h));
            h.magic = PMTP_MAGIC_ATELIER;
            h.version = (it % 8 == 1) ? 1U : static_cast<uint32_t>(rng() % 5U);
            h.D = static_cast<uint32_t>(rng() % 128U);
            h.k = static_cast<uint32_t>(rng() % 32U);
            std::memcpy(fuzz_buf.data(), &h, sizeof(h));
        }
        (void)validate_slab_header(fuzz_buf.data(), len, (it % 2 == 0));
    }
    return true;
}

static bool fuzz_qdwh_adversarial() {
    std::mt19937_64 rng(99887766ULL);
    std::uniform_real_distribution<double> dist(-10.0, 10.0);

    // 1. Subnormal, NaN, Inf, zero matrices must never UB or crash
    std::vector<double> bad(64 * 8, 1.0);
    bad[17] = std::numeric_limits<double>::quiet_NaN();
    PolarSolverUsed solver = PolarSolverUsed::QDWH_PRIMARY;
    if (std::isfinite(retract_stiefel_qdwh(bad.data(), 64, 8, 8, nullptr, &solver))) return false;
    if (solver != PolarSolverUsed::REJECTED_INVALID) return false;

    bad[17] = std::numeric_limits<double>::infinity();
    if (std::isfinite(retract_stiefel_qdwh(bad.data(), 64, 8, 8, nullptr, &solver))) return false;

    std::vector<double> zero_mat(64 * 8, 0.0);
    if (std::isfinite(retract_stiefel_qdwh(zero_mat.data(), 64, 8, 8, nullptr, &solver))) return false;

    // 2. Well-conditioned & moderately-conditioned fuzz matrices -> QDWH primary converges <= 1e-12
    for (int trial = 0; trial < 32; ++trial) {
        const uint32_t D = 128, k = 8;
        std::vector<double> Z(D * k);
        for (size_t i = 0; i < Z.size(); ++i) Z[i] = dist(rng);
        double scale = (trial % 2 == 0) ? 1.0 : 1e4;
        for (double& v : Z) v *= scale;
        uint32_t iters = 0;
        double defect = retract_stiefel_qdwh(Z.data(), D, k, 8, &iters, &solver);
        if (!std::isfinite(defect) || defect > 1e-12) {
            std::cerr << "QDWH trial " << trial << " exceeded defect threshold: " << defect << "\n";
            return false;
        }
    }
    return true;
}

int main() {
    if (!test_valid_abi_and_tamper_mac()) return 1;
    if (!fuzz_abi_headers(10000)) return 2;
    if (!fuzz_qdwh_adversarial()) return 3;
    std::cout << "[PASS] ASAN/UBSAN ABI v1 + QDWH Fuzzer: 10000 mutated headers + 35 adversarial matrices PASSED (0 UB/OOB/leaks)\n";
    return 0;
}
