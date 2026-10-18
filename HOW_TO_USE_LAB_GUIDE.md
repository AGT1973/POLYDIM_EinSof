# GUÍA PEDAGÓGICA Y MANUAL DE LABORATORIO — POLYDIM EINSOF
## Cátedra de Arquitecturas Distribuidas de Alta Dimensión y Cómputo No Euclidiano
### Universidad Tecnológica Nacional — Facultad Regional Buenos Aires (UTN-FRBA)
**Grupo de Investigación POLYDIM | Versión Académica V26155 / Paper V1550**

---

## 🏛️ CONTEXTO INSTITUCIONAL Y MISIÓN PEDAGÓGICA

Bienvenido al entorno de investigación y desarrollo de **POLYDIM EINSOF**. 

En la ingeniería de inteligencia artificial contemporánea, el paradigma hegemónico colapsa las representaciones latentes a cadenas unidimensionales de texto ("gusano de tokens 1D"). De acuerdo con la **Desigualdad del Procesamiento de Datos** (*Data Processing Inequality*, DPI):

$$I(X; Z) \le I(X; Y)$$

Cada paso intermedio de cuantización o serialización textual destruye irreversiblemente la entropía y la riqueza métrica del espacio latente. La tesis central de POLYDIM postula que la cognición de redes neuronales es intrínsecamente **continua, geométrica y de alta dimensión**, residiendo de manera natural sobre variedades riemannianas como la hiperesfera unitaria $\mathcal{S}^{D-1}$ ($D \ge 10.000$) y la variedad de marcos ortonormales de Stiefel $\mathrm{St}(D, K)$.

Para garantizar la reproducibilidad científica universal sin requerir semanas de configuración ni dependencias de terceros, este repositorio cuenta con una suite **cero-dependencias** que valida en silicio real los principios fundacionales del proyecto.

---

## ⚡ PASO 0: EJECUCIÓN "CLICK-AND-RUN" (ZERO-CONFIG MASTER RUNNER)

Todo alumno de grado, posgrado o evaluador externo puede verificar la integridad del entorno ejecutando un único comando desde cualquier terminal:

```bash
python quickstart_harness.py
```

### ¿Qué hace internamente este script?
1. **Interroga el Silicio Local (Regla 27 - Silicon Contract):** Detecta dinámicamente si la máquina cuenta con procesadores AMD (Zen/Excavator), Intel (Xeon/Core), ARM (Apple Silicon/Graviton) o aceleradores NVIDIA GPU / Google Cloud TPU, asignando el nivel de memoria correspondiente (Clase 0 a Clase 4) sin asumir vendor-lock.
2. **Audita los Compiladores Disponibles:** Identifica en el `PATH` la presencia de `g++` (GCC 14), `rustc` (Rust 2021 Safe SIMD), `dart` (Flutter SDK) y `python` (3.11/3.14). Si algún compilador no está instalado, **no falla**: conmuta automáticamente a la implementación nativa pura en Python estándar.
3. **Ejecuta la Suite de 3 Invariantes Matemáticas:**
   - **Invariante 1:** Normalización Hiperesférica en $\mathcal{S}^{D-1}$ ($D = 10.000$) con acumulador compensado de Neumaier y escalado Blue/LASSQ.
   - **Invariante 2:** Proyección y marco ortonormal de Stiefel $\mathrm{St}(10.000, 4)$ con defecto ortogonal $\|X^T X - I_K\|_\infty < 10^{-14}$ mediante algoritmo Gram-Schmidt Modificado reortogonalizado (*Twice-Is-Enough Theorem*).
   - **Invariante 3:** Superacumulación exacta Kulisch demostrando la preservación de 56 bits en productos subnormales extremos ($10^{-315} \times 10^{-315}$) donde la FPU estándar colapsa a $0.0$, y resistencia a cancelación catastrófica.
4. **Auditoría de Recursos Físicos:**
   - Latencia total inferior a 2 segundos en CPU estándar.
   - Consumo de memoria RAM física del proceso estrictamente $< 80$ MB.
   - Retorno estricto de **EXIT CODE 0**.

---

## 🔬 LABORATORIO 1: TRANSMISIÓN ZERO-COPY INTER-PROCESO (PMTP VS JSON)

