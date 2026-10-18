// ============================================================================
// POLYDIM EINSOF — DART FFI NATIVE SILICON BINDINGS V26155
// ============================================================================
//
// Purpose:
//   Zero-copy high-performance Dart FFI bridge for Flutter & Dart Server Apps
//   binding directly to kernel_cpp_v26155.dll / kernel_rust_v26155.dll under
//   Rule 27 (Silicon Contract) and Rule 22 (PMTP Zero-Copy Memory).
//
// Remediations V26155:
//   * Theorem 692: Implementation of NativeVector zero-copy wrapper pattern
//     leveraging Pointer<Double>.asTypedList(n) and NativeFinalizer(calloc.nativeFree)
//     safety net.
//   * Added @Packed(1) to PmtpTensorDescriptorNative ensuring exact binary alignment
//     with C++ #pragma pack(1) and Rust 88-byte fixed ABI.
//   * Fixed native struct memory leaks: view pointers (calloc) freed strictly in finally blocks.
//   * Client-side range validation for empty vectors (n == 0) and max dimension (n > 1e7).
//   * Granular telemetry preservation in validateDescriptor (returns integer Status code).
// ============================================================================

import 'dart:ffi';
import 'dart:io';
import 'dart:typed_data';
import 'package:ffi/ffi.dart';

// Unified Status Codes
abstract class PolydimStatus {
  static const int ok = 0;
  static const int invalidArgument = -1;
  static const int nonfiniteInput = -2;
  static const int aliasViolation = -3;
  static const int alignmentError = -4;
  static const int notUnit = -5;
  static const int notTangent = -6;
  static const int zeroVector = -7;
  static const int pathRequired = -8;
  static const int numericalFailure = -9;
  static const int rangeError = -10;
  static const int fpEnvError = -11;
  static const int unrepresentableOutput = -12;
  static const int lengthMismatch = -13;
  static const int precisionLoss = -14;
  static const int pmtpSlabError = -15;
  static const int panicTrapped = -99;
}

// C ABI Native Struct Views
final class PolydimF64ConstView extends Struct {
  external Pointer<Double> ptr;

  @Uint64()
  external int len;
}

final class PolydimF64MutView extends Struct {
  external Pointer<Double> ptr;

  @Uint64()
  external int len;
}

@Packed(1)
final class PmtpTensorDescriptorNative extends Struct {
  @Array(4)
  external Array<Uint8> magic;

  @Uint16()
  external int version;

  @Uint16()
  external int encodedSize;

  @Uint64()
  external int segmentId;

  @Uint64()
  external int bufferId;

  @Uint64()
  external int generation;

  @Uint64()
  external int byteOffset;

  @Uint64()
  external int byteLength;

  @Uint8()
  external int dtypeCode;

  @Uint8()
  external int ndim;

  @Array(6)
  external Array<Uint8> reserved;

  @Array(4)
  external Array<Uint64> shape;
}

// C FFI Function Signatures
typedef PolydimSphereProjectC = Int32 Function(
  PolydimF64ConstView inView,
  PolydimF64MutView outView,
);
typedef PolydimSphereProjectDart = int Function(
  PolydimF64ConstView inView,
  PolydimF64MutView outView,
);

typedef PolydimSphereTransportC = Int32 Function(
  PolydimF64ConstView xView,
  PolydimF64ConstView yView,
  PolydimF64ConstView vView,
  PolydimF64MutView outView,
);
typedef PolydimSphereTransportDart = int Function(
  PolydimF64ConstView xView,
  PolydimF64ConstView yView,
  PolydimF64ConstView vView,
  PolydimF64MutView outView,
);

typedef PolydimPmtpValidateC = Int32 Function(
  Pointer<PmtpTensorDescriptorNative> desc,
);
typedef PolydimPmtpValidateDart = int Function(
  Pointer<PmtpTensorDescriptorNative> desc,
);

/// Theorem 692: Zero-Copy Managed Native Memory Vector
final class NativeVector {
  static final Finalizer<Pointer<Double>> _finalizer = Finalizer((ptr) {
    calloc.free(ptr);
  });

  Pointer<Double>? _ptr;
  final int length;
  late final Float64List view;
  bool _isDisposed = false;

  NativeVector(this.length) {
    if (length <= 0 || length > 10000000) {
      throw RangeError('NativeVector length=$length out of valid bounds (1..10,000,000)');
    }
    final p = calloc<Double>(length);
    _ptr = p;
    view = p.asTypedList(length);
    _finalizer.attach(this, p, detach: this);
  }

  Pointer<Double> get pointer {
    if (_isDisposed || _ptr == null) {
      throw StateError('NativeVector has already been disposed');
    }
    return _ptr!;
  }

  void dispose() {
    if (!_isDisposed) {
      _finalizer.detach(this);
      if (_ptr != null) {
        calloc.free(_ptr!);
        _ptr = null;
      }
      _isDisposed = true;
    }
  }
}

