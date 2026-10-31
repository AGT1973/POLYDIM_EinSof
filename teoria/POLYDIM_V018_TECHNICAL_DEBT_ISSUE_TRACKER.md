# POLYDIM / PMTP — REGISTRO FORMAL DE DEUDA TÉCNICA ARQUITECTÓNICA V018
> **Documento Canónico:** `E:\POLYDIM_EINSOF\DOCUMENTOS_MAESTROS\POLYDIM_V018_TECHNICAL_DEBT_ISSUE_TRACKER.md`  
> **Clasificación:** DEUDA TÉCNICA ESTRUCTURAL V018 (NO REPARABLE MEDIANTE PARCHES AISLADOS DE LÍNEA)  
> **Origen:** Dictamen Adversarial Externo Red Team (GPT-6.1-sol-pro Round 1 & Round 2)  
> **Estado:** ESPECIFICACIÓN REFINADA POST-R2 PARA REDISEÑO ARQUITECTÓNICO V018 | FECHA: 2026-10-31  

---

## I. MATRIZ CONSOLIDADA DE DEUDA TÉCNICA V018

| ID | Severidad | Componente / Ubicación | Defecto Fundamental | Acción Requerida en V018 | Estado |
|---|---|---|---|---|---|
| **D01** | **SEV-1** | `pmtp_kernel_cpp.cpp`<br>`pmtp_shm_read_leased`<br>`pmtp_shm_publish_atomic` | `memmove` ordinario no atómico en publisher vs `atomic_ref<uint64_t>` en consumer (Violación DRF ISO C++20 UB). Ni fences ni generation post-checks revierten el UB. | Rediseño completo con arbitraje simétrico por slot: Writer CAS (`READABLE`, readers=0) -> `WRITING`, copia payload, publica slot y descriptor; Reader CAS-pin en slot `READABLE` antes de prestar puntero. | **ESPECIFICACIÓN SOTA REFINADA R2** |
| **D04** | **SEV-1** | `pmtp_tri_segment.cpp`<br>`pmtp_tri_acquire_lease`<br>`pmtp_tri_release_lease` | Cookie sin nonce monotónico de 64 bits (32 bits agotan rango a $10^7$/s en 429 s; CRC8 no es anti-forja). Falta ciclo de vida de adquisición atómica. | Cookie opaca de 64 bits ligada a registro del servidor con máquina de estados `FREE -> ACQUIRING -> PINNED -> RELEASING -> FREE`, secuencia monotónica de 64 bits y no-reentrancia sincronizada. | **ESPECIFICACIÓN SOTA REFINADA R2** |
| **D05** | **SEV-1** | `pmtp_tri_segment.cpp`<br>`pmtp_tri_open`<br>Mapeo de segmento de leases | Mapeo RW monolítico compartido entre consumidores hostiles. Nombres o modo 0600 en POSIX no aíslan procesos con mismo UID; descriptores en Windows requieren ACLs explícitas. | Desacoplamiento MMU estricto: objetos creados por broker con autorización por token/UID y descriptores transferidos vía IPC de control; prohibición de reapertura por nombre predecible. | **ESPECIFICACIÓN SOTA REFINADA R2** |
| **D06** | **SEV-1 / SEV-2** | `pmtp_tri_segment.cpp`<br>`pmtp_tri_close` | Carrera en admisión: chequear `ACTIVE` y luego incrementar `in_flight_ops` permite que `close` desmapee entre ambas instrucciones. Timeout=0 salta drenaje. | Puerta de admisión atómica acoplada en una sola palabra CAS de 64 bits (`state_and_ops`: estado + in_flight_ops). Drenaje no destructivo que preserva mapeos ante timeout. | **ESPECIFICACIÓN SOTA REFINADA R2** |
| **D12** | **SEV-2** | `kernel_rust.rs` vs `pmtp_kernel_cpp.cpp`<br>`PmtpHeaderCompact` | `generation=0` (C++ EMPTY) vs `generation=1` (Rust). Máscaras colisionan con `PMTP_DESTROYING_BIT` (bit 63). No entran dos contadores de 32 bits + bit 63 en 64 bits. | Partición asimétrica canónica documentada: Slot 0 (32 bits, `0xFFFFFFFF`), Slot 1 (31 bits, `0x7FFFFFFF00000000ULL`), Bit 63 (`DESTROYING`). Rust `generation: AtomicU32::new(0)`. | **ESPECIFICACIÓN SOTA REFINADA R2** |
| **D13** | **SEV-2** | `pmtp_kernel_cpp.cpp`<br>`pmtp_shm_release_lease_raw` | `release_raw` sin autenticación. Un MAC BLAKE2s sin consumo de un solo uso permite replay de tokens capturados en release. | Capability token BLAKE2s acoplado a consumo atómico de un solo uso del nonce de adquisición (`acquisition_nonce`) al liberar, invalidando cualquier intento de replay. | **ESPECIFICACIÓN SOTA REFINADA R2** |
| **R2-08** | **SEV-1** | `pmtp_tri_segment.cpp`<br>`pmtp_tri_create` | Multiplicación no chequeada de tamaños de buffer en `pmtp_tri_create` (`sizeof + payload * num_slots`) permite wrapping de enteros previo a la reserva de memoria. | Aritmética checked / saturating estricta en silicio: validación previa de cotas $D, K, \text{num\_slots}$ antes de cualquier multiplicación para allocators. | **ESPECIFICACIÓN SOTA REFINADA R2** |

---

## II. ESPECIFICACIONES ARQUITECTÓNICAS REFINADAS (RED TEAM R2)

