// =============================================================================
// PMTP DART FFI BINDINGS (CERTIFIED COMPATIBLE V26605)
// Unifies C++, Rust, Dart and Python with strict byte-level parity.
// =============================================================================

import 'dart:ffi';
import 'package:ffi/ffi.dart';

@Packed(1)
final class PolydimWireHeader extends Struct {
  @Uint32()
  external int magic;                // Offset  0 (4 bytes): 0x504D5450 ("PMTP")

  @Uint16()
  external int versionMajor;         // Offset  4 (2 bytes): 1

  @Uint16()
  external int versionMinor;         // Offset  6 (2 bytes): 0

  @Array(16)
  external Array<Uint8> slabUuid;    // Offset  8 (16 bytes): UUID de 128 bits

  @Uint64()
  external int numElements;          // Offset 24 (8 bytes): Cantidad de elementos

  @Uint64()
  external int payloadBytes;         // Offset 32 (8 bytes): Tamaño del payload en bytes

  @Uint64()
  external int timestampNs;          // Offset 40 (8 bytes): Marca temporal nanosegundos

  @Uint32()
  external int dtype;                // Offset 48 (4 bytes): Identificador de tipo IEEE-754

  @Double()
  external double stiefelDefect;     // Offset 52 (8 bytes): Defecto de ortogonalidad ||W^T W - I||

  @Array(32)
  external Array<Uint8> blake2sHash; // Offset 60 (32 bytes): Firma criptográfica del payload

  @Array(36)
  external Array<Uint8> reserved;    // Offset 92 (36 bytes): Espacio de expansión alineado
}

void validatePmtpAbi() {
  final headerSize = sizeOf<PolydimWireHeader>();
  assert(headerSize == 128, 
    'DESFASE CRÍTICO DE ABI: PolydimWireHeader mide $headerSize bytes en lugar de 128 bytes.');
  assert(headerSize % 64 == 0, 
    'ALINEACIÓN INVÁLIDA: PolydimWireHeader debe ser múltiplo exacto de 64 bytes.');
}

// =============================================================================
// FIRMAS NATIVAS C-ABI PARA LIBPMTP_CORE / PMTP_KERNEL_CPP_V26600
// =============================================================================

typedef PmtpShmCreateNative = Pointer<Void> Function(
  Pointer<Utf8> name,
  Uint32 slabId,
  Uint64 numElements,
  Uint16 dtypeId
);
typedef PmtpShmCreateDart = Pointer<Void> Function(
  Pointer<Utf8> name,
  int slabId,
  int numElements,
  int dtypeId
);

typedef PmtpShmOpenNative = Pointer<Void> Function(
  Pointer<Utf8> name,
  Uint32 slabId,
  Uint64 numElements,
  Uint16 dtypeId
);
typedef PmtpShmOpenDart = Pointer<Void> Function(
  Pointer<Utf8> name,
  int slabId,
  int numElements,
  int dtypeId
);

typedef PmtpShmPublishAtomicNative = Int32 Function(
  Pointer<Void> handle,
  Pointer<Void> data,
  Uint64 numElements,
  Double scale
);
typedef PmtpShmPublishAtomicDart = int Function(
  Pointer<Void> handle,
  Pointer<Void> data,
  int numElements,
  double scale
);

typedef PmtpShmAcquireLeaseNative = Int32 Function(
  Pointer<Void> handle,
  Uint32 slot,
  Pointer<Uint64> outGeneration
);
typedef PmtpShmAcquireLeaseDart = int Function(
  Pointer<Void> handle,
  int slot,
  Pointer<Uint64> outGeneration
);

typedef PmtpShmReleaseLeaseNative = Int32 Function(
  Pointer<Void> handle,
  Uint32 slot
);
typedef PmtpShmReleaseLeaseDart = int Function(
  Pointer<Void> handle,
  int slot
);

typedef PmtpShmReadLeasedNative = Int32 Function(
  Pointer<Void> handle,
  Pointer<Void> outBuffer,
  Uint64 bufferCapacityBytes,
  Pointer<Uint32> outSlot,
  Pointer<Uint64> outGeneration
);
typedef PmtpShmReadLeasedDart = int Function(
  Pointer<Void> handle,
  Pointer<Void> outBuffer,
  int bufferCapacityBytes,
  Pointer<Uint32> outSlot,
  Pointer<Uint64> outGeneration
);

typedef PmtpShmCloseNative = Void Function(
  Pointer<Void> handle
);
typedef PmtpShmCloseDart = void Function(
  Pointer<Void> handle
);