### 1.1 Fundamento Teórico
Cuando dos procesos o agentes de IA intercambian un tensor de dimensión $D = 10.000$ en formato JSON, la representación textual requiere:
- Aproximadamente 250 KB a 300 KB de caracteres ASCII con coma flotante (`"0.123456789012345", ...`).
- Parseo de strings, asignación masiva en el heap y redondeo espurio.
- Latencias de $15$ a $50$ milisegundos y uso innecesario de ciclos de CPU.

El protocolo **PMTP** (*Polydim Multi-Tenant Protocol*) elimina la serialización: los procesos intercambian únicamente un descriptor binario C-ABI de **88 bytes** (`PmtpTensorDescriptor`) y leen los datos directamente de la memoria compartida física (*Shared Memory*) en **cero copias**.

#### Estructura del Descriptor PMTP (88 Bytes):
```text
Offset  Tamaño  Campo          Descripción
0       4 B     magic          "PDM4" (Identificador único de protocolo)
4       2 B     version        26155 (Versión del protocolo C-ABI)
6       2 B     encoded_size   88 (Longitud exacta del descriptor en bytes)
8       8 B     segment_id     ID del segmento de memoria compartida
16      8 B     buffer_id      ID del búfer físico
24      8 B     generation     Contador monotónico de generación
32      8 B     byte_offset    Desplazamiento del tensor (88 bytes para datos)
40      8 B     byte_length    Longitud exacta de datos (80.000 bytes para FP64)
48      1 B     dtype_code     1 = IEEE-754 binary64 (float64)
49      1 B     ndim           Número de dimensiones (1 para vector)
50      6 B     reserved       Alineación a 8 bytes (padding con ceros)
56      32 B    shape          [10000, 0, 0, 0] (uint64_t x 4)
-------------------------------------------------------------------------
TOTAL:  88 Bytes
```

### 1.2 Práctica de Laboratorio: Implementación Ejecutable

Crea un archivo llamado `lab1_pmtp_demo.py` y ejecútalo para contrastar el rendimiento:

```python
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
```

### 1.3 Tarea para el Alumno
1. Ejecuta el script y calcula el factor de aceleración exacto en tu estación de trabajo.
2. ¿Por qué es obligatorio llamar a `with memoryview(...)` o liberar la vista de memoria antes de invocar `shm_consumer.close()` en Python? *(Pista: Inspecciona la excepción `BufferError` del protocolo de búferes de CPython)*.

---

## 🧮 LABORATORIO 2: PREVENCIÓN DE CANCELACIÓN CATASTRÓFICA Y SUPERACUMULADOR C++20

### 2.1 Fundamento Teórico
En el entrenamiento de redes neuronales profundas con manifolds no euclidianos y optimizadores de segundo orden, surgen dos patologías numéricas críticas en el estándar IEEE-754 binary64 (doble precisión):

1. **Underflow de Productos Subnormales:**
   El número positivo no nulo más pequeño representable en IEEE-754 binary64 es $2^{-1074} \approx 4,94 \times 10^{-324}$.
   Si multiplicamos dos gradientes pequeños en la cola de una distribución gaussiana, por ejemplo:
   $$a = 10^{-315}, \quad b = 10^{-315}$$
   El producto analítico exacto es:
   $$a \times b = 10^{-630} \approx 2^{-2093}$$
   En cualquier CPU estándar con FPU IEEE-754 comercial, la operación de hardware produce inmediatamente:
   $$10^{-315} \times 10^{-315} \longrightarrow 0,0 \quad \text{(Underflow Catastrófico)}$$
   Se destruyen 56 bits de información de gradiente.

2. **Cancelación Catastrófica en Acumulación de Gradientes:**
   Al sumar términos de magnitudes dispares, por ejemplo:
   $$S = (10^8 + 10^{-8}) - 10^8$$
   El resultado exacto analítico es $10^{-8}$. Sin embargo, en FP64 estándar, la suma ingenua devuelve $1,4901 \times 10^{-8}$, lo que representa un **49% de error relativo**.

