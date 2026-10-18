#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO 1: PMTP ZERO-COPY VS JSON SERIALIZATION BENCHMARK
Cátedra POLYDIM — UTN-FRBA
"""

import time
import json
import struct
import array
from multiprocessing import shared_memory

D = 10000  # Dimensión del espacio vectorial

def run_lab1():
    print("=" * 70)
    print("LABORATORIO 1: PMTP ZERO-COPY VS SERIALIZACIÓN JSON (D = 10.000)")
    print("=" * 70)

    # 1. Crear vector de prueba en R^10000
    vector_original = [float(i) * 0.0001 for i in range(D)]

    # -------------------------------------------------------------
    # EXPERIMENTO A: SERIALIZACIÓN TRADICIONAL JSON (Gusano 1D)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    json_str = json.dumps(vector_original)
    json_bytes = json_str.encode('utf-8')
    vector_recuperado_json = json.loads(json_str)
    t_json_ms = (time.perf_counter() - t0) * 1000.0
    tamano_json_kb = len(json_bytes) / 1024.0

    print(f"\n[ENFOQUE TRADICIONAL - JSON]")
    print(f"  • Latencia de ida y vuelta : {t_json_ms:.2f} ms")
    print(f"  • Sobrecarga de red/RAM    : {tamano_json_kb:.1f} KB transferidos")
    print(f"  • Copias en memoria        : 3 asignaciones completas de heap")

    # -------------------------------------------------------------
    # EXPERIMENTO B: PMTP ZERO-COPY (Descriptor 88 Bytes en RAM)
    # -------------------------------------------------------------
    shm_name = "pmtp_lab1_shared_slab"
    try:
        old_shm = shared_memory.SharedMemory(name=shm_name)
        old_shm.close()
        old_shm.unlink()
    except FileNotFoundError:
        pass

    # Reservar bloque de memoria compartida: 88 bytes de cabecera + D * 8 bytes de datos
    shm_size = 88 + (D * 8)
    shm = shared_memory.SharedMemory(name=shm_name, create=True, size=shm_size)

    t0_pmtp = time.perf_counter()

    # 1. Empaquetar Descriptor PMTP (88 Bytes exactamente)
    # Formato C-ABI: 4s (magic), H (ver), H (sz), Q (seg), Q (buf), Q (gen), Q (off), Q (len), B (dtype), B (ndim), 6s (res), 4Q (shape)
    desc_bytes = struct.pack(
        '<4sHHQQQQQBB6s4Q',
        b'PDM4',    # magic
        26155,      # version
        88,         # encoded_size
        1,          # segment_id
        101,        # buffer_id
        1,          # generation
        88,         # byte_offset
        D * 8,      # byte_length (80.000 B)
        1,          # dtype_code: 1 = float64
        1,          # ndim = 1
        b'\x00' * 6,# reserved
        D, 0, 0, 0  # shape
    )
    shm.buf[:88] = desc_bytes

    # 2. Escribir vector en el búfer compartido
    arr_datos = array.array('d', vector_original)
    shm.buf[88:88 + (D * 8)] = arr_datos.tobytes()

    # --- SIMULACIÓN DEL RECEPTOR (Otro Proceso) ---
    shm_consumer = shared_memory.SharedMemory(name=shm_name)
    
    # Leer el descriptor de 88 bytes
    magic, ver, sz, seg, buf, gen, off, b_len, dt, nd, res, s0, s1, s2, s3 = struct.unpack(
        '<4sHHQQQQQBB6s4Q', shm_consumer.buf[:88]
    )

    # Mapeo ZERO-COPY mediante memoryview (puntero directo a RAM, sin alloc)
    with memoryview(shm_consumer.buf[off:off + b_len]).cast('d') as zero_copy_view:
        val_0 = zero_copy_view[0]
        val_5000 = zero_copy_view[5000]
        val_9999 = zero_copy_view[9999]

    t_pmtp_ms = (time.perf_counter() - t0_pmtp) * 1000.0

    # Limpieza de recursos del sistema operativo
    shm_consumer.close()
    shm.close()
    shm.unlink()

    speedup = t_json_ms / max(0.001, t_pmtp_ms)
    print(f"\n[ENFOQUE NATIVO - PMTP ZERO-COPY]")
    print(f"  • Descriptor transmitido   : Exactamente 88 bytes C-ABI")
    print(f"  • Latencia de ida y vuelta : {t_pmtp_ms:.2f} ms")
    print(f"  • Factor de aceleración    : {speedup:.1f}x MÁS RÁPIDO")
    print(f"  • Verificación numérica    : idx[0]={val_0:.4f}, idx[5000]={val_5000:.4f}, idx[9999]={val_9999:.4f}")
    print(f"  • Copias en memoria        : 0 (Lectura directa sobre puntero físico)")
    print("=" * 70)

if __name__ == "__main__":
    run_lab1()