### [D01] Arbitraje Simétrico de Slots Libres de Carrera (Data-Race-Free ISO C++20)
Para erradicar la condición de carrera entre el `std::memmove` del publicador y los accesos de los consumidores, se abandona definitivamente la lectura no leasada sobre buffers en mutación. La publicación y lectura se coordinan mediante un protocolo de arbitraje atómico sobre cada slot:
1. **Escritor:**
   - Selecciona slot candidato $i \in \{0, 1, 2\}$.
   - Ejecuta CAS atómico: `slot_state[i].compare_exchange_strong(READABLE, WRITING)` garantizando que `readers_count[i] == 0`.
   - Copia datos mediante `std::memcpy` regular sin conflicto concurrentes.
   - Publica slot y descriptor con semántica de liberación (`std::memory_order_release`).
2. **Lector:**
   - Lee descriptor con semántica de adquisición (`std::memory_order_acquire`).
   - Ejecuta CAS atómico para anclar (*pin*) su lectura incrementando el contador del slot si y solo si permanece en `READABLE`.
   - Revalida el descriptor; únicamente accede al payload tras verificar la consistencia del anclaje.
   - Al terminar, libera su propio ticket atómico.

### [D04] Protocolo de Cookie Monotónica de 64 Bits con Ciclo de Vida Atómico
Para prevenir replay y agotamiento de rango temporal:
1. La secuencia de adquisición se basa en un contador monotónico de 64 bits (`uint64_t g_monotonic_lease_seq`), con período de envoltura asintótico inmune a agotamiento ($>58.000$ años a $10^7$ ops/s).
2. Se introduce la máquina de estados de adquisición:
   $$\mathrm{FREE} \xrightarrow{\text{CAS}} \mathrm{ACQUIRING} \xrightarrow{\text{Init}} \mathrm{PINNED} \xrightarrow{\text{CAS}} \mathrm{RELEASING} \xrightarrow{\text{Clean}} \mathrm{FREE}$$
3. El handle opaco de 64 bits referencia un registro seguro propiedad del broker/controlador, vinculando la adquisición a la sesión y espacio de proceso del cliente.

### [D05] Aislamiento de Memoria por MMU Bajo Modelo Hostil
1. El segmento de datos de publicación se mapea estrictamente `PAGE_READONLY` en todos los procesos consumidores.
2. Cada canal de control/lease reside en un objeto de memoria independiente, creado por el broker local con descriptores de seguridad (Win32 DACL / POSIX IPC) asignados por identidad de proceso/token.
3. Se erradica la apertura directa por nombres predecibles accesibles entre consumidores del mismo nivel de privilegios.

### [D06] Puerta de Admisión Atómica y Drenaje Seguro No Destructivo
1. Para eliminar la ventana de carrera entre la observación del estado `ACTIVE` y el incremento de operaciones en vuelo, el estado del contexto y el contador de operaciones se empaquetan en un único entero atómico de 64 bits:
   ```cpp
   // High 32 bits: Context State (ACTIVE, DRAINING, DRAINED, CLOSED)
   // Low 32 bits:  in_flight_ops
   std::atomic<uint64_t> state_and_ops;
   ```
2. La admisión a cualquier operación de lectura/escritura ejecuta un `fetch_add(1)` condicional a que los bits altos representen `ACTIVE`, todo en una única instrucción atómica de silicio (`LOCK CMPXCHG8B` en x86_64).
3. `pmtp_tri_close`:
   - Conmuta a `DRAINING` mediante CAS.
   - Permite que las operaciones de liberación (`release`) sigan ingresando.
   - Espera el vaciado de `in_flight_ops == 0` y la liberación de leases.
   - Si expira el tiempo límite, retorna `PMTP_ERR_TIMEOUT` sin desmapear la memoria ni invalidar descriptores, preservando la estabilidad del proceso.

### [D12] Partición Canónica de Bits y Semántica C++/Rust
1. Se fija la partición canónica en el entero empaquetado de 64 bits:
   - Slot 0: bits 0..31 (32 bits, máscara `0x00000000FFFFFFFFULL`, capacidad $2^{32}-1$ lectores).
   - Slot 1: bits 32..62 (31 bits, máscara `0x7FFFFFFF00000000ULL`, capacidad $2^{31}-1$ lectores).
   - Bit 63: `PMTP_DESTROYING_BIT` (`1ULL << 63`).
2. En `kernel_rust.rs`:
   - `generation: AtomicU32::new(0)` (unificado con C++ `0 = EMPTY`).
   - Máscaras simétricas a las de C++ aplicadas en adquisición y liberación.

### [D13] Autenticación Criptográfica de Solo-Un-Uso (Anti-Replay)
1. El capability token se calcula como:
   $$\mathrm{Token} = \operatorname{BLAKE2s}_{K_{\mathrm{session}}}(\mathrm{reader\_id} \parallel \mathrm{slot\_idx} \parallel \mathrm{generation\_64} \parallel \mathrm{nonce\_64})$$
2. En la liberación, el controlador consume atómicamente el `nonce_64` (transición a 0 o registro de tumba), de modo que reintentos o repeticiones del mismo token autenticado son rechazados de inmediato.

---

## III. CONCLUSIÓN DE CIERRE DE CICLO R2
El Tribunal Adversarial GPT-6.1-sol-pro ha validado la retirada de las afirmaciones inválidas de contracción única (D16) y ha aceptado la presente matriz como el marco formal para el rediseño estructural de **V018**.
El despliegue de V017 se sella como hito de transición y hardening preliminar, bloqueándose la certificación de producción hostil hasta la implementación completa de las 7 especificaciones de silicio detalladas en este documento.