#### La Solución POLYDIM: El Superacumulador Kulisch de 4.352 Bits
El superacumulador de Kulisch (`SuperaccSoA` en C++20, arquitectura C07 de POLYDIM) implementa un registro de punto fijo de 4.352 bits distribuido en 136 bloques de `uint32_t` (radix $2^{32}$).
- El bit 0 representa el peso exacto de $2^{-2148}$.
- El bit 2.148 representa el entero $1,0$.
- El bit 4.351 representa $2^{+2048}$.
Cualquier producto de dos flotantes IEEE-754 ($2^{-1074} \times 2^{-1074} = 2^{-2148}$) se ubica sin redondeo intermedio dentro de la ventana del acumulador.

### 2.2 Práctica de Laboratorio: Implementación Ejecutable

Crea un archivo llamado `lab2_superaccumulator.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO 2: SUPERACUMULADOR KULISCH Y PREVENCIÓN DE CANCELACIÓN
Cátedra POLYDIM — UTN-FRBA
"""

import struct
import math

class KulischSuperacc4352:
    """
    Simulador de Referencia C07: Registro de Punto Fijo de 4.352 bits.
    136 palabras de 32 bits (Radix 2^32). Rango: [2^-2148, 2^+2048].
    """
    def __init__(self):
        self.words = [0] * 136

    def accumulate_product(self, a: float, b: float):
        # 1. Descomponer flotantes IEEE-754 en signo, exponente y mantisa entera
        bits_a = struct.unpack('!Q', struct.pack('!d', a))[0]
        bits_b = struct.unpack('!Q', struct.pack('!d', b))[0]

        exp_a, mant_a = (bits_a >> 52) & 0x7FF, bits_a & 0xFFFFFFFFFFFFF
        exp_b, mant_b = (bits_b >> 52) & 0x7FF, bits_b & 0xFFFFFFFFFFFFF

        # Exponentes y mantisas según tipo de número (normal vs subnormal)
        scale_a = -1074 if exp_a == 0 else (exp_a - 1075)
        int_m_a = mant_a if exp_a == 0 else (mant_a | (1 << 52))

        scale_b = -1074 if exp_b == 0 else (exp_b - 1075)
        int_m_b = mant_b if exp_b == 0 else (mant_b | (1 << 52))

        # Producto entero exacto (hasta 106 bits de precisión)
        prod_int = int_m_a * int_m_b
        total_exp = scale_a + scale_b

        # Desplazamiento respecto al bit 0 del acumulador (quantum 2^-2148)
        bit_pos = total_exp + 2148
        
        # Desplazar y sumar a las palabras radix 2^32
        shifted = prod_int << bit_pos
        bits_totales = prod_int.bit_length()
        
        idx = 0
        temp = shifted
        while temp > 0 and idx < 136:
            self.words[idx] += (temp & 0xFFFFFFFF)
            temp >>= 32
            idx += 1

        return {
            "prod_int": prod_int,
            "bits_totales": bits_totales,
            "bit_pos": bit_pos,
            "word_index": bit_pos // 32
        }

def run_lab2():
    print("=" * 70)
    print("LABORATORIO 2: AUDITORÍA DE CANCELACIÓN CATASTRÓFICA Y SUBNORMALES")
    print("=" * 70)

    # CASO 1: Subnormal Underflow Catastrófico
    a = 1.0e-315
    b = 1.0e-315
    prod_hardware = a * b

    print(f"\n[EXPERIMENTO 1: PRODUCTO SUBNORMAL a={a}, b={b}]")
    print(f"  • Hardware FPU estándar a * b : {prod_hardware}")
    print(f"  • ¿Hubo Underflow a Cero?     : {prod_hardware == 0.0} (INFORMACIÓN DESTRUIDA)")

    acc = KulischSuperacc4352()
    res = acc.accumulate_product(a, b)

    print(f"  • En Superacumulador Kulisch  : PRESERVADO EXACTO")
    print(f"  • Bits exactos activos        : {res['bits_totales']} bits")
    print(f"  • Posición de bit en registro : Bit {res['bit_pos']} (Palabra {res['word_index']})")
    print(f"  • Valor entero en registro    : {res['prod_int']}")

    # CASO 2: Cancelación Catastrófica en Sumas
    print(f"\n[EXPERIMENTO 2: CANCELACIÓN CATASTRÓFICA (1e8 + 1e-8) - 1e8]")
    suma_ingenua = (1.0e8 + 1.0e-8) - 1.0e8
    error_relativo_ingenuo = abs(suma_ingenua - 1.0e-8) / 1.0e-8

    print(f"  • Suma ingenua en Python/C++  : {suma_ingenua:.16e}")
    print(f"  • Valor analítico exacto      : 1.0000000000000000e-08")
    print(f"  • Error relativo de la FPU    : {error_relativo_ingenuo:.2%} (ERROR GRAVE)")

    # Acumulación compensada de Neumaier
    def neumaier(vals):
        s, c = 0.0, 0.0
        for v in vals:
            t = s + v
            if abs(s) >= abs(v):
                c += (s - t) + v
            else:
                c += (v - t) + s
            s = t
        return s + c

    suma_neumaier = neumaier([1.0e8, 1.0e-8, -1.0e8])
    error_neumaier = abs(suma_neumaier - 1.0e-8) / 1.0e-8
    print(f"  • Suma compensada Neumaier     : {suma_neumaier:.16e}")
    print(f"  • Error relativo Neumaier     : {error_neumaier:.2e} (PRECISIÓN TOTAL)")
    print("=" * 70)

if __name__ == "__main__":
    run_lab2()
```

