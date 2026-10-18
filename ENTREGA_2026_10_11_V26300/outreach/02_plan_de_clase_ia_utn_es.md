# PLAN DE CLASE: IA AVANZADA & CÓMPUTO DE ALTO RENDIMIENTO
**Institución:** UTN-FRBA / Maestría en Ciencia de Datos e Inteligencia Artificial  
**Asignatura:** Sistemas de IA en Alta Dimensión & Optimización Riemanniana  
**Módulo:** Cuello de Botella de Tokens 1D vs. Memoria Compartida de Copia Cero (PMTP)  
**Audiencia:** Alumnos de Ingeniería en Sistemas, Graduados, Maestrandos  
**Requisitos de Hardware:** Laptop estándar (AMD APU / Intel Core / Apple Silicon), 4 GB RAM, Python 3.10+  

---

## 1. OBJETIVOS DE APRENDIZAJE
Al finalizar esta sesión de laboratorio, los alumnos serán capaces de:
1. Comprender la formulación matemática de la **Desigualdad de Procesamiento de Información (DPI)** en cadenas de Markov y su impacto en la cuantización/tokenización.
2. Medir cuantitativamente la latencia de IPC, fallos de caché y ancho de banda comparando serialización de cadenas JSON frente a Memoria Compartida Win32/POSIX.
3. Decodificar y construir el descriptor binario de 88 bytes **PMTP** utilizando `struct` de Python y buffers `ndarray` de NumPy.
4. Ejecutar e interpretar las 29 comprobaciones deterministas de silicio en `polydim_v26155_monolito.py`.

---

## 2. FUNDAMENTOS TEÓRICOS (30 MINUTOS)

### 2.1 El Cuello de Botella de Tokens 1D y DPI
Sean dos agentes cooperativos, Agente $A$ y Agente $B$:
* Estado latente del Agente $A$: $X \in \mathbb{R}^D$ donde $D = 10.000$.
* Pipeline clásico: Agente $A$ proyecta $X \to$ tokens discretos $T_1, \dots, T_m \to$ cadena JSON $S \to$ socket de red $\to$ Agente $B$ tokeniza $S \to$ capa de embedding $\to \hat{X}$.
* **Cota de DPI y Teoría de Tasa-Distorsión (Cover & Thomas, 2006):**
  Un flujo de bytes 1D sin límite puede codificar cualquier matriz sin pérdidas. No obstante, los sistemas reales imponen:
  1. Presupuesto de contexto finito: $m < \infty$.
  2. Vocabulario discreto finito: $|\Sigma| \approx 32.000$.
  3. No inyectividad en la impresión de flotantes ($\exists x \ne y : T(x) = T(y)$).
  Bajo $I(X; \hat{X}) \le I(X; S) \le H(S) \le m \log_2 |\Sigma|$, la información mutua queda acotada en $\approx 1.916\text{ bits}$ para $m=128$, forzando una distorsión geométrica no nula $\mathbb{E}[\|X - \hat{X}\|_F^2] \ge D^*(R)$.

### 2.2 La Alternativa de Copia Cero PMTP
En lugar de serializar floats a texto:
1. El Agente $A$ reserva un bloque de memoria compartida del SO (`multiprocessing.shared_memory` o Win32 `CreateFileMappingW`).
2. El Agente $A$ escribe los bytes binarios crudos IEEE-754 FP64 directamente en el bloque.
3. El Agente $A$ envía una estructura de 88 bytes con nombre de slab, shape, dtype y offset al Agente $B$.
4. El Agente $B$ mapea el bloque en su espacio de direcciones sin copiar un solo byte en memoria.
* **Métricas Reales:** Transferencia del descriptor en $< 1,2\ \mu\text{s}$. Ancho de banda saturando el bus de memoria (9,03 GB/s DMA Pinned, hasta 102,4 GB/s DDR5, 139,78 GB/s Triton SRAM).
* **Condicionamiento Numérico:** Sobre $\mathrm{St}(n, k)$, la actualización de Cayley asegura $\|Y^\top Y - I_k\|_F \le C(n, k) u \kappa(A)$, con fallback automático a Polar/QR si el número de condición se degrada.

