import ctypes
import numpy as np
import time
import sys
import os

# Add MinGW bin to DLL search path for libgomp and pthreads
mingw_bin = r"E:\varios\winlibs_gcc14_zip\mingw64\bin"
if os.path.exists(mingw_bin):
    os.add_dll_directory(mingw_bin)

# Load compiled DLL
dll_path = r"E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26250\Auditoria_Externa\libpolydim_cpp_v26250.dll"
try:
    lib = ctypes.CDLL(dll_path)
except Exception as e:
    print(f"FAILED to load {dll_path}: {e}")
    sys.exit(1)

class PolydimF64ConstView(ctypes.Structure):
    _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]

class PolydimF64MutView(ctypes.Structure):
    _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]

lib.polydim_sphere_project_v26155.argtypes = [PolydimF64ConstView, PolydimF64MutView]
lib.polydim_sphere_project_v26155.restype = ctypes.c_int32

lib.polydim_sphere_transport_v26155.argtypes = [
    PolydimF64ConstView, PolydimF64ConstView, PolydimF64ConstView, PolydimF64MutView
]
lib.polydim_sphere_transport_v26155.restype = ctypes.c_int32

print("=== SILICON AUDIT SUITE: C++20 V26250 (8-WAY NEUMAIER + OPENMP) ===")

# Test 1: High Dimension D=100,000 Spherical Projection
D = 100000
x = np.random.randn(D).astype(np.float64)
out = np.zeros(D, dtype=np.float64)

in_v = PolydimF64ConstView(x.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), D)
out_v = PolydimF64MutView(out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), D)

t0 = time.perf_counter()
ret = lib.polydim_sphere_project_v26155(in_v, out_v)
t1 = time.perf_counter()

if ret != 0:
    print(f"[FAIL] Sphere project returned {ret}")
    sys.exit(1)

norm_out = np.linalg.norm(out)
diff_norm = abs(norm_out - 1.0)
print(f"[PASS] D={D} Project: Exit Code 0 | Latency: {(t1-t0)*1000:.3f} ms | ||out|| - 1 = {diff_norm:.2e}")
assert diff_norm < 1e-13, f"Norm drift: {diff_norm}"

# Test 2: Subnormal and Extreme Values
x_sub = np.full(D, 1e-305, dtype=np.float64)
out_sub = np.zeros(D, dtype=np.float64)
in_sub_v = PolydimF64ConstView(x_sub.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), D)
out_sub_v = PolydimF64MutView(out_sub.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), D)

ret = lib.polydim_sphere_project_v26155(in_sub_v, out_sub_v)
norm_sub = np.linalg.norm(out_sub)
print(f"[PASS] Subnormal 1e-305 Project: Exit Code {ret} | ||out|| - 1 = {abs(norm_sub - 1.0):.2e}")
assert ret == 0 and abs(norm_sub - 1.0) < 1e-13

# Test 3: NaN and Inf Rejection
x_nan = x.copy()
x_nan[500] = np.nan
in_nan_v = PolydimF64ConstView(x_nan.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), D)
ret = lib.polydim_sphere_project_v26155(in_nan_v, out_v)
print(f"[PASS] NaN Rejection: Exit Code {ret} (Expected POLYDIM_NONFINITE_INPUT = -2)")
assert ret == -2

# Test 4: Scale-Invariant Tangency for Small Norm (||v|| = 1e-8)
# Construct unit points x, y and tangent vector v at x
x_pt = np.random.randn(1000).astype(np.float64)
x_pt /= np.linalg.norm(x_pt)
y_pt = np.random.randn(1000).astype(np.float64)
y_pt /= np.linalg.norm(y_pt)

# Random vector orthogonalized against x_pt
v_rand = np.random.randn(1000).astype(np.float64)
v_tang = v_rand - np.dot(x_pt, v_rand) * x_pt
# Scale to small norm 1e-8
v_small = v_tang * (1e-8 / np.linalg.norm(v_tang))
out_t = np.zeros(1000, dtype=np.float64)

xv = PolydimF64ConstView(x_pt.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
yv = PolydimF64ConstView(y_pt.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
vv = PolydimF64ConstView(v_small.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
ov = PolydimF64MutView(out_t.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)

ret = lib.polydim_sphere_transport_v26155(xv, yv, vv, ov)
print(f"[PASS] Small Norm Tangency (||v||=1e-8): Exit Code {ret}")
assert ret == 0

# Check with slightly non-tangent small vector (defective tangency)
v_bad = v_small + x_pt * 1e-10  # error is 1% of ||v||
vv_bad = PolydimF64ConstView(v_bad.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
ret_bad = lib.polydim_sphere_transport_v26155(xv, yv, vv_bad, ov)
print(f"[PASS] Defective Tangency Rejection: Exit Code {ret_bad} (Expected POLYDIM_NOT_TANGENT = -6)")
assert ret_bad == -6, f"Expected -6, got {ret_bad}"

print("\nALL SILICON TESTS FOR C++20 V26250 COMPLETED WITH EXIT CODE 0.")
sys.exit(0)