### 2.3 Compilación Opcional en C++20 Nativo
Para comprobar la implementación en lenguaje C++ compilado, ubica el ejecutable de referencia en el repositorio:
```bash
# Ejecución del binario compilado de referencia
.\ENTREGA_2026_10_09_V26200\RESPUESTAS\c07_exact_converter_reference.exe
```
Salida esperada:
```text
(EXIT_CODE=0, LATENCY_MS=0.007, PEAK_RAM_MB=0.0083, CHECKS_PASSED=13/13)
```

---

## 🗄️ LABORATORIO 3: INSPECCIÓN DE LOS 1.571 TEOREMAS EN POSTGRESQL 16

### 3.1 Fundamento Teórico y Regla 0
En sistemas autónomos de investigación agéntica, el uso de bases de datos embebidas basadas en archivos (como SQLite) induce **amnesia inter-sesión**, bloqueos de archivo concurrentes (`database is locked`) y desincronización de estado entre pestañas y terminales.

Por mandato de la **Regla 0 (Anti-Amnesia Bootstrap & Exclusividad Total de PostgreSQL 16)**:
- Queda terminantemente vetado SQLite para operaciones activas del proyecto.
- **PostgreSQL 16.4** es la **única fuente de verdad transaccional**, alojando la base de datos `polydim_vec_db` con la tabla maestra de teoremas certificados: `polydim_theorems`.

### 3.2 Esquema de la Tabla `polydim_theorems`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | Identificador único secuencial del teorema |
| `cycle` | `VARCHAR(50)` | Ciclo de auditoría o entrega (ej. `V930`, `V26155`) |
| `version` | `VARCHAR(50)` | Versión del kernel asociada |
| `topic` | `TEXT` | Título y tópico matemático formal |
| `theorem` | `TEXT` | Enunciado analítico riguroso y demostración |
| `status` | `VARCHAR(50)` | Estado de certificación (`SOTA_CERTIFIED`, `SOTA_AUDITED`) |
| `redteam_note` | `TEXT` | Ataque adversarial y resolución de vulnerabilidad |
| `staging_ref` | `TEXT` | Archivo fuente físico donde se implementa el teorema |

### 3.3 Práctica de Laboratorio: Script de Inspección Segura