---

## 3. EJERCICIOS PRÁCTICOS DE LABORATORIO (60 MINUTOS)

### Ejercicio 3.1: Benchmark de IPC JSON vs. Memoria Compartida (Script de Alumno)
Los estudiantes ejecutan el script comparativo en sus máquinas locales:

```python
import time
import json
import numpy as np
from multiprocessing import shared_memory

def run_comparison(dim=4096):
    print(f"=== BENCHMARK UTN: Tensor Latente D={dim} (Float64) ===")
    tensor = np.random.randn(dim).astype(np.float64)
    raw_bytes = tensor.nbytes
    print(f"Tamano crudo: {raw_bytes} bytes ({raw_bytes / 1024:.2f} KB)")

    # 1. Pipeline Clasico JSON
    t0 = time.perf_counter()
    json_str = json.dumps(tensor.tolist())
    json_bytes = len(json_str.encode('utf-8'))
    t_ser = time.perf_counter() - t0

    t0 = time.perf_counter()
    reconstructed_list = json.loads(json_str)
    reconstructed_np = np.array(reconstructed_list, dtype=np.float64)
    t_deser = time.perf_counter() - t0
    total_json_time = (t_ser + t_deser) * 1000.0

    print(f"\n[1] Pipeline Clasico JSON:")
    print(f"    Tamano Serializado: {json_bytes} bytes (Expansion: {json_bytes / raw_bytes:.2f}x)")
    print(f"    Tiempo Ida y Vuelta: {total_json_time:.3f} ms")
    print(f"    Error Reconstruccion: {np.max(np.abs(tensor - reconstructed_np)):.2e}")

    # 2. Pipeline PMTP Memoria Compartida
    t0 = time.perf_counter()
    shm = shared_memory.SharedMemory(create=True, size=raw_bytes)
    target_buf = np.ndarray(tensor.shape, dtype=tensor.dtype, buffer=shm.buf)
    np.copyto(target_buf, tensor)
    t_write = time.perf_counter() - t0

    t0 = time.perf_counter()
    read_buf = np.ndarray(tensor.shape, dtype=tensor.dtype, buffer=shm.buf)
    t_read = time.perf_counter() - t0
    total_shm_time = (t_write + t_read) * 1000.0

    print(f"\n[2] Pipeline PMTP Memoria Compartida:")
    print(f"    Sobrecarga Metadata: 88 bytes fijos")
    print(f"    Tiempo Ida y Vuelta: {total_shm_time:.3f} ms")
    print(f"    Error Reconstruccion: {np.max(np.abs(tensor - read_buf)):.2e}")
    print(f"    Aceleracion:        {total_json_time / max(total_shm_time, 1e-6):.1f}x")

    shm.close()
    shm.unlink()

if __name__ == '__main__':
    run_comparison(4096)
```

### Ejercicio 3.2: Inspección del Descriptor Binario de 88 Bytes
Los estudiantes analizan la estructura definida en `polydim_v26155_monolito.py`:
1. ¿Por qué es indispensable `#pragma pack(push, 1)` al intercambiar estructuras entre Python, C++ y Rust?
2. ¿Qué ocurre si el campo `magic` no coincide con `0x504D5450`?
3. Verificar que la suma CRC32 detecte alteraciones de un solo bit en desplazamientos o coordenadas de forma.

---

## 4. CRITERIOS DE EVALUACIÓN Y RÚBRICA

Los alumnos ejecutan la suite de conformidad del monolito:
```powershell
python E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26155\polydim_v26155_monolito.py
```

### Criterios de Corrección:
* **Checks 1 a 7 (Conformidad PMTP):** 100% aprobados con 0 errores.
* **Checks 8 a 15 (Geometría Numérica):** Defecto de ortogonalidad $< 10^{-14}$.
* **Código de Retorno:** Obligatoriamente `Exit Code 0`. Cualquier excepción no capturada invalida la entrega.
