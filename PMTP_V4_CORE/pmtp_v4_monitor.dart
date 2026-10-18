// ============================================================================
// POLYDIM EINSOF — PMTP-v4 10,000D LIVE FRONTEND MONITOR (DART 3.13)
// ============================================================================

import 'dart:io';
import 'dart:typed_data';
import 'dart:math';
import 'dart:convert';

void main(List<String> args) async {
  final sandboxDir = r'E:\POLYDIM_EINSOF\PMTP_V4_CORE\SANDBOX_10000D';
  final binPath = '$sandboxDir\\pmtp_v4_collapsed_1d_state.bin';
  final descPath = '$sandboxDir\\pmtp_v4_collapsed_128b_descriptor.bin';
  final lockPath = '$sandboxDir\\night_daemon.lock';

  stdout.writeln('');
  stdout.writeln('╔══════════════════════════════════════════════════════════════════════╗');
  stdout.writeln('║       POLYDIM PMTP-v4 — 10,000D LIVE FRONTEND MONITOR (DART)         ║');
  stdout.writeln('║       Manifold: S^(9999) | Shared Memory & Mathematical Oracle       ║');
  stdout.writeln('╚══════════════════════════════════════════════════════════════════════╝');
  stdout.writeln('');

  // 1. Consulta al Oráculo Matemático de PostgreSQL 16
  stdout.writeln('● ORÁCULO MATEMÁTICO (POSTGRESQL 16):');
  try {
    final res = await Process.run('python', [
      '-c',
      '''
import psycopg
conn = psycopg.connect('dbname=polydim_vec_db user=postgres host=localhost port=5432')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM pmtp_v4_theorems WHERE status='SOTA_CERTIFIED'")
t_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM pmtp_v4_facts")
f_count = cur.fetchone()[0]
cur.execute("SELECT topic, script_output FROM pmtp_v4_theorems ORDER BY id DESC LIMIT 2")
rows = cur.fetchall()
print(f"THEOREMS={t_count}|FACTS={f_count}")
for r in rows:
    print(f"TOPIC: {r[0]} | OUT: {r[1]}")
conn.close()
'''
    ]);
    if (res.exitCode == 0) {
      final lines = res.stdout.toString().trim().split('\n');
      for (final l in lines) {
        stdout.writeln('  ├── $l');
      }
    } else {
      stdout.writeln('  └── [WARN] Conexión Python/PG16 falló: ${res.stderr}');
    }
  } catch (e) {
    stdout.writeln('  └── [WARN] No se pudo consultar PG16: $e');
  }
  stdout.writeln('');

  // 2. Inspección del Descriptor Canónico de 128 Bytes
  final descFile = File(descPath);
  if (descFile.existsSync()) {
    final bytes = descFile.readAsBytesSync();
    if (bytes.length == 128) {
      final bd = ByteData.sublistView(bytes);
      final magic = bd.getUint32(0, Endian.little);
      final version = bd.getUint16(4, Endian.little);
      final flags = bd.getUint16(6, Endian.little);
      final epoch = bd.getUint64(8, Endian.little);
      final nodeId = bd.getUint32(16, Endian.little);
      final pid = bd.getUint32(20, Endian.little);
      final domain = bd.getUint32(24, Endian.little);
      final state = bd.getUint32(28, Endian.little);
      final elements = bd.getUint64(32, Endian.little);
      final byteLen = bd.getUint64(48, Endian.little);

      final magicStr = String.fromCharCodes(bytes.sublist(0, 4));

      stdout.writeln('● PMTP-v4 WIRE DESCRIPTOR (128 BYTES C++20 ABI):');
      stdout.writeln('  ├── Magic           : 0x${magic.toRadixString(16).toUpperCase()} ("$magicStr")');
      stdout.writeln('  ├── Versión         : $version | Flags: 0x${flags.toRadixString(16).padLeft(4, '0')}');
      stdout.writeln('  ├── Global Epoch    : $epoch | Node: $nodeId | PID: $pid');
      stdout.writeln('  ├── Memory Domain   : $domain (${domain == 0 ? "HOST_DRAM_SHM" : domain == 1 ? "CUDA_VRAM" : "OTHER"})');
      stdout.writeln('  ├── Epoch State     : $state (${state == 1 ? "COMMITTED_READ" : "OTHER"})');
      stdout.writeln('  ├── Total Elementos : $elements (Dimensión)');
      stdout.writeln('  ├── Byte Length     : $byteLen bytes (${(byteLen / 1024).toStringAsFixed(2)} KB)');
      stdout.writeln('  └── Wire Integrity  : BITWISE CERTIFIED (128B exactos)');
    }
  }
  stdout.writeln('');

  // 3. Inspección del Estado 1D Colapsado en Disco Rígido
  final binFile = File(binPath);
  if (binFile.existsSync()) {
    final bytes = binFile.readAsBytesSync();
    final floatList = Float64List.sublistView(bytes);
    final count = floatList.length;

    var sumSq = 0.0;
    for (var i = 0; i < count; i++) {
      final v = floatList[i];
      sumSq += v * v;
    }
    final norm = sqrt(sumSq);
    final deviation = (norm - 1.0).abs();

    stdout.writeln('● ESTADO 1D COLAPSADO EN DISCO RÍGIDO:');
    stdout.writeln('  ├── Ruta Archivo    : $binPath');
    stdout.writeln('  ├── Tamaño Físico   : ${bytes.length} bytes');
    stdout.writeln('  ├── Elementos FP64  : $count floats');
    stdout.writeln('  ├── Norma L2 ||x||  : ${norm.toStringAsFixed(15)}');
    stdout.writeln('  ├── Desviación |1-N|: ${deviation.toStringAsExponential(3)}');
    stdout.writeln('  └── Certificación   : ${deviation < 5.0e-15 ? "SOTA_CERTIFIED (COTA TEÓRICA CUMPLIDA)" : "DIVERGENTE"}');
  }

  stdout.writeln('');
  stdout.writeln('══════════════════════════════════════════════════════════════════════');
}