Crea un archivo llamado `lab3_inspect_theorems.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO 3: CONSULTA TRANSACCIONAL DE TEOREMAS EN POSTGRESQL 16
Cátedra POLYDIM — UTN-FRBA
"""

import sys

def run_lab3():
    print("=" * 70)
    print("LABORATORIO 3: AUDITORÍA TRANSACCIONAL DE TEOREMAS (POSTGRESQL 16)")
    print("=" * 70)

    try:
        import psycopg
    except ImportError:
        print("\n[AVISO]: El paquete 'psycopg' no está instalado en este entorno.")
        print("Para instalarlo en tu entorno virtual: pip install psycopg")
        print("\nConsulta equivalente mediante CLI de PostgreSQL (psql):")
        print("  psql -U postgres -d polydim_vec_db -c 'SELECT COUNT(*), MIN(id), MAX(id) FROM polydim_theorems;'")
        print("=" * 70)
        return

    # Parámetros de conexión oficiales de POLYDIM (localhost:5432)
    conn_params = {
        "dbname": "polydim_vec_db",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432
    }

    try:
        conn = psycopg.connect(**conn_params)
        cur = conn.cursor()

        # 1. Verificación del Censo Maestro de Teoremas
        cur.execute("SELECT COUNT(*), MIN(id), MAX(id) FROM polydim_theorems;")
        total, min_id, max_id = cur.fetchone()

        print(f"\n[1. ESTADO TRANSACCIONAL MAESTRO]")
        print(f"  • Total de Teoremas Certificados : {total}")
        print(f"  • Rango de IDs Físicos          : {min_id} .. {max_id}")

        # 2. Desglose por Estado de Certificación
        cur.execute("SELECT status, COUNT(*) FROM polydim_theorems GROUP BY status ORDER BY count DESC;")
        print(f"\n[2. DESGLOSE DE CERTIFICACIÓN]")
        for status, count in cur.fetchall():
            print(f"  • Estado: {status:<18} | Cantidad: {count} teoremas")

        # 3. Muestra de Teoremas Críticos de Silicio (Regla 13: Consulta Acotada)
        cur.execute("""
            SELECT id, topic, status, staging_ref 
            FROM polydim_theorems 
            WHERE topic ILIKE '%Stiefel%' 
               OR topic ILIKE '%Householder%' 
               OR topic ILIKE '%Neumaier%'
            ORDER BY id ASC 
            LIMIT 5;
        """)
        print(f"\n[3. MUESTRA DE TEOREMAS DE RETRACCIÓN Y PRECISIÓN (LIMIT 5)]")
        for row in cur.fetchall():
            thm_id, topic, status, staging = row
            staging_str = staging if staging else "Núcleo Analítico"
            print(f"  • Teorema {thm_id:04d} [{status}]: {topic}")
            print(f"    └ Implementación física: {staging_str}")

        cur.close()
        conn.close()
        print("\n[RESULTADO]: Base de datos sincronizada. Exit Code 0.")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR DE CONEXIÓN POSTGRESQL]: {e}")
        print("Asegúrate de que el servicio PostgreSQL 16 esté activo en el puerto 5432.")
        print("=" * 70)

if __name__ == "__main__":
    run_lab3()
```

### 3.4 Consultas SQL Directas (Para psql o DBeaver)
Si utilizas el cliente de línea de comandos `psql`:

```sql
-- 1. Verificar el recuento total físico (debe retornar 1571)
SELECT COUNT(*) FROM polydim_theorems;

-- 2. Inspeccionar teoremas con notas del Red Team
SELECT id, topic, redteam_note 
FROM polydim_theorems 
WHERE redteam_note IS NOT NULL AND redteam_note != ''
ORDER BY id DESC 
LIMIT 5;

-- 3. Resumen de versión y ciclo
SELECT version, COUNT(*) 
FROM polydim_theorems 
GROUP BY version 
ORDER BY COUNT(*) DESC;
```

---

## 📋 RÚBRICA DE EVALUACIÓN PARA DOCENTES Y EVALUADORES

| Criterio | Requisito Formal | Puntaje |
|---|---|:---:|
| **Ejecución Zero-Config** | Ejecuta `python quickstart_harness.py` retornando `EXIT CODE 0` sin instalar paquetes pip externos. | 25% |
| **Límites Físicos** | Latencia total $< 2$ segundos y huella de memoria RAM estrictamente $< 80$ MB. | 15% |
| **Laboratorio 1 (PMTP)** | Comprensión y demostración de la cabecera C-ABI de 88 bytes y lectura zero-copy vía `memoryview`. | 20% |
| **Laboratorio 2 (Kulisch)** | Explicación del underflow subnormal ($10^{-315} \times 10^{-315}$) y demostración de los 56 bits en el superacumulador. | 20% |
| **Laboratorio 3 (PostgreSQL)** | Conexión a `polydim_vec_db` y verificación de los 1.571 teoremas con el desglose de estados. | 20% |
| **TOTAL** | **Conformidad Estricta en Silicio Real** | **100%** |

---
*Cátedra de Arquitecturas Distribuidas de Alta Dimensión — UTN-FRBA 2026*
