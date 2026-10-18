import numpy as np
import math
import sys
import os

# Import monolito
sys.path.insert(0, r"E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26250\Auditoria_Externa")
import polydim_v26250_monolito as mono

print("=== SILICON AUDIT SUITE: MONOLITO & PMTP V26250 ===")

# Test 1: P-02 Invalid dtype rejection
try:
    desc = mono.PmtpTensorDescriptor(shape=(10,), dtype_code=7)
    print("[FAIL] P-02: Accepted dtype_code=7")
    sys.exit(1)
except ValueError as e:
    print(f"[PASS] P-02: Successfully rejected invalid dtype_code=7: {e}")

# Test 2: P-03 64-bit overflow rejection
try:
    desc = mono.PmtpTensorDescriptor(shape=(10,), byte_offset=(1 << 64) - 10, byte_length=100)
    print("[FAIL] P-03: Accepted 64-bit overflow")
    sys.exit(1)
except ValueError as e:
    print(f"[PASS] P-03: Successfully rejected 64-bit overflow: {e}")

# Test 3: P-01 HMAC 120-byte Wire Descriptor
session_key = b"polydim_secure_session_key_2026"
desc_valid = mono.PmtpTensorDescriptor(shape=(10,), byte_offset=0, byte_length=80, dtype_code=1)
wire_120 = desc_valid.pack(session_key=session_key)
assert len(wire_120) == 120, f"Expected 120 bytes, got {len(wire_120)}"

# Unpack with correct key
unpacked = mono.PmtpTensorDescriptor.unpack(wire_120, session_key=session_key)
assert unpacked.shape == (10,)
print(f"[PASS] P-01: Successfully packed and unpacked 120-byte HMAC wire descriptor")

# Unpack with forged HMAC
forged = bytearray(wire_120)
forged[90] ^= 0xFF
try:
    mono.PmtpTensorDescriptor.unpack(bytes(forged), session_key=session_key)
    print("[FAIL] P-01: Accepted forged HMAC")
    sys.exit(1)
except ValueError as e:
    print(f"[PASS] P-01: Successfully rejected forged HMAC in 120-byte descriptor: {e}")

# Test 4: P-04 AnchoredArray slicing preserves _slab_owner
alloc = mono.PmtpSlabAllocator("test_slab_anchor_v26250", 1024, create=True)
try:
    arr = alloc.as_ndarray(shape=(4, 4), dtype=np.float64)
    assert arr._slab_owner is alloc
    sliced = arr[0:2, :]
    assert hasattr(sliced, "_slab_owner") and sliced._slab_owner is alloc, "Slicing lost _slab_owner!"
    print(f"[PASS] P-04: AnchoredArray slice preserved _slab_owner successfully")
finally:
    alloc.close()

# Test 5: P-11 Step overflow handling
orch = mono.PolydimOrchestratorV26250()
X = np.eye(4, 2, dtype=np.float64)
Z = np.zeros((4, 2), dtype=np.float64)
status, _, meta = orch.retract_stiefel(X, Z, step=10**1000)
assert status == mono.Status.INVALID_ARGUMENT, f"Expected INVALID_ARGUMENT, got {status}"
print(f"[PASS] P-11: step=10**1000 returned Status.INVALID_ARGUMENT without unhandled OverflowError")

# Test 6: P-08 Asymptotic Cayley Reflector
Z_tangent = np.zeros((4, 2), dtype=np.float64)
Z_tangent[2, 0] = 1.0
Z_tangent[3, 1] = 1.0
status, out_inf, meta_inf = orch.retract_stiefel(X, Z_tangent, step=1e308)
assert status == mono.Status.OK, f"Expected Status.OK, got {status} ({meta_inf})"
ortho_defect = np.max(np.abs(out_inf.T @ out_inf - np.eye(2)))
assert ortho_defect < 1e-12, f"Ortho defect: {ortho_defect}"
print(f"[PASS] P-08: Exact Asymptotic Cayley Reflector verified: ortho defect = {ortho_defect:.2e}")

# Test 7: P-10 Polar Frobenius SVD
M_random = np.random.randn(4, 2)
Q_p = orch.polar_qr_reanchor(M_random)
ortho_p = np.max(np.abs(Q_p.T @ Q_p - np.eye(2)))
assert ortho_p < 1e-12
print(f"[PASS] P-10: Polar Frobenius SVD produced exact isometry: ortho defect = {ortho_p:.2e}")

print("\nALL SILICON TESTS FOR MONOLITO & PMTP V26250 COMPLETED WITH EXIT CODE 0.")
sys.exit(0)