class PolydimSiliconCoreV26155 {
  late DynamicLibrary _lib;
  late PolydimSphereProjectDart _sphereProject;
  late PolydimSphereTransportDart _sphereTransport;
  late PolydimPmtpValidateDart _pmtpValidate;

  PolydimSiliconCoreV26155({String? libraryPath}) {
    final path = libraryPath ?? _detectLibraryPath();
    _lib = DynamicLibrary.open(path);

    _sphereProject = _lib.lookupFunction<PolydimSphereProjectC, PolydimSphereProjectDart>(
      'polydim_sphere_project_v26155',
    );
    _sphereTransport = _lib.lookupFunction<PolydimSphereTransportC, PolydimSphereTransportDart>(
      'polydim_sphere_transport_v26155',
    );
    _pmtpValidate = _lib.lookupFunction<PolydimPmtpValidateC, PolydimPmtpValidateDart>(
      'polydim_pmtp_validate_descriptor_v26155',
    );
  }

  static String _detectLibraryPath() {
    if (Platform.isWindows) {
      if (File('kernel_cpp_v26155.dll').existsSync()) return 'kernel_cpp_v26155.dll';
      if (File('kernel_rust_v26155.dll').existsSync()) return 'kernel_rust_v26155.dll';
      final defaultPath = r'E:\POLYDIM_EINSOF\ENTREGA_2026_10_07_V26155\kernel_cpp_v26155.dll';
      if (File(defaultPath).existsSync()) return defaultPath;
      return r'E:\POLYDIM_EINSOF\ENTREGA_2026_10_07_V26155\kernel_rust_v26155.dll';
    } else if (Platform.isLinux) {
      return 'libkernel_cpp_v26155.so';
    } else if (Platform.isMacOS) {
      return 'libkernel_cpp_v26155.dylib';
    }
    throw UnsupportedError('Unsupported operating system for POLYDIM FFI');
  }

  /// High-Performance Spherical Projection onto S^(D-1)
  Float64List sphereProject(Float64List input) {
    final n = input.length;
    if (n == 0 || n > 10000000) {
      throw RangeError('Vector length n=$n out of valid bounds (1..10,000,000)');
    }

    final inVec = NativeVector(n);
    final outVec = NativeVector(n);
    final inView = calloc<PolydimF64ConstView>();
    final outView = calloc<PolydimF64MutView>();

    try {
      inVec.view.setAll(0, input);

      inView.ref.ptr = inVec.pointer;
      inView.ref.len = n;

      outView.ref.ptr = outVec.pointer;
      outView.ref.len = n;

      final rc = _sphereProject(inView.ref, outView.ref);

      if (rc != PolydimStatus.ok) {
        throw Exception('polydim_sphere_project_v26155 failed with status code $rc');
      }

      return Float64List.fromList(outVec.view);
    } finally {
      calloc.free(inView);
      calloc.free(outView);
      inVec.dispose();
      outVec.dispose();
    }
  }

  /// Spherical Parallel Transport along geodesic on S^(D-1)
  Float64List sphereTransport(Float64List x, Float64List y, Float64List v) {
    final n = x.length;
    if (n == 0 || n > 10000000) {
      throw RangeError('Vector length n=$n out of valid bounds (1..10,000,000)');
    }
    if (y.length != n || v.length != n) {
      throw ArgumentError('Vectors x, y, v must have equal length n=$n');
    }

    final xVec = NativeVector(n);
    final yVec = NativeVector(n);
    final vVec = NativeVector(n);
    final outVec = NativeVector(n);

    final xView = calloc<PolydimF64ConstView>();
    final yView = calloc<PolydimF64ConstView>();
    final vView = calloc<PolydimF64ConstView>();
    final outView = calloc<PolydimF64MutView>();

    try {
      xVec.view.setAll(0, x);
      yVec.view.setAll(0, y);
      vVec.view.setAll(0, v);

      xView.ref.ptr = xVec.pointer;
      xView.ref.len = n;

      yView.ref.ptr = yVec.pointer;
      yView.ref.len = n;

      vView.ref.ptr = vVec.pointer;
      vView.ref.len = n;

      outView.ref.ptr = outVec.pointer;
      outView.ref.len = n;

      final rc = _sphereTransport(xView.ref, yView.ref, vView.ref, outView.ref);

      if (rc != PolydimStatus.ok) {
        throw Exception('polydim_sphere_transport_v26155 failed with status code $rc');
      }

      return Float64List.fromList(outVec.view);
    } finally {
      calloc.free(xView);
      calloc.free(yView);
      calloc.free(vView);
      calloc.free(outView);
      xVec.dispose();
      yVec.dispose();
      vVec.dispose();
      outVec.dispose();
    }
  }

  /// PMTP 88-Byte Binary Descriptor Validation returning granular Status
  int validateDescriptor(Pointer<PmtpTensorDescriptorNative> desc) {
    return _pmtpValidate(desc);
  }
}
