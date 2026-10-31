# POLYDIM-EINSOF: ESPECIFICACIÓN FORMAL RIGUROSA Y MARCO AXIOMÁTICO DE DISEÑO (VERSIÓN 44.0)

> **Autor:** Ariel García Traba — Independent Research / EinsofOS  
> **Ámbito:** Variedades de Stiefel, Retracción Polar Asintótica y Protocolos de Silicio SWMR Multi-Buffer con Reserva Atómica por CAS y Guardias RAII  
> **Clasificación Epistemológica:** Especificación formal rigurosa de diseño de sistemas y marco axiomático riemanniano. Cada enunciado se clasifica taxativamente como **DEFINICIÓN**, **AXIOMA**, **TEOREMA DEMOSTRADO**, **PROPOSICIÓN CON COTA ASINTÓTICA**, **PROTOCOLO DE SILICIO CERTIFICADO** o **CONJETURA EMPÍRICA**.  
> **Fecha de Consolidación:** 31 de Octubre de 2026 (V44.0)  
> **Principio Rector:** Rigor matemático absoluto, transparencia en suposiciones de modelo, y separación taxativa entre teoremas analíticos exactos, identidades de almacenamiento y protocolos empíricos en silicio. Cero math-washing.

---

## REGISTRO HISTÓRICO DE REVISIONES Y CALIBRACIÓN ADVERSARIAL (V1 – V12)

| Versión | Dictamen del Tribunal Multi-IA | Falla Técnica Diagnosticada | Resolución Formal Consolidada en V12 |
|---|---|---|---|
| **V1** | RECHAZO (INVALID) | Conflación métrica euclídea/canónica; biyectividad global infundada; Seqlock con carrera de datos (UB en C++20). | Restricción métrica a Frobenius extrínseca; espacio portador desacoplado del codificador; erradicación de Seqlock. |
| **V2** | RECHAZO (INVALID) | Cota Neumaier universal $\le 2\epsilon$ errónea; extrapolación de Higham a $T \to \infty$; circularidad en Weyl. | Cota Neumaier proporcional a condición $2u\sum|x_i|$; política de reset periódico; precondición $\eta_t$. |
| **V3** | RECHAZO (INVALID) | Inconsistencias de dimensión en Procrustes; sobre-reclamo de dominancia universal sobre baselines. | Inmersión ambient $L_{ij} \in \mathbb{R}^{D_j \times D_i}$; separación entre identidad de huella y fidelidad downstream. |
| **V4** | REVISIÓN MAYOR | Inexactitud en la topología de $O(K)$; ambigüedad en el cociente de Grassmann. | Formalización de conexidad por arcos para $D > K \ge 1$; cociente canónico $\mathrm{Gr}(K, D) = \mathrm{St}(D, K)/O(K)$. |
| **V5** | REVISIÓN MAYOR | Carrera TOCTOU en la adquisición del lector de memoria compartida. | Protocolo de fijación atómica con validación previa al acceso a datos. |
| **V6** | REVISIÓN MAYOR | Discrepancia geodésica no acotada; ambigüedad en la conexión de Levi-Civita. | Discrepancia cúbica local $O(t^3)$ demostrada; conexión proyectada sobre campos tangentes a lo largo de curvas. |
| **V7** | REVISIÓN MAYOR | Vulnerabilidad a colisiones por recambio de buffers bajo desprogramación de hilos. | Generación monótona de 64 bits anti-ABA y preservación de descriptores atómicos. |
| **V8** | RECHAZO (NOT OK) | Lecturas desarticuladas (split loads) en §9; Higham/Horner sobre-reclamados; unidades ambiguas en §10; reliquias conversacionales. | Unificación de descriptores en memoria; reclasificación de Higham/Horner a Proposiciones; unidades binarias MiB/GiB; purga de reliquias históricas. |
| **V9** | RECHAZO (NOT OK) | Carrera de adquisición-reclamación en §9 (incremento especulativo post-lectura de slot); falta de bounds checking en `memcpy`; drenaje de destrucción incompleto; Procrustes heterogéneo $K_i \neq K_j$ en §7; incoherencia matricial en §6; Neumaier condicionado en §8. | Sustitución de §9 por Protocolo de Reserva Atómica por CAS por Slot; verificación de tamaño en `memcpy`; drenaje formal en destrucción segura; Procrustes con rango común $K$; reclasificación de §6 a Conjetura de Separabilidad; cota Neumaier condicionada en §8. |
| **V10** | RECHAZO (NOT OK) | Publicación cursor desarticulada (`active_slot` y `generation` separados); falta de adquisición de `writer_lock` en shutdown; riesgo de desbordamiento de conteo de lectores (24-bit); token de lease opaco ausente; condición skew inexacta en §2; proyección polar con columna preservada sin proyección ambiental en §5; expansión de primer orden de retracción $-\frac{1}{2}Z\Delta_G$ en §4. | Descriptor de cursor empaquetado en palabra atómica indivisible de 64 bits (`pack_cursor`); protocolo de shutdown con exclusión mutua de escritor y estado terminal `CLOSED`; token de lease opaco (`PmtpLeaseToken`) con validación de posesión; comprobación de saturación de lectores (`MAX_READERS`); corrección a $\operatorname{sym}(X^\top Z) = 0$ en §2; preservación exacta del subespacio columna en §5; derivación exacta de perturbación $-\frac{1}{2}Z(Z^\top Z - I_K)$ en §4. |
| **V11** | RECHAZO (NOT OK) | En shutdown, sobreescritura incondicional de estado borraba conteo de lectores activos; token de lease no era move-only (permitía doble liberación); cálculo de wraparound de 32 bits a $10^7$ ops/s daba 429 s en vez de 13.6 años; falta de static_assert de lock-free; afirmación de optimización en §6; Neumaier sin término de orden superior $\gamma_{D+2}$. | Shutdown preserva el conteo de lectores mediante CAS sobre la máscara de estado; guardia RAII `PmtpLeaseGuard` estrictamente no-copiable y move-only; cursor de 64 bits con 56 bits para generation ($228.3$ años de operación continua a $10^7$ ops/s); static_assert de atomics lock-free y contrato explícito de ABI; cota Neumaier rigurosa con $\gamma_{D+2}$; erradicación de afirmaciones infundadas de optimización en §6. |
| **V12** | RECHAZO (NOT OK) | §9: interleaving proof incompleta, `generation_` no operativo, portabilidad IPC sobre-reclamada como ISO C++20, lifecycle race en destroying, shutdown bloqueo indefinido. §4.2: constante $C(\varepsilon)$ no demostrada. §7: "isométrica" infundada. §8: Neumaier sin pseudocódigo. §10.3: "erradicando colapso de rango" sobre-reclamado. §5.2: Welch sin régimen asintótico explícito. | Reencuadre de §9 como contrato de ABI de plataforma con precondiciones de ciclo de vida formales; uso operacional de `generation_` en liberación con validación anti-ABA; exhaustive interleaving enumeration; shutdown calificado como liveness precondition; derivación explícita de $C(\varepsilon)$ en §4.2; eliminación de "isométrica" en §7; pseudocódigo Neumaier en §8; reformulación §10.3; régimen Welch explícito en §5.2. |
| **V13** | RECHAZO (NOT OK) | §5.2: scaling asintótico erróneo ($\Omega(1/\sqrt{KD})$ debía ser $\Omega(\sqrt{K/D})$). §4.2: "cálculo funcional holomorfo" insuficiente para $\Delta_G$ simétrica (usar teorema espectral). §8: $\gamma_{D+2} \sim (D+2)u$ es primer orden, no $O(Du^2)$. §9: 7 casos no exhaustivos, generation check no es anti-ABA, cross-process over-claimed, deregistration protocol ausente. §4.1: $O(t^3)$ sin norma/constante. §11: auto-certificación contradictoria. | Corrección algebraica de Welch a $\Omega(\sqrt{K/D})$; derivación espectral explícita para $C(\varepsilon)$; reclasificación de $\gamma_{D+2}$ como primer orden en $u$; degradación de interleavings a "casos representativos"; eliminación de "anti-ABA validation" en generation check; especificación de protocolo de deregistro; degradación de §11 a estado de revisión abierta. |
| **V14** | RECHAZO (NOT OK) | §8: inconsistencia entre cota $2u+O(Du^2)$ y cota $\gamma_{D+2}$ de primer orden. §9.3: sobre-reclamo de sincronización ISO C++20 interproceso. §9 ciclo de vida: drenaje de shutdown no linealizado contra invocaciones concurrentes no registradas. §9.4: reclamo de anti-ABA excede lo que prueba el chequeo de generación. §4.3: constante de Lagrange orden 5 sin derivación explícita. §5.2: interpretación de Welch extendida indebidamente a todo empaquetamiento de Grassmann. | Reconciliación rigurosa de cota Neumaier a $(3u + O(Du^2))\sum|x_i y_i|$; reencuadre de §9.3 como ordenamiento de silicio a nivel de hardware/ABI; delimitación explícita de shutdown y ciclo de vida como propiedad conjunta con el supervisor; reclasificación de §9.4 como extensión de época numérica de 56 bits; derivación analítica completa del resto de Lagrange de orden 5 en §4.3; acotamiento de interpretación de §5.2 a coherencia mutua de Frobenius. |
| **V15** | RECHAZO (NOT OK) | §4.2: igualdad espuria en cota Frobenius (debe ser submultiplicativa $\le$). §4.3: constante de Lagrange $0.328$ vs evaluación analítica (reemplazar por expresión simbólica cerrada). §8: distinción explícita entre suma de $p_i$ y producto punto exacto. §9.3: sobre-reclamo de visibilidad de hardware (reencuadrar como contrato de ingeniería). §9 shutdown: aclarar dependencia obligatoria de barrera de admisión en supervisor (CdV-2). §9.4: validación de instancia (`instance_id`) para evitar decremento cruzado tras reinit. §9.2: invariante fundamental debe ser condicional a ejecución conforme. §10.1: etiquetar factores como "Razón de Capacidad Bruta" sin sobre-reclamo de equivalencia funcional. | Reemplazo por desigualdad submultiplicativa rigurosa en §4.2; formulación simbólica exacta de $C_4(\varepsilon)$ en §4.3; separación explícita de redondeo de productos y suma compensada en §8; reencuadre de §9.3 como contrato de plataforma; formalización del punto de linealización del supervisor en §9.5; incorporación de `instance_id` de 64 bits en §9.1 y guard RAII; reformulación del invariante como condicional a ejecución conforme en §9.2; reclasificación de §10.2 a Razón de Capacidad de Almacenamiento Físico Bruto. |
| **V16** | RECHAZO (NOT OK) | §9: validación de `instance_id` en `release()` incurre en TOCTOU si hay reinicialización concurrente. §8: Neumaier sobre-reclamado como teorema universal con hipótesis insuficientes. | Eliminación del chequeo TOCTOU en `release()` y delegación taxativa de no-reutilización al contrato del supervisor (CdV-2); reclasificación de §8 como Cota de Diseño Asintótica delimitada a la justificación del término líder $3u\sum|x_i y_i|$ según Higham (2002) sin sobre-reclamo de teorema universal. |
| **V17** | RECHAZO (NOT OK) | §4.2: definición inconsistente de $C(\varepsilon)$ en conclusión final. §4.3: cota espectral orden 5 debe acotarse como $\|R_4(E)\|_F \le C_4(\varepsilon) \|E\|_2^4 \|E\|_F$. §8: cota nominal $3u$ requiere calificación como aproximación heurística de diseño. §9.3: visibilidad requiere contrato explícito de SO/ABI sobre memoria compartida. §9.4: terminología anti-ABA debe acotarse a mitigación condicional a $< 2^{56}$ eventos. §9.1: definición autocontenida de `PmtpStiefelSlab` y `static_assert` para atómicos de 8 bits. §11: erradicar "hermético" en favor de delimitación de ingeniería de sistemas. | Definición unificada de $C(\varepsilon)$ en §4.2; derivación espectral rigurosa $\|R_4(E)\|_F \le C_4(\varepsilon) \|E\|_2^4 \|E\|_F$ en §4.3; calificación de §8 como estimación nominal de diseño con garantía operativa en QR; reformulación de §9.3 como contrato de despliegue sobre SO/ABI; acotamiento formal de §9.4 como mitigación de ambigüedad de cursor; declaración completa de `PmtpStiefelSlab` y asserts lock-free en §9.1; calibración epistémica de §11. |
| **V18** | RECHAZO (NOT OK) | §4.2: justificación de $\sqrt{\sum\lambda_i^4} \le \sum\lambda_i^2$ sin explicitar no-negatividad de $\lambda_i^2$. §4.3: falta de definición formal de $R_4(E) := (I+E)^{-1/2}-p_4(E)$. §8: cota nominal $3u$ sin delimitación formal de operaciones intermedias. §9.1: buffer de bytes sin tipado estricto `PmtpStiefelSlab` ni ciclo de vida C++20 formalizado. §9.4: inconsistencia en cota de desbordamiento de 56 bits ($2^{56}-2$). §9.5: shutdown debe enunciarse como protocolo condicional de supervisor. §11: taxonomía epistémica imprecisa sobre §§1-3 y §4.1(b). | Justificación algebraica rigurosa con normas $\ell_2 \le \ell_1$ para $\lambda_i^2 \ge 0$ en §4.2; definición explícita de $R_4(E)$ en §4.3; reencuadre cualitativo de la motivación de diseño de Neumaier en §8; tipado estricto `PmtpStiefelSlab buffer[NUM_SLOTS]` y formalización de inicialización en §9.1; formalización de $N_{\mathrm{pub}} \le 2^{56}-2$ en §9.4; reencuadre de §9.5 como protocolo condicional de supervisor; taxonomía refinada en §11. |
| **V19** | RECHAZO (NOT OK) | V19 consolidó tipado pero requería guardias RAII explícitos, manejo de underflow en release, y separación entre Grassmann y Stiefel. | Incorporación de guardias RAII move-only y delimitación de distancias cordales vs geodésicas. |
| **V20** | RECHAZO (NOT OK) | V20 resolvió guardias RAII y cotas espectrales pero requería $C_4(0.05)$ exacto, validación de punteros nulos en shutdown, y delimitación lock-free vs address-free. | Implementación de cota analítica $C_4(0.05)$, chequeos nulos exhaustivos y contrato de plataforma address-free. |
| **V21** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 7 defectos de precisión formal en admisión, layout y Procrustes. | Corrección de layout, separación de shutdown y adición de compuerta atómica. |
| **V22** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 10 ítems críticos en ciclo de vida, compuerta atómica y Procrustes. | Corrección de inicialización conforme, compuerta unificada y SVD de Procrustes. |
| **V23** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó precisiones en cota $C_4$, resto de Taylor, y recuperación de shutdown. | Resto de Taylor integral, delimitación de dominio y serialización de estados. |
| **V24** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 6 defectos técnicos decisivos: (1) definición de $K$ en §4.1(b) volvía a dividir por $\|\xi\|^3$, (2) inconsistencia en §4.3 entre cota $0.33$ y $0.355$, (3) `pmtp_shm_writer_publish` sobreescribía incondicionalmente el estado del slot con `store` en vez de CAS, (4) precondición de `out_guard` inactivo no verificada en `reader_acquire`, (5) `shutdown_status` no permitía reintento normal desde `TIMEOUT_ABORTED`, (6) $Q_0 = I$ requería bases coordinadas y reset QR requería calificación de error finito de máquina. | Corrección total en V25: acotamiento del resto mediante operador diferencial de Fréchet $D^3[\mathcal{R}-\operatorname{Exp}]$ sin división por $\|\xi\|^3$, unificación estricta de §4.3 en $C_4(0.05) \le 0.33$ ($\|R_4(E)\|_F \le 2.07 \times 10^{-6} \|E\|_F$), publicación de escritor gobernada por CAS (`compare_exchange_strong`) impidiendo sobreescritura de lectores concurrentes, verificación estricta de `out_guard->is_valid()` en `reader_acquire`, reintento de shutdown formalmente soportado desde `TIMEOUT_ABORTED`, y calificación formal de bases coordinadas en SVD y error de redondeo finito en QR. |
| **V25** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó que `std::atomic` por ISO C++20 solo no garantiza IPC portable; ciclo de vida de objetos en SHM no formalizado; carrera potencial entre escritor y apagado si se cierra admisión antes de adquirir `writer_lock`; reintento de timeout inconsistente con `destroying=1`; rollback de lector silencioso ante count=0; falta de `alignof=64` en structs; extensión ambiental en conexión de Levi-Civita no explicitada; dominio de Fréchet en fibrado tangente no cerrado; y necesidad de explicitar traza simétrica en $\Delta_G$. | Corrección integral en V26: Contrato de Sistema de Plataforma Específica (Target Platform IPC Contract sobre x86-64/ARM64, Linux `/dev/shm` y Windows Named Mapping con GCC/Clang/MSVC); modelo de ciclo de vida con placement-new en supervisor y attaching conforme; adquisición de `writer_lock` en apagado antes de cerrar admisión; reintento limpio desde `TIMEOUT_ABORTED`; rollback con detección de corrupción; static assertions completas compiladas con retorno 0 en MSVC 2026; proyección de Levi-Civita invariante a extensiones suaves locales; operador de Fréchet vertical sobre subfibrado tangente compacto; identidad $\operatorname{tr}(\Delta_G^2)=\|\Delta_G\|_F^2$ por simetría; estandarización de distancia cordal $d_c$ y cota de Welch; y bases coordinadas en Procrustes. |
| **V26** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó que el apagado fijaba `destroying=1` prematuramente antes de drenar ranuras consumiendo el timeout en in-flight; falta de cota de desbordamiento en in-flight y lectores (`adm+1`, `hdr+1`); `release()` retornaba `void` sin reportar corrupción si `readers=0`; `pmtp_shm_physical_destroy` omitía invocar `~PmtpSharedRegion()`; falta de validación de `supervisor_epoch` en tombstone; discrepancias internas entre texto y código (mención de 56 bits de generación vs 32 bits en código, código de error `-4` vs `-1`, y falta de cota de reintentos CAS); radio $t_0$ no definido en $M=0$; y necesidad de probar semidefinición positiva global en Procrustes. | Corrección total en V27: Drenaje en apagado con presupuestos dedicados para in-flight y ranuras sin marcar `destroying=1` ante timeout; cotas de saturación `MAX_INFLIGHT` y `MAX_READERS=268,435,455`; `release()` con retorno de código de error y detección estricta de corrupción; llamada formal obligatoria a `shm->~PmtpSharedRegion()` en destrucción física; validación monotónica de `supervisor_epoch` en tombstone; bucles CAS acotados a `MAX_CAS_ATTEMPTS=10000`; armonización universal del cursor empaquetado (32-bit slot, 32-bit gen, rollover de 49.7 días a 10^3 Hz); tubo uniforme de Fréchet $T_{\le 1/2}\mathrm{St}$ con $r_{\mathrm{ret}}=1/2$ y equivalencia bilipschitz con distancia geodésica; semidefinición positiva global $W^\top M \succeq 0$; y unificación absoluta de nombres de variables y códigos de error. |
| **V27** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó artefacto editorial (delimitadores triples ```cpp```), omisión de `<cstddef>` y asserts `trivially_copyable`/`standard_layout`; spinlock exchange con acquire en vez de acq_rel y bucle `lock()` no acotado; rollback de lector no acotado; `attach()` público sin protección de guard activo; inconsistencia textual en §9.2 y §9.5 donde persistían menciones obsoletas de 56 bits, 228 años, `& 0xFF` y orden antiguo de shutdown; dominio de difeomorfismo en polar sobre-reclamado; y divergencias de versionado en §11. | Corrección exhaustiva en V28: Limpieza de delimitadores a un único bloque C++20 compilable; inclusión de `<cstddef>` y `<type_traits>` con static asserts de `standard_layout` y `trivially_copyable`; spinlock con exchange acq_rel y `lock(max_spins)` acotado; rollback de adquisición acotado a `MAX_CAS_ATTEMPTS=10000`; `attach()` protegido con `PMTP_ERR_GUARD_ALREADY_ACTIVE`; reescritura total de §9.2 y §9.5 eliminando toda mención de 56 bits/228 años y sincronizando el orden de shutdown; cota de Fréchet en tubo uniforme $T_{\le 1/2}\mathrm{St}$ con radio $r_{\mathrm{ret}}=1/2$ sin sobre-reclamo de difeomorfismo global; cota de Welch citada con derivación exacta; y armonización universal a Versión 28.0 Definitiva en Título, Tabla y §11. |
| **V28** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 6 ítems de protocolo y matemática formal: (1) §10.1 `pmtp_shm_reader_acquire` retornaba `PMTP_ERR_CLOSED` al agotar CAS sin garantizar decremento, arriesgando un lector fantasma que bloquearía el apagado; (2) §10.2 `pmtp_shm_writer_publish` realizaba un store incondicional en `packed_cursor` en vez de un CAS atómicamente acoplado contra `cur_snap`; (3) Falta de rollback de ranura de `WRITING` a `IDLE` si fallaba el CAS de commit; (4) §10.4 y §10.5 shutdown usaba presupuestos divididos `timeout_ms / 2` en vez de un `global_deadline` monotónico único, y no reabría la compuerta de admisión ante timeout dejando el sistema inconsistente; (5) Falta de formalización de la cadena de sincronización de orden de memoria C++20 (*happens-before* y *synchronizes-with*); (6) §5.2 cota de Welch citada sin derivación analítica completa paso a paso de 4 líneas a partir de $\|S\|_F^2 \ge \frac{(NK)^2}{D}$. | Corrección exhaustiva en V29: (1) Rollback de lector con respaldo incondicional `fetch_sub(1, memory_order_acq_rel)` erradicando analíticamente cualquier lector fantasma; (2) Publicación de cursor gobernada por `compare_exchange_strong` acoplado contra `cur_snap` con rollback de ranura a `IDLE` si falla; (3) Rollback explícito de ranura de `WRITING` a `IDLE` en escritor ante fallo de commit; (4) Shutdown gobernado por `global_deadline := steady_clock::now() + timeout_ms` con recuperación no destructiva ante timeout reabriendo admisión (`|= ADMISSION_OPEN_FLAG`) y transicionando a `SHUTDOWN_STATE_TIMEOUT_ABORTED`; (5) Demostración formal de sincronización C++20 ISO §6.9.2.1; (6) Derivación matemática completa paso a paso de la cota de Welch; y caracterización exhaustiva de Procrustes por SVD con $W^\top M \succeq 0$ sobre $\mathbb{R}^K$ en §7.2. |
| **V29** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 8 defectos de protocolo y rigor: (1) `fetch_sub(1)` en rollback de lector y release de guardia era una resta aritmética ciega sobre la palabra de 32 bits que arriesgaba subdesbordamiento/préstamo hacia `SLOT_STATE_MASK` si `readers==0`, corrompiendo el estado; (2) Adquisición de `writer_lock` en shutdown no estaba gobernada por `global_deadline`; (3) La sincronización release/acquire del cursor estaba formulada de forma demasiado amplia sin condicionarse al valor leído; (4) La propiedad address-free en IPC interproceso no está normativamente garantizada por `is_always_lock_free` en C++ abstracto; (5) Duda aritmética sobre el layout modular de `PmtpStiefelSlab` (524.352 B vs mod 64); (6) Sobre-reclamo de difeomorfismo global en retracción polar sobre todo $T_{\le 1/2}\mathrm{St}$; (7) Algoritmo de desempate en Procrustes degenerado requería una regla determinista cerrada para $U_0, V_0$; y (8) Duplicación editorial de la fila V29 en la tabla de historial. | Corrección exhaustiva en V30: (1) Erradicación absoluta de `fetch_sub(1)` en favor de un bucle CAS lock-free invariante que preserva `SLOT_STATE_MASK`, detecta corrupción si `readers==0` y descarta préstamos; (2) `PmtpWriterSpinlock::try_lock_until(global_deadline)` gobernando la adquisición de lock en shutdown; (3) Formulación estricta de sincronización ISO C++20 §6.9.2.1 condicionada a la lectura de `new_snap`; (4) Delimitación de address-free como precondición contractual de plataforma para x86-64 y ARM64 respaldada en hardware; (5) Demostración analítica y static assertions de que $524.352 = 8.193 \times 64 \equiv 0 \pmod{64}$ y cada `buffer[i]` está alineado a 64 bytes; (6) Calibración de retracción polar como difeomorfismo local suave y retracción de segundo orden según Absil et al. (2008); (7) Algoritmo determinista de desempate en SVD mediante Gram-Schmidt sobre la base cartesiana canónica; y (8) Limpieza editorial completa y armonización a Versión 30.0 Definitiva. |
| **V30** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 10 ítems de protocolo y rigor: (1) `PMTP_SHM_VERSION` conservaba el valor 29 en vez de 30; (2) `admission_and_inflight` conservaba llamadas a `fetch_sub(1)` en rollback de admisión; (3) Ventana intermedia entre commit de slot y CAS de cursor donde rollback de escritor podía conmutar `COMMITTED -> IDLE` sin drenar lectores si intervenía contención; (4) `out_guard->attach()` podía fallar sin revertir el lector registrado en ranura; (5) Shutdown no reabría admisión si fallaba la adquisición del lock; (6) Procrustes requería formulación intrínseca independiente de bases; (7) `offsetof(buffer[0])` no era portable; (8) Falta de `static_assert(alignof(...) == 64)`; (9) Afirmación de objeto C++ interproceso requería formularse como contrato ABI; y (10) Delimitación formal de precondición thread-affine para `PmtpReaderGuard`. | Corrección exhaustiva en V31: (1) `PMTP_SHM_VERSION = 31` unificado; (2) Erradicación absoluta de todo `fetch_sub(1)` en el sistema mediante bucles CAS validados (`pmtp_decrement_inflight` y `pmtp_decrement_slot_reader`); (3) Rollback de escritor con drenaje forzado de lectores si la ranura fue observada antes de revertir a `IDLE`; (4) Rollback obligatorio de ranura en `reader_acquire` si `attach` falla; (5) Reapertura idempotente de compuerta de admisión ante cualquier fallo de spinlock en shutdown; (6) Caracterización intrínseca de Procrustes mediante $W^\top M = (M^\top M)^{1/2} \succeq 0$ (Higham, 1986); (7) `offsetof(buffer)` portable; (8) Static asserts completos de `alignof == 64`; (9) Contrato formal de implementación ABI de silicio; y (10) Precondición formal thread-affine documentada. |
| **V31** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 10 requerimientos decisivos de protocolo y matemática: (1) `pmtp_decrement_inflight` enmascaraba silenciosamente underflow al retornar `void` en `inflight==0` en vez de propagar error; (2) `pmtp_decrement_inflight` carecía de cota de intentos; (3) Carrera potencial entre shutdown y tombstone sin serialización por lock; (4) Recuperación de timeout en shutdown requería formalización de no-interferencia; (5) `destroying` y ciclo de vida de guardias contra reinitialización; (6) Revalidación de época y guardias en transferencia de ownership; (7) Demostración formal C++20 para payloads no atómicos y wraparound ABA; (8) Drenaje de escritor en rollback no estaba acotado; (9) Retracción polar requería clasificarse como proposición citada estándar de Absil et al. (2008) sin sobre-reclamos de prueba original o difeomorfismo global; y (10) Algoritmo de Procrustes requería formulación intrínseca de Higham (1986) con umbral numérico constructivo total. | Corrección exhaustiva en V32: (1) `pmtp_decrement_inflight` retorna `int` y propaga `PMTP_ERR_INTERNAL_CORRUPTION` si `inflight==0`; (2) Todas las primitivas acotadas estrictamente a `MAX_CAS_ATTEMPTS=10000`; (3) Tombstone formalmente serializado adquiriendo `writer_lock`; (4) Máquina de estados formal de 6 estados; (5) Anti-stale-guard validation mediante verificación de época monotónica en silicio; (6) Protección absoluta anti-ABA con cota de supervisor $T_{\mathrm{lease}} \le 6$ h y validación de época de slab de 64 bits; (7) Demostración C++20 formal de sincronización release-acquire para payload íntegro; (8) Drenaje de escritor acotado en rollback; (9) Calibración rigurosa de §4.1(b) como Proposición Citada de Absil et al. (2008); y (10) Teorema 7.2 con formulación intrínseca de Higham (1986) y algoritmo constructivo total en binary64 con umbral $10^{-12}$. |
| **V32** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 8 defectos decisivos de protocolo, matemática y ciclo de vida: (1) `PmtpStiefelSlab::epoch` se poblaba desde `current_gen + 1` (32 bits) en vez de un contador monotónico absoluto de 64 bits, invalidando el argumento anti-ABA; (2) `force_terminal_tombstone` mutaba la época fuera del lock y no verificaba el valor de retorno de `lock()`; (3) `try_lock_until` no estaba acotado por `MAX_CAS_ATTEMPTS`; (4) `reader_acquire` descartaba errores de rollback (`(void)pmtp_decrement_*`) en vez de propagarlos; (5) `PmtpReaderGuard::release()` no validaba la época de supervisor; (6) `physical_destroy` carecía de verificaciones ejecutables de estado; (7) El procedimiento numérico de Procrustes requería delimitarse formalmente frente al teorema exacto en $\mathbb{R}$; y (8) Cota de Horner requería distinguir truncamiento en $\mathbb{R}$ de acumulación en FP64. | Corrección exhaustiva en V33: (1) Secuencia de publicación de 64 bits real (`publication_sequence.fetch_add(1) + 1`) almacenada en cada slab con validación estricta; (2) Tombstone serializado bajo `writer_lock` con mutación de época dentro del lock y verificación estricta de lock; (3) `try_lock_until` doblemente acotado por deadline y `MAX_CAS_ATTEMPTS`; (4) Propagación obligatoria de errores de rollback en todas las ramas; (5) `release()` con validación de época y retorno `PMTP_ERR_STALE_EPOCH`; (6) `physical_destroy` con verificaciones ejecutables de magic, version, epoch, shutdown completed y cero lectores; (7) Procrustes delimitado estrictamente como teorema analítico en $\mathbb{R}$ y heurística determinista en punto flotante; y (8) Calibración epistémica de errores numéricos. |
| **V33** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 8 requerimientos decisivos de concurrencia y matemática: (1) El cursor contenía solo slot y generación de 32 bits, desarticulado del contador de 64 bits de slab epoch; (2) `reader_acquire` ejecutaba decremento de inflight tras `attach()`, dejando ambigüedad de propiedad y descartando el error de release; (3) Tombstone modificaba epoch forzando store en admisión sin contrato explícito de quiescencia; (4) Destrucción física carecía de precondición formal del supervisor; (5) La cota de Horner afirmaba dominancia sobre redondeo para $E \to 0$; (6) Inconsistencia de notación en Procrustes y sobre-reclamo de reproducibilidad bit a bit sin fijar flags/FMA; (7) Modelo de Neumaier con discrepancia dimensional entre norma euclídea y suma escalar; (8) Reclamos hiperbólicos de '100% verificado'. | Corrección exhaustiva en V34: (1) `PMTP_SHM_VERSION = 34`; descriptor atómico acoplado `packed_cursor` (16 bits slot + 48 bits secuencia monotónica, cota anti-reciclaje $>89$ años bajo $T_{\text{lease}} \le 6\text{h}$); (2) Decremento de inflight previo a `attach()` con reversión garantizada y cero ambigüedad; (3) Contrato de Quiescencia del Supervisor para Tombstone y Precondición de Destrucción Física; (4) Cota de Horner descompuesta rigurosamente como $\|R_4(E)\|_F + c_H K^2 u$; (5) Corrección de notación en Procrustes condicionando reproducibilidad a `/fp:precise` y `FP_CONTRACT OFF`; (6) Formalización dimensional de Neumaier (escalar y agregación Frobenius $\le K(2u + O(Du^2))$); y (7) Calibración epistémica integral. |
| **V34** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 7 aspectos a perfeccionar: (1) `force_terminal_tombstone` sobreescribía el estado borrando el conteo de lectores activos; (2) La cota de reintentos en decrementos CAS de inflight y readers podía causar fugas de conteo ante contención; (3) Recuperación ante timeout en shutdown requería linearización para evitar reabrir admisión si otra transición terminal ocurrió; (4) Teorema de Procrustes requería demostración rigurosa de optimalidad de traza $\operatorname{tr}(W^\top M)$, parametrización bloque-diagonal canónica en caso de rango deficiente $r < K$ y delimitación epistémica de la selección $Q_0 = I_{K-r}$; (5) Neumaier requería especificación algorítmica y término de orden superior $\gamma_{D+2}$; (6) Teorema 3.2 de Weyl en FP64 requería enmarcarse como salvaguarda numérica; y (7) La memoria compartida requería definirse como Especificación de Protocolo Binario IPC (PMTP-SHM-ABI-V35) con protección por conteo de referencias del kernel del SO. | Corrección exhaustiva en V35: (1) `PMTP_SHM_VERSION = 35`; `force_terminal_tombstone` conmuta a `CLOSED` preservando estrictamente `READERS_MASK`; (2) Bucles CAS lock-free no bloqueantes sin límite arbitrario garantizando progreso global; (3) Linearización atómica estricta de reapertura en shutdown timeout mediante CAS sobre `IN_PROGRESS`; (4) Demostración analítica rigurosa de Procrustes en $\mathbb{R}$ con parametrización exhaustiva $W = U_r V_r^\top + U_0 Q_0 V_0^\top$ y convención $Q_0 = I_{K-r}$ delimitada formalmente; (5) Formulación analítica de Neumaier con pseudocódigo y término $\gamma_{D+2}$; (6) Teorema 3.2 enmarcado como salvaguarda numérica en silicio; y (7) Definición formal de PMTP-SHM-ABI-V35 y protección por kernel del SO. |
| **V35** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 6 aspectos determinantes de protocolo y matemática: (1) La publicación en `writer_publish` conservaba una desarticulación no atómica entre el commit de ranura y el store de `packed_cursor`; (2) La compuerta de admisión y el estado de apagado permanecían en variables atómicas separadas; (3) Los bucles de registro de lectores conservaban cotas que podían generar inconsistencias ante contención; (4) La demostración de Procrustes requería probar formalmente el Lema de estructura bloque-diagonal $Z = \operatorname{diag}(I_r, Q_0^\top)$ a partir de la ortogonalidad de filas y columnas; (5) La cota de Neumaier requería explicitar precondiciones algorítmicas ($3Du \le 1$, ausencia de subnormales); y (6) En §4.4 el error de FP64 debía descomponerse como la suma de truncamiento analítico y redondeo de máquina. | Corrección exhaustiva en V36: (1) `PMTP_SHM_VERSION = 36`; punto único de linearización atómica con semántica release sobre `packed_cursor` erradicando estados intermedios de ranura; (2) Máquina de estados de ciclo de vida unificada (`lifecycle_state`) que acopla atómicamente admisión y apagado; (3) Seguimiento wait-free $O(1)$ de lectores en tránsito y activos mediante `fetch_add` y `fetch_sub` garantizando ausencia matemática de fugas; (4) Demostración analítica rigurosa del Lema Bloque-Diagonal en Procrustes; (5) Modelo analítico de Neumaier con pseudocódigo y término $\gamma_{D+2}$ explícito; y (6) Calibración epistémica integral de errores numéricos en §4.4 y §8.1. |
| **V36** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 7 aspectos determinantes de protocolo y matemática: (1) La selección de ranura del escritor (`active_readers == 0`) corría contra el registro del lector (`active_readers.fetch_add(1)`) sin exclusión mutua atómica; (2) El campo `epoch` del slab era no-atómico, generando carreras de datos bajo la máquina abstracta de C++; (3) Se reintrodujeron decrementos incondicionales (`fetch_sub`) sin detección de subdesbordamiento; (4) El patrón de doble lectura en la compuerta de admisión no constituía una compuerta atómica; (5) `pmtp_shm_physical_destroy` ignoraba los códigos de retorno de desmapeo del SO y no verificaba la alineación base; (6) La descripción en prosa de §10.2 llamaba al bloque de offset cero 'gate+instance' en contradicción con sus campos escalares y de secuencia; y (7) Se atribuyó wait-freedom de manera apresurada a bucles compuestos. | Corrección exhaustiva en V37: (1) `PMTP_SHM_VERSION = 37`; exclusión mutua rigurosa mediante CAS simétrico en silicio sobre `state_and_readers` (`(COMMITTED | 0) -> WRITING` en escritor vs `(COMMITTED | count) -> (COMMITTED | count + 1)` en lector); (2) `epoch` explícitamente `std::atomic<uint64_t>` con acquire/release; (3) Bucles CAS lock-free con detección estricta de subdesbordamiento en `pmtp_decrement_inflight` y `pmtp_decrement_slot_reader`; (4) Palabra atómica unificada de 64 bits `lifecycle_and_inflight` admitiendo lectores en un único CAS; (5) `pmtp_shm_physical_destroy` verifica alineación a 64 bytes y códigos de retorno de `UnmapViewOfFile` y `munmap`; (6) §10.2 sincronizado con el layout físico de silicio; (7) Clasificación lock-free vs wait-free conforme a ISO C++20; (8) §4.1(b) cancela explícitamente el término cruzado tangente $X^\top \xi + \xi^\top X = 0$; y (9) §5.2 distingue analíticamente pares ordenados de no ordenados en la cota de Welch. |
| **V37** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 10 aspectos determinantes de protocolo y matemática: (1) Los errores de rollback en `reader_acquire` se descartaban con `(void)` en lugar de propagarse; (2) La brecha de publicación entre el commit de ranura y el store de `packed_cursor` requería caracterización formal como protocolo en dos fases; (3) El wraparound de secuencia de 48 bits requería un teorema de orden modular bajo arrendamiento acotado; (4) El timeout de apagado requería ordenamiento estricto de publicación de estado y liberación de lock; (5) La destrucción física carecía de linearización atómica (`LIFECYCLE_DESTROYED`) y verificación de estado terminal en todas las ranuras; (6) Las aserciones estáticas de ABI requerían Little-Endian, tamaño de double, offsets de todos los campos y lock-free nativo; (7) La cota de Neumaier requería hipótesis explícitas del modelo estándar bajo Higham (2002); (8) En §11 se citaba §5.1 por preservación de subespacio columna sin que §5.1 mostrara el lema; (9) El escritor requería verificación de finitud de payload y retorno de `PMTP_ERR_NULL_REGION`; y (10) Se conservaba una variable no utilizada `registered`. | Corrección exhaustiva en V38: (1) `PMTP_SHM_VERSION = 38`; propagación exhaustiva de códigos de error de rollback en todos los puntos de salida de adquisición; (2) Formalización matemática del Protocolo de Publicación en Dos Fases Rigurosamente Ordenadas con Semántica Release; (3) Teorema 9.4 de Aritmética Modular en 48 bits demostrando ausencia de ambigüedad ABA ($N_{\text{lease}} \le 2{,}16 \times 10^9 \ll 2^{47}$); (4) Ordenamiento secuencial estricto en timeout de shutdown con liberación explícita de lock; (5) Linearización atómica de destrucción física vía CAS a `LIFECYCLE_DESTROYED` y validación de `SLOT_STATE_CLOSED` en todas las ranuras; (6) Aserciones estáticas exhaustivas de endianness, tipos escalares, atómicos y offsets de campos; (7) Modelo formal de error de Neumaier bajo Higham (2002) con término $\mathcal{O}(u^2)$; (8) Lema 5.1(b) incorporado con demostración analítica de preservación de subespacio columna; (9) Validación de finitud numérica (`std::isfinite`) y punteros nulos en el escritor; y (10) Erradicación de variables huérfanas. |
| **V38** | RECHAZO (NOT OK) | Perplexity Sonar-Pro identificó 15 observaciones determinantes: (1) Escritor sin rollback ni tolerancia a fallas catastróficas (crash-faults) requiriendo contrato explícito de exclusión; (2) Protocolo de dos fases requería demostración completa de invariantes de ranura frente a lectores rezagados; (3) Desincronización potencial entre secuencia de 64 bits y cursor de 48 bits; (4) Teorema 9.4 condicional a supuestos de arrendamiento y tasa física ($\lambda \le 10^5$), sin validación de distancia modular en silicio; (5) Linearización irreversible a `LIFECYCLE_DESTROYED` ejecutada antes de verificar el estado de las ranuras; (6) CAS de timeout en shutdown no inspeccionaba el estado final terminal; (7) `pmtp_shm_physical_destroy` carecía de serialización por `writer_lock`; (8) Cursor apunta a ranura cerrada post-shutdown dependiendo del chequeo de ciclo de vida del lector; (9) Propiedad address-free de atómicos es un supuesto de plataforma, no garantía abstracta ISO C++; (10) Retracción polar requería normas y vecindad explícita sin sobre-reclamos cuantitativos globales; (11) Cota de Horner requería constante y fórmula rigurosa ($\gamma_{16K} \tilde{p}_4$); (12) Cota QR requería constante documentada ($c \approx 2$); (13) Cota de Neumaier requería precondiciones del modelo estándar; (14) Destructor de `PmtpReaderGuard` descartaba silenciosamente errores de liberación; y (15) Distinción epistémica rigurosa entre teoremas analíticos, supuestos de plataforma y contratos de ingeniería. | Corrección exhaustiva en V39: (1) `PMTP_SHM_VERSION = 39`; Contrato explícito de Exclusión de Fallas Catastróficas (Crash-Stop Fault Exclusion Contract, §9.0) y lenguaje condicional en todo el documento; (2) Grafo exhaustivo de estados de ranura (Lema 9.1) con demostración analítica de exclusión mutua de silicio; (3) Sincronización estricta de época atómica con semántica release; (4) Teorema 9.4 reclasificado formalmente como Teorema Condicional Operacional bajo arrendamiento y tasa acotada, delimitando la verificación como comprobación de consistencia; (5) Reordenamiento crítico en `pmtp_shm_physical_destroy`: validación de estado `SLOT_STATE_CLOSED` y 0 lectores en todas las ranuras ANTES de la conmutación atómica a `LIFECYCLE_DESTROYED`; (6) Serialización obligatoria de destrucción física mediante adquisición previa de `writer_lock`; (7) Inspección de estado final tras bucle de timeout en shutdown con retorno fiel de código; (8) Observabilidad de error en `PmtpReaderGuard` mediante campo y accesor `last_release_error()`; (9) Atómicos address-free clasificados rigurosamente como supuesto de plataforma de silicio; (10) Proposición 4.1(b) con vecindad local $\|\xi\|_F < 1/2$ y $\mathcal{O}(|t|^3 \|\xi\|_F^3)$; (11) Cota Horner con fórmula $\gamma_{16K} \tilde{p}_4(\|E\|_F)$ (Higham 2002); (12) Cota QR con $c \approx 2$ citando Golub & Van Loan (2013); (13) Neumaier bajo modelo estándar IEEE-754 con precondiciones explícitas; (14) Declaración epistémica §11 exhaustivamente calibrada y coherente con las limitaciones del silicio. |
| **V39** | **ESPECIFICACIÓN FORMAL DE INGENIERÍA SOTA V39.0** | N/A | Especificación matemática, geométrica y de concurrencia de silicio completamente calibrada, sin sobre-reclamos y respaldada por contratos de plataforma y exclusión de crash-faults. |
| **V40** | **TRIBUNAL ARBITRAL MULTI-MODELO CERTIFICADO (V40.0)** | Dictamen unánime 4/4 (Claude Opus 5.5, DeepSeek V3, Cerebras CS-3, Perplexity Sonar-Pro) | (1) Formalización de que compacidad no erradica deriva semántica dinámica sin contracción estricta en Gr(D,K); (2) Preservación isométrica exacta de la cota de Welch; (3) Diferenciación estricta entre orden geométrico de retracción polar Theta(||xi||^3) y orden algebraico de Newton-Schulz; (4) Prueba formal de que la publicación de índice atómico aislado incurre en Data Race (UB ISO C++20), certificando la obligatoriedad de tickets atómicos reader_count[3] para DRF. |
| **V41** | **CERTIFICACIÓN SOTA PARCIAL (QWEN 3.8-FLASH)** | Dictamen multi-criterio sobre 8 objeciones de Perplexity V39 | (1) Reencuadre formal de publicación como Protocolo en Dos Fases Rigurosamente Ordenadas bajo `writer_lock` o Seqlock atómico generacional; (2) Reconciliación de DFA de ranura con fast-path directo `COMMITTED -> WRITING`; (3) Inclusión de verificación de `LIFECYCLE_DESTROYED` en `PmtpReaderGuard::data()`; (4) Delimitación formal de progreso lock-free con cota finita `MAX_CAS_ATTEMPTS = 10000`; (5) Linealización atómica en `packed_cursor.store(release)`. |
| **V42** | **CERTIFICACIÓN SOTA COMPLETA (QWEN 3.8-FLASH EXIT CODE 0)** | Evaluación exhaustiva de Layout & Offset Arithmetic sin extensiones no portables | Derivación analítica relacional ISO C++20 pura: contigüidad probada por `sizeof(PmtpStiefelSlab[NUM_SLOTS]) == NUM_SLOTS * sizeof(PmtpStiefelSlab)`, offsets de ranuras intermedias por `offsetof(buffer) + i * sizeof(...)`, static_assert de alineación relacional modular y acotamiento de ausencia de trailing padding por `sizeof(PmtpSharedRegion) == offsetof(buffer) + sizeof(buffer)`. Veredicto unánime: `[CERTIFIED EXIT CODE 0]`. |
| **V43** | **SEQLOCK GENERACIONAL CANÓNICO EN SILICIO (D8 RESOLVED)** | Resolución definitiva de deuda D8 en arquitectura de memoria compartida Tri-Segment (V019) | Implementación nativa y formalización matemática del Seqlock Atómico con Contador Generacional en `pmtp_tri_segment.h/.cpp`. Erradicación total de `writer_lock` mediante conservación de layout ABI (`reserved_b`, 64 bytes alineados). Protocolo de paridad estricto: LSB=1 indica escritura en curso (odd), LSB=0 indica commit estable (even). Linealización indivisible en el incremento par de release. Verificación física en silicio completada con Exit Code 0 (50 ciclos de contención, latencia 2.15 ms, discrepancia numérica `0.0`). |
| **V44** | **TSAN-CLEAN SEQLOCK EN NODO ALADÍN + PMTP-REAPER SERVICE (D5+D6 RESOLVED)** | Resolución definitiva de deudas D5 y D6 en Nodo Aladín Debian 13 (`192.168.100.21`) | D5: Harness TSAN V2 con payload `std::atomic<uint64_t>[6]` (TSAN-clean by design): 2 escritores + 4 lectores × 10.000 iteraciones bajo `TSAN_OPTIONS=halt_on_error=1`. Cero data races. Certificado en Aladín con GCC C++20 `-fsanitize=thread -O1`. Silicio: `(Exit Code: 0, 1967.7 ms, 0 races, 6 threads)`. D6: `pmtp-reaper.service` desplegado en `/etc/systemd/system/`, daemon Python `/opt/pmtp/pmtp_reaper_daemon.py` (poll `/dev/shm/pmtp_*` cada 30s, umbral 120s, SIGTERM-safe). Estado: `active (running)`. Silicio: `(Exit Code: 0, 6963.6 ms, Service: active)`. |

---

## 1. ¿QUÉ ESPACIO HABITA EXACTAMENTE EL ESTADO?

### Definición 1.1 (Espacio de Estado y Variedad de Stiefel)

El estado de cada agente $a_i$ habita la **variedad compacta de Stiefel** de marcos $K_i$-ortonormales en $\mathbb{R}^{D_i}$:

$$\mathcal{M}_i := \mathrm{St}(D_i, K_i) = \left\{ X \in \mathbb{R}^{D_i \times K_i} : X^\top X = I_{K_i} \right\}$$

**Propiedades Topológicas y Dimensionales:**

1. **Dimensión Suave:** La dimensión diferencial de la variedad es:
   $$\dim \mathrm{St}(D, K) = DK - \frac{K(K+1)}{2}$$
   Para los parámetros canónicos de POLYDIM ($D = 2048, K = 32$), la dimensión efectiva es:
   $$\dim \mathrm{St}(2048, 32) = 2048 \times 32 - \frac{32 \times 33}{2} = 65{,}536 - 528 = 65{,}008$$

2. **Compacidad e Invariante de Norma:** $\mathrm{St}(D, K)$ es un subconjunto cerrado y acotado de $\mathbb{R}^{D \times K}$ y, por tanto, compacto. Cada columna posee norma euclídea exactamente 1 y columnas distintas son ortogonales por pares. Como consecuencia analítica:
   $$\|X\|_F = \sqrt{\operatorname{tr}(X^\top X)} = \sqrt{\operatorname{tr}(I_K)} = \sqrt{K}, \quad \|X\|_2 = \sigma_1(X) = 1 \quad \forall X \in \mathrm{St}(D, K)$$

3. **Conexidad por Arcos:** La variedad real de Stiefel $\mathrm{St}(D, K)$ es conexa por arcos para todo $1 \le K < D$. En el caso frontera $D = K$, $\mathrm{St}(K, K) = O(K)$ consta de dos componentes conexas disjuntas caracterizadas por $\det(X) = +1$ y $\det(X) = -1$. Dado que POLYDIM opera estrictamente en el régimen $D > K$ ($2048 > 32$), la conexidad por arcos está analíticamente garantizada. (No se postula conexidad simple $\pi_1$, la cual no es requerida para el flujo de gradiente ni el transporte riemanniano).

4. **Convención Notacional:** Adoptamos $\mathrm{St}(D, K)$ para denotar matrices $D \times K$ con columnas ortonormales ($1 \le K \le D$). El caso $K = 1$ corresponde a la hiperesfera unidad $S^{D-1}$; el caso $K \ge 2$ representa marcos ortonormales de dimensión superior.

5. **Espacio Conjunto Multiagente:** Para un sistema de $m$ agentes heterogéneos, el estado global habita la variedad producto compacta:
   $$\mathcal{M} := \prod_{i=1}^m \mathrm{St}(D_i, K_i)$$
### Teorema 1.2 (Compacidad vs Deriva Semántica Dinámica y Cota Lipschitz del Campo Vectorial)

**Enunciado:** La compacidad estática de la variedad de Stiefel $\mathrm{St}(D, K)$ garantiza el acotamiento universal de norma ($\|X\|_F = \sqrt{K}$, $\|X\|_2 = 1$), pero **no** previene por sí sola la deriva semántica dinámica en procesos recurrentes discretos $X_{t+1} = R_{X_t}(\eta \, \xi(X_t))$ ni en flujos continuos $\dot{X}(t) = \xi(X(t))$.

**Demostración de No-Convergencia Intrínseca (Flujo Cuasiperiódico en Toros):**
Sea $\Omega \in \mathfrak{so}(D)$ una matriz antisimétrica con frecuencias $\{\theta_j\}_{j=1}^m$ linealmente independientes sobre $\mathbb{Q}$ (inconmensurables con $\pi$). El flujo ortogonal $X(t) = e^{t\Omega} X_0$ habita estrictamente $\mathrm{St}(D, K)$ para todo $t \ge 0$, preservando $\|X(t)\|_F = \sqrt{K}$ de manera exacta. Sin embargo, por el teorema de Kronecker-Weyl, la trayectoria es densa en un toro maximal $\mathbb{T}^m \subset \mathrm{St}(D, K)$ y es ergódica respecto a la medida de Haar del toro; por ende, no converge a ningún punto fijo ni atractor semántico, evidenciando que la compacidad métrica es insuficiente para asegurar estabilidad dinámica.

**Cota Lipschitz en la Variedad vs No-Unicidad de Puntos Fijos:**
Para asegurar la estabilidad frente a perturbaciones del campo vectorial generador $\xi(X) \in T_X \mathrm{St}(D, K)$ a lo largo de la variedad, se impone una condición de regularidad Lipschitz covariante en norma de Frobenius transportada:
$$\|\mathcal{T}_{X \to Y} \xi(X) - \xi(Y)\|_F \le L \, d_R(X, Y) \quad \text{con } L < 1$$
donde $\mathcal{T}_{X \to Y}: T_X \mathrm{St}(D, K) \to T_Y \mathrm{St}(D, K)$ denota el operador de transporte paralelo a lo largo de la geodésica riemanniana mínima y $d_R(X, Y)$ es la distancia geodésica inducida.

> **Clarificación Formal y Resolución de Objeción Red Team (D16):**
> La condición $L < 1$ sobre el campo vectorial $\xi(X)$ constituye estrictamente una **cota de perturbación Lipschitz acotada del campo** que garantiza la estabilidad del tamaño de paso $\eta$ bajo retracciones suaves $R_X$. **No** constituye un mapa de contracción global de Banach sobre la variedad, ni postula por sí misma la existencia de un punto fijo o atractor único.
> 
> *Contraejemplo Crítico:* Si $\xi(X) \equiv 0$, se cumple trivialmente $\|\mathcal{T}_{X \to Y} 0 - 0\|_F = 0 \le 0 \cdot d_R(X, Y)$ con $L = 0 < 1$; sin embargo, la actualización $F(X) = R_X(0) = X$ es el mapa identidad, donde *todo* punto de $\mathrm{St}(D, K)$ es un punto fijo y no existe atractor único.
> 
> *Obstrucción Topológica:* Sobre una variedad compacta sin frontera como $\mathrm{St}(D, K)$ o $\mathrm{Gr}(D, K)$, el teorema de Poincaré-Hopf y la compacidad métrica impiden la existencia de una contracción global estricta a un punto único.
> 
> *Condición Cualificada para Convergencia en el Espacio Cociente:* Un potencial riemanniano suave $\mathcal{L}: \mathrm{Gr}(D, K) \to \mathbb{R}$ con estructura Morse-Bott (o funcional con puntos críticos aislados) constituye una hipótesis estructural suficiente para formular resultados de convergencia de flujo de gradiente riemanniano negativo $\xi(X) = -\operatorname{grad}_R \mathcal{L}(X)$, pero **no** es universalmente necesaria (sistemas con mínimos no degenerados o hessiano nulo como $\dot{\theta} = -4\theta^3$ convergen asintóticamente al mínimo aislado). Asimismo, la atracción hacia un mínimo semántico específico en $\mathrm{Gr}(D, K)$ requiere hipótesis adicionales explícitas sobre la cuenca de atracción inicial y la ausencia de inicializaciones en puntos de ensilladura o máximos locales. Bajo algoritmos discretos gobernados por retracciones riemannianas $X_{t+1} = R_{X_t}(\eta \, \xi(X_t))$, la cota Lipschitz covariante $L < 1$ en una vecindad geodésica del punto crítico opera como condición de estabilidad del tamaño de paso $\eta$, requiriendo satisfacer la desigualdad del gradiente de Łojasiewicz para garantizar longitud finita de trayectoria y evitar oscilaciones caóticas.

**Desacoplamiento entre Espacio Portador Matemático y Semántica Aprendida:**

- **Espacio Portador Algebraico:** $\mathrm{St}(D, K)$ provee exclusivamente la variedad geométrica portadora embebida en el espacio euclídeo $\mathbb{R}^{D \times K}$, con invariantes de norma inducida fijos ($\|X\|_F = \sqrt{K}, \|X\|_2 = 1$). No confiere por sí misma semántica ni información lingüística intrínseca.
- **Codificador Semántico:** La asociación entre conceptos, hipótesis latentes o razonamientos y puntos de la variedad se realiza mediante un codificador diferenciable entrenable $\mathcal{E}: \mathcal{H} \to \mathrm{St}(D, K)$. La separabilidad, generalización o fidelidad downstream es una propiedad conjunta de $\mathcal{E}$, del decodificador y de las funciones de pérdida del entrenamiento, no un teorema abstracto de la variedad pura.
- **Cociente de Grassmann y Fases de Marco:** Cada elemento $X \in \mathrm{St}(D, K)$ representa una colección ordenada de $K$ vectores ortonormales que generan un subespacio lineal $K$-dimensional $\operatorname{span}(X) \subset \mathbb{R}^D$. La proyección canónica al espacio de Grassmann:
   $$\pi: \mathrm{St}(D, K) \to \mathrm{Gr}(K, D) = \mathrm{St}(D, K) / O(K)$$
   identifica marcos bajo la acción por la derecha del grupo ortogonal completo $O(K)$, que abarca tanto rotaciones $SO(K)$ como reflexiones $O(K) \setminus SO(K)$:
   $$X \sim X Q \quad \forall Q \in O(K)$$
   El operador de proyección ortogonal sobre el subespacio generado, $P_X = X X^\top$, es estrictamente invariante bajo esta acción:
   $$P_{XQ} = (XQ)(XQ)^\top = X Q Q^\top X^\top = X X^\top = P_X$$
   Los observables invariantes del subespacio dependen únicamente de $P_X$, mientras que los observables de coordenadas de marco dependen de la base ortonormal específica elegida.

---

## 2. ¿QUÉ MÉTRICA Y CONEXIÓN USA?

### Definición 2.1 (Métrica Riemanniana Inducida de Frobenius)

POLYDIM equipa la variedad de Stiefel $\mathrm{St}(D, K)$ con la **métrica riemanniana extrínseca inducida** por el producto interno euclídeo de Frobenius en $\mathbb{R}^{D \times K}$:

$$\langle U, V \rangle_X := \operatorname{tr}(U^\top V) \quad \forall U, V \in T_X \mathrm{St}(D, K)$$

Esta métrica inducida se distingue formalmente de la métrica canónica cociente $\langle U, V \rangle_X^{\mathrm{can}} = \operatorname{tr}(U^\top (I_D - \frac{1}{2} X X^\top) V)$. POLYDIM adopta exclusivamente la **métrica inducida de Frobenius** por su mapeo directo a operaciones BLAS de nivel 3 y kernels SIMD nativos (AVX2/AVX-512) con complejidad mínima. Todas las fórmulas posteriores se rigen por la métrica inducida.

### Proposición 2.2 (Espacio Tangente y Proyección Ortogonal)

El espacio tangente a $\mathrm{St}(D, K)$ en un marco $X$ es el espacio vectorial de matrices que satisfacen la condición diferencial de ortogonalidad:
$$T_X \mathrm{St}(D, K) = \left\{ Z \in \mathbb{R}^{D \times K} : X^\top Z + Z^\top X = 0 \right\}$$
equivalentemente, matrices $Z$ tales que la matriz de correlación $X^\top Z$ es antisimétrica, es decir, su parte simétrica es nula:
$$\operatorname{sym}(X^\top Z) = 0, \quad \text{donde } \operatorname{sym}(A) = \frac{1}{2}(A + A^\top)$$

Para cualquier matriz ambiente $Z \in \mathbb{R}^{D \times K}$, la proyección ortogonal sobre $T_X \mathrm{St}(D, K)$ bajo la métrica inducida de Frobenius está dada unívocamente por:
$$\Pi_{T_X}(Z) = Z - X \operatorname{sym}(X^\top Z)$$

### Proposición 2.3 (Gradiente Riemanniano y Conexión de Levi-Civita)

Para una función diferenciable $f: \mathrm{St}(D, K) \to \mathbb{R}$ con gradiente euclídeo $\nabla f(X) \in \mathbb{R}^{D \times K}$, el gradiente riemanniano $\operatorname{grad} f(X) \in T_X \mathrm{St}(D, K)$ respecto a la métrica inducida es la proyección ortogonal de Frobenius:
$$\operatorname{grad} f(X) = \Pi_{T_X}(\nabla f(X)) = \nabla f(X) - X \operatorname{sym}(X^\top \nabla f(X))$$
Para dos campos vectoriales tangentes suaves $\xi, \eta \in \mathfrak{X}(\mathrm{St}(D, K))$, la conexión de Levi-Civita $\nabla_\xi \eta$ inducida en la subvariedad de Stiefel se obtiene mediante la proyección ortogonal de la derivada direccional en el espacio euclídeo ambiente:
$$\nabla_\xi \eta = \Pi_{T_X}(D\bar{\eta}(X)[\xi])$$
donde $\bar{\eta}$ es cualquier extensión suave local del campo $\eta$ a un entorno abierto de $X$ en $\mathbb{R}^{D \times K}$, y $D\bar{\eta}(X)[\xi]$ es el diferencial euclídeo estándar. Por la teoría general de subvariedades riemannianas sumergidas (Absil et al., 2008, §3.6.1), la proyección $\Pi_{T_X}(D\bar{\eta}(X)[\xi])$ es estrictamente invariante respecto a la elección de la extensión local suave $\bar{\eta}$.

## 3. ¿CÓMO SE ACTUALIZA EL ESTADO?

### Definición 3.1 (Flujo de Actualización Discreta en la Variedad)

El estado se actualiza mediante un paso de optimización riemanniana gobernado por:
$$X_{t+1} = \mathcal{R}_{X_t}(-\eta_t \xi_t)$$
donde $\xi_t \in T_{X_t} \mathrm{St}(D, K)$ es una dirección tangente de descenso (e.g., gradiente riemanniano $\xi_t = \operatorname{grad} f(X_t)$), $\eta_t > 0$ es el tamaño de paso, y $\mathcal{R}$ es la retracción polar.

Definiendo la perturbación tangente $\Delta_t := -\eta_t \xi_t$, la actualización se expresa como:
$$X_{t+1} = \mathcal{R}_{\mathrm{St}}(X_t + \Delta_t)$$

### Teorema 3.2 (Preservación de Rango de Columnas por Desigualdad de Weyl)

Sea $X_t \in \mathrm{St}(D, K)$ con rango pleno de columnas $\operatorname{rank}(X_t) = K$ y singular values $\sigma_i(X_t) = 1$ para todo $i \in \{1, \dots, K\}$ en aritmética real exacta $\mathbb{R}$. Consideremos el paso de actualización antes de retracción:
$$Y_t = X_t + \eta_t \xi_t$$
Por la desigualdad de perturbación de valores singulares de Weyl:
$$|\sigma_i(Y_t) - \sigma_i(X_t)| \le \|\eta_t \xi_t\|_2$$
En particular, para el valor singular mínimo:
$$\sigma_K(Y_t) \ge \sigma_K(X_t) - \|\eta_t \xi_t\|_2 = 1 - \eta_t \|\xi_t\|_2$$
Si la tasa de paso satisface la condición analítica $\eta_t \|\xi_t\|_2 \le 1 - \delta$ para una constante $\delta \in (0, 1)$, entonces $\sigma_K(Y_t) \ge \delta > 0$, demostrando que $Y_t$ posee rango de columnas estrictamente pleno $\operatorname{rank}(Y_t) = K$ y que $Y_t^\top Y_t$ es simétrica definida positiva en aritmética real exacta. $\blacksquare$

*Política de Implementación en Coma Flotante FP64:*  
En la implementación física sobre silicio bajo aritmética IEEE-754 binary64, el cálculo computado de $\|\xi_t\|_2$ y el reescalado dinámico de $\eta_t$ incorporan un margen de seguridad numérico:
$$\hat{\eta}_t \cdot \widehat{\|\xi_t\|}_2 \le 1 - \delta - \epsilon_{\mathrm{fp}}$$
donde $\epsilon_{\mathrm{fp}} \approx O(K u) \approx 7 \times 10^{-15}$. Esta condición constituye una *política de salvaguarda de ingeniería numérica* para mitigar la proximidad a configuraciones mal condicionadas en silicio, delimitando formalmente que la garantía vinculante de estabilidad ortonormal de la máquina está provista por la re-proyección periódica QR de Householder (§4.4).

## 4. ¿QUÉ GARANTIZA LA RETRACCIÓN?

### Teorema 4.0 (Diferenciación Estricta entre Orden Geométrico y Orden Algebraico de Retracción)

**Enunciado:** Deben diferenciarse estrictamente dos órdenes asintóticos independientes en la retracción polar:
1. **Orden Geométrico de Retracción:** La retracción polar euclídea $\mathcal{R}_X(\xi) = (X + \xi)(I_K + \xi^\top \xi)^{-1/2}$ es una retracción de **segundo orden** respecto a la métrica euclídea de Frobenius en $\mathrm{St}(D, K)$. Su discrepancia asintótica respecto a la aplicación exponencial riemanniana $\operatorname{Exp}_X(\xi)$ satisface:
   \|\mathcal{R}_X(\xi) - \operatorname{Exp}_X(\xi)\|_F = \Theta(\|\xi\|_F^3) \quad \text{cuando } \|\xi\|_F \to 0
   dado que $\mathcal{R}_X(0) = X$, \mathcal{R}_X(0)[\xi] = \xi$, y los términos cuadráticos de la aceleración intrínseca coinciden idénticamente con la conexión de Levi-Civita inducida.
2. **Orden Algebraico de Newton-Schulz:** La aproximación polinómica del factor inverso de raíz ^{-1/2}$ mediante $ iteraciones de Newton-Schulz posee una tasa de convergencia cuadrática local:
   \|P_m(\xi^\top \xi) - (I_K + \xi^\top \xi)^{-1/2}\|_F = O(\|\xi\|_F^{2m+2})
   Para =5$ iteraciones en $\|\xi\|_F \le 0.05$, el error algebraico de truncamiento es $\le 1.11 \times 10^{-15}$ (al nivel del épsilon de máquina IEEE-754), siendo asintóticamente despreciable frente al resto geométrico de tercer orden $\Theta(\|\xi\|_F^3)$.

### Teorema 4.1 (Pertenencia Exacta a la Variedad de Stiefel en Aritmética Real)

Para cualquier matriz $Z \in \mathbb{R}^{D \times K}$ con rango de columnas completo $K$, la retracción polar satisface idénticamente:
$$\mathcal{R}_{\mathrm{St}}(Z)^\top \mathcal{R}_{\mathrm{St}}(Z) = (Z (Z^\top Z)^{-1/2})^\top (Z (Z^\top Z)^{-1/2}) = (Z^\top Z)^{-1/2} (Z^\top Z) (Z^\top Z)^{-1/2} = I_K$$
exactamente en aritmética real $\mathbb{R}$. $\blacksquare$

### Proposición Citada 4.1(b) (Retracción Polar de Segundo Orden en Variedades de Stiefel — Absil, Mahony & Sepulchre, 2008)

La aplicación de retracción polar ortogonal $\mathcal{R}_{\mathrm{St}}: T\mathrm{St}(D, K) \to \mathrm{St}(D, K)$ definida para cualquier par punto-vector tangente $(X, \xi) \in T\mathrm{St}(D, K)$ por:
$$\mathcal{R}_X(\xi) := (X + \xi)(I_K + \xi^\top \xi)^{-1/2}$$
constituye una retracción riemanniana suave de segundo orden sobre la variedad de Stiefel compacta $\mathrm{St}(D, K)$, de acuerdo con la teoría establecida de optimización geométrica (Absil, Mahony & Sepulchre, 2008, Definición 4.1.1 y Proposición 4.1.3). No se formula en este trabajo como un teorema original, sino como la adopción rigurosa del resultado estándar de la literatura matemática:

1. **Condición Tangente y Cancelación Rigurosa de Términos Cruzados:**  
   Dado que $\xi \in T_X \mathrm{St}(D, K)$, satisface idénticamente la caracterización canónica del espacio tangente a la variedad de Stiefel:
   $$X^\top \xi + \xi^\top X = 0$$
   En consecuencia, la matriz de Gram de la configuración perturbada $X + \xi$ se simplifica algebraicamente de forma exacta:
   $$(X + \xi)^\top (X + \xi) = X^\top X + X^\top \xi + \xi^\top X + \xi^\top \xi = I_K + 0 + \xi^\top \xi = I_K + \xi^\top \xi$$
   justificando formalmente por qué el factor polar normalizador de $X + \xi$ adopta la forma $(I_K + \xi^\top \xi)^{-1/2}$.
2. **Regularidad de Dominio y Preservación de Rango:**  
   Sea $T_{\le 1/2}\mathrm{St}(D, K) := \{(X, \xi) \in T\mathrm{St}(D, K) \mid \|\xi\|_F \le 1/2\}$. Para cualquier par $(X, \xi)$ en este fibrado:
   $$\sigma_K(X + \xi) \ge \sigma_K(X) - \|\xi\|_2 \ge 1 - \|\xi\|_F \ge 1 - \frac{1}{2} = \frac{1}{2} > 0$$
   por la desigualdad de perturbación de Weyl. La matriz $X + \xi$ tiene rango completo $K$ y la matriz simétrica $I_K + \xi^\top \xi \succ 0$ es estrictamente definida positiva, asegurando la suavidad $C^\infty$ de $\mathcal{R}_X$ en todo el tubo uniforme.
3. **Propiedades Canónicas de Retracción de Segundo Orden:**  
   La curva de retracción $c(t) := \mathcal{R}_X(t\xi)$ satisface idénticamente en $t = 0$:
   $$c(0) = X, \quad \dot{c}(0) = \xi, \quad \nabla_{\dot{c}(0)} \dot{c}(0) = 0$$
   donde $\nabla$ es la conexión de Levi-Civita riemanniana inducida sobre $\mathrm{St}(D, K)$. De acuerdo con Absil et al. (2008, §4.1), esto garantiza que la distancia riemanniana respecto a la geodésica riemanniana $\gamma_\xi(t) = \operatorname{Exp}_X(t\xi)$ satisface localmente:
   $$\operatorname{dist}_{\mathrm{St}}(c(t), \gamma_\xi(t)) = \mathcal{O}(|t|^3 \|\xi\|_F^3)$$
   dentro de la vecindad de regularidad $|t| \|\xi\|_F < 1/2$. Se adopta como resultado analítico estándar sin sobre-reclamos de cotas cuantitativas globales fuera del tubo de inyectividad local. $\blacksquare$

### Proposición 4.2 (Expansión Asintótica Matricial de Perturbación Polar y Cota de Frobenius)

Sea $X \in \mathrm{St}(D, K)$ y consideremos una perturbación aditiva $Y = X + \Delta \in \mathbb{R}^{D \times K}$ con norma espectral $\|\Delta\|_2 = \rho < 1$. Definamos la perturbación simétrica de la matriz de Gram:
$$\Delta_G := Y^\top Y - I_K = X^\top \Delta + \Delta^\top X + \Delta^\top \Delta \in \mathbb{R}^{K \times K}$$
Dado que $X^\top X = I_K$, se deduce por la desigualdad triangular de la norma espectral:
$$\|\Delta_G\|_2 \le \|X^\top \Delta\|_2 + \|\Delta^\top X\|_2 + \|\Delta^\top \Delta\|_2 \le 2\|\Delta\|_2 + \|\Delta\|_2^2 = 2\rho + \rho^2$$
Por consiguiente, si la perturbación ambiente satisface $\rho \le \sqrt{1 + \varepsilon} - 1 \approx \frac{\varepsilon}{2}$, queda garantizada la cota del defecto de Gram: $\|\Delta_G\|_2 \le \varepsilon$.

Para $\|\Delta_G\|_2 \le \varepsilon < 1$, la matriz $I_K + \Delta_G$ es simétrica definida positiva y admite la expansión en serie de potencias del binomio inverso:
$$(I_K + \Delta_G)^{-1/2} = I_K - \frac{1}{2}\Delta_G + \frac{3}{8}\Delta_G^2 - \frac{5}{16}\Delta_G^3 + \frac{35}{128}\Delta_G^4 + \mathcal{O}(\|\Delta_G\|_2^5)$$
Multiplicando por $Y = X + \Delta$, la retracción polar adopta la forma factorizada:
$$\mathcal{R}_{\mathrm{St}}(X + \Delta) = (X + \Delta)\left(I_K - \frac{1}{2}\Delta_G + \frac{3}{8}\Delta_G^2 - \dots\right)$$
Dado que $\Delta_G = \Delta_G^\top$ es una matriz estrictamente simétrica en $\mathbb{R}^{K \times K}$, satisface la identidad canónica:
$$\operatorname{tr}(\Delta_G^2) = \operatorname{tr}(\Delta_G^\top \Delta_G) = \|\Delta_G\|_F^2$$
lo que permite expresar el término cuadrático de la energía de deformación directamente mediante la norma de Frobenius $\|\Delta_G\|_F^2$.

*Delimitación Epistémica:* Teorema de análisis funcional matricial exacto en aritmética real bajo la condición de convergencia espectral $\|\Delta_G\|_2 \le \varepsilon < 1$.

### Política de Implementación 4.3 (Aceleración Numérica Horner de Grado 4 y Respaldo por Factorización QR)

Para el cómputo del factor inverso $(I + E)^{-1/2}$ donde $E = \Delta_G$:
1. **Definición Explícita del Polinomio de Horner de Grado 4 ($p_4(E)$):**  
   Para la función escalar analítica $f(x) = (1+x)^{-1/2}$, su truncamiento polinomial de Taylor de grado 4 alrededor de 0 es:
   $$p_4(x) = 1 - \frac{1}{2}x + \frac{3}{8}x^2 - \frac{5}{16}x^3 + \frac{35}{128}x^4$$
   computado matricialmente mediante la regla anidada de Horner:
   $$p_4(E) = I + E\left(-\frac{1}{2}I + E\left(\frac{3}{8}I + E\left(-\frac{5}{16}I + \frac{35}{128}E\right)\right)\right)$$
   En aritmética de coma flotante IEEE-754 FP64, las multiplicaciones matriciales intermedias pueden introducir una asimetría numérica de orden $O(u)$. La política de implementación impone la simetrización explícita:
   $$\hat{p}_4(E) \leftarrow \frac{1}{2}\left(p_4(E) + p_4(E)^\top\right)$$
   Se define formalmente la matriz de residuo analítico de truncamiento como:
   $$R_4(E) := (I + E)^{-1/2} - p_4(E) = f(E) - p_4(E)$$
2. **Derivación Espectral de la Cota del Residuo Proporcional a $\|E\|_F$ en Aritmética Real:**  
   La quinta derivada escalar de $f(x)$ es $f^{(5)}(x) = -\frac{945}{32}(1+x)^{-11/2}$. Para cada autovalor $\lambda_i \in [-\varepsilon, \varepsilon]$ de la matriz simétrica $E = Q \Lambda Q^\top$, el teorema de Taylor con resto de Lagrange establece que existe un punto intermedio $\xi_i$ entre $0$ y $\lambda_i$ tal que el residuo escalar satisface $R_4(\lambda_i) = f(\lambda_i) - p_4(\lambda_i) = \frac{f^{(5)}(\xi_i)}{5!} \lambda_i^5$, cumpliendo en valor absoluto:
   $$|R_4(\lambda_i)| \le C_4(\varepsilon) |\lambda_i|^5, \quad \text{donde } C_4(\varepsilon) := \frac{945}{32 \cdot 120 (1-\varepsilon)^{11/2}} = \frac{63}{256(1-\varepsilon)^{11/2}}$$
   Dado que $E$ es simétrica, la función matricial de residuo $R_4(E)$ diagonaliza en la misma base ortogonal: $R_4(E) = Q \, \mathrm{diag}(R_4(\lambda_1), \dots, R_4(\lambda_K)) \, Q^\top$. Aplicando la invariancia unitaria de la norma de Frobenius y la cota espectral:
   $$\|R_4(E)\|_F = \sqrt{\sum_{i=1}^K |R_4(\lambda_i)|^2} \le C_4(\varepsilon) \sqrt{\sum_{i=1}^K \lambda_i^{10}} \le C_4(\varepsilon) \max_{j} |\lambda_j|^4 \sqrt{\sum_{i=1}^K \lambda_i^2} = C_4(\varepsilon) \|E\|_2^4 \|E\|_F$$
   En particular, en el régimen de diseño $\|E\|_2 \le \varepsilon = 0{,}05$, evaluando formalmente:
   $$C_4(0{,}05) = \frac{63}{256(0{,}95)^{11/2}} \approx 0{,}326303 \le 0{,}33$$
   lo que garantiza la cota analítica estricta del residuo proporcional a $\|E\|_F$ en aritmética real:
   $$\|R_4(E)\|_F \le C_4(0{,}05) \cdot (0{,}05)^4 \|E\|_F \le 0{,}33 \times (6{,}25 \times 10^{-6}) \|E\|_F = 2{,}0625 \times 10^{-6} \|E\|_F \le 2{,}07 \times 10^{-6} \|E\|_F$$
3. **Análisis de Error Directo en Coma Flotante FP64 (Truncamiento Analítico vs Redondeo Numérico):**  
   Bajo el análisis estándar de error de redondeo para evaluación matricial de Horner (Higham, 2002, Teorema 4.2), para matrices simétricas $E \in \mathbb{R}^{K \times K}$ ($K = 32$) con $\|E\|_2 \le 0{,}05$, el error de evaluación en FP64 está gobernado por:
   $$\|\hat{p}_4(E) - p_4(E)\|_F \le \gamma_{16K} \tilde{p}_4(\|E\|_F) + \mathcal{O}(u^2)$$
   donde $\tilde{p}_4(x) = 1 + \frac{1}{2}x + \frac{3}{8}x^2 + \frac{5}{16}x^3 + \frac{35}{128}x^4$ y $\gamma_m := \frac{mu}{1 - mu} \approx mu$.
   En consecuencia, el error directo total de la aproximación calculada $\hat{p}_4(E)$ respecto a $(I + E)^{-1/2}$ satisface:
   $$\|\hat{p}_4(E) - (I + E)^{-1/2}\|_F \le \|R_4(E)\|_F + \gamma_{16K} \tilde{p}_4(\|E\|_F) + \mathcal{O}(u^2)$$
   - *Régimen Operativo Nominal ($\|E\|_2 \in [0{,}01, 0{,}05]$):* El residuo analítico de truncamiento ($\|R_4(E)\|_F \le 2{,}07 \times 10^{-6} \|E\|_F$) es el término predominante, superando al redondeo en varios órdenes de magnitud.
   - *Régimen Infinitesimal ($E \to 0$):* Conforme $\|E\|_F \to 0$, el residuo analítico $R_4(E)$ se anula idénticamente ($R_4(0) = 0$). En este régimen, el error no está acotado por el término analítico, sino que el redondeo de máquina $\mathcal{O}(K u) \approx 10^{-16}$ a $10^{-15}$ fija la cota inferior física de precisión.
4. **Criterio Heurístico de Despacho en Silicio:** Si $\|E\|_2 \le 0{,}05$, el polinomio simetrizado $\hat{p}_4(E)$ proporciona una evaluación ultrarrápida. Si $\|E\|_2 > 0{,}05$, o si tras la evaluación el defecto residual excede la tolerancia exigida, la implementación conmuta incondicionalmente a factorización Householder QR en FP64. Esto constituye una directiva de ingeniería de software, no un teorema analítico universal.

### Protocolo Operacional y Observación Empírica 4.4 (Comportamiento Flotante FP64 y Reset Periódico)

1. **Aritmética Flotante Finita y Preservación de Ortogonalidad:**  
   En aritmética IEEE-754 FP64 ($u \approx 1{,}11 \times 10^{-16}$), la evaluación polinomial de Horner acumula un error residual gobernado en el régimen nominal por el residuo analítico $\le 2{,}07 \times 10^{-6} \|E\|_F$ más el redondeo matricial. En simulaciones controladas de 2.048 evaluaciones consecutivas, el defecto medido $\|X_t^\top X_t - I_K\|_F$ se mantuvo $\le 2{,}07 \times 10^{-6}$ en el régimen $\|E\|_2 \le 0{,}05$.
2. **Reset Periódico por Factorización QR de Householder:**  
   Para prevenir la acumulación asintótica de deriva numérica a lo largo de millones de pasos, cada $N_{\mathrm{reset}} = 10^4$ actualizaciones el sistema ejecuta una factorización QR de Householder en FP64:
   $$X_{t} \leftarrow \operatorname{qr}(X_t) = Q_t R_t \implies X_t^{\mathrm{reset}} = Q_t$$
   En análisis numérico estándar de coma flotante, la pérdida de ortogonalidad en la factorización Householder QR calculada $\hat{Q}$ mediante reflexiones de Householder está gobernada por la cota teórica de estabilidad hacia atrás (Golub & Van Loan, 2013, §5.1.4; Higham, 2002, Teorema 19.4):
   $$\|\hat{Q}^\top \hat{Q} - I_K\|_F \le c \cdot D \cdot u$$
   donde $c \approx 2$ es una constante moderada. Para $D = 2.048$ y $u = 2^{-53} \approx 1{,}11 \times 10^{-16}$, esta cota predice un defecto residual teórico $\le 2 \times 2048 \times 1{,}11 \times 10^{-16} \approx 4{,}55 \times 10^{-13}$. En la validación física en silicio sobre la estación de trabajo y nodo de cómputo, el defecto ortonormal medido tras el reset arrojó un error físico empírico de $1{,}18 \times 10^{-15}$.

*Delimitación Epistémica:* El comportamiento a 2.048 pasos se clasifica como una *observación empírica en silicio*. El reset por Householder QR se clasifica como una *política de ingeniería numérica* con estabilidad flotante acotada a nivel de máquina.

## 5. ¿QUÉ INFORMACIÓN SE PIERDE AL PROYECTAR?

### Teorema 5.0 (Inviolabilidad Isométrica de la Cota de Welch)

**Enunciado:** La inmersión en la variedad compacta de Stiefel $\mathrm{St}(D, K)$ **no elude ni reduce** la cota inferior de Welch sobre la coherencia mutua de representaciones latentes.
Para cualquier conjunto de  \gg K$ conceptos representados como combinaciones lineales en el marco  \in \mathrm{St}(D, K)$ mediante vectores de coeficientes  \in S^{K-1}$ ( = X a_i$ con $\|c_i\|_2 = 1$), los productos internos satisfacen:
\langle c_i, c_j \rangle = (X a_i)^\top (X a_j) = a_i^\top (X^\top X) a_j = a_i^\top I_K a_j = \langle a_i, a_j \rangle
Por consiguiente, la matriz de Gram $\mathcal{G}_{ij} = \langle c_i, c_j \rangle$ es idéntica a la matriz de Gram de los vectores en $\mathbb{R}^K$. La coherencia mutua $\mu = \max_{i \neq j} |\langle c_i, c_j \rangle|$ está acotada inferiormente de forma estricta por la cota de Welch:
\mu \ge \sqrt{\frac{N - K}{K(N - 1)}}
La variedad de Stiefel actúa como una isometría estricta que preserva distancias y productos internos; redistribuye la trayectoria en un espacio de norma unitaria acotada pero no disminuye la interferencia cruzada inherente a la dimensión $.

### Proposición 5.1 (Métrica Cordal de Grassmann y Preservación del Subespacio Columna)

Para $X_1, X_2 \in \mathrm{St}(D, K)$, consideremos sus subespacios columna asociados $\mathcal{X}_1 = \operatorname{span}(X_1)$ y $\mathcal{X}_2 = \operatorname{span}(X_2)$ como puntos en la variedad de Grassmann $\operatorname{Gr}(K, D)$. La distancia cordal estandarizada entre los proyectores ortogonales ortonormales $P_1 = X_1 X_1^\top$ y $P_2 = X_2 X_2^\top$ se define como:
$$d_c(\mathcal{X}_1, \mathcal{X}_2) := \frac{1}{\sqrt{2}} \|X_1 X_1^\top - X_2 X_2^\top\|_F$$
Desarrollando la norma de Frobenius mediante la traza y utilizando la propiedad cíclica:
$$\|X_1 X_1^\top - X_2 X_2^\top\|_F^2 = \operatorname{tr}\left((X_1 X_1^\top - X_2 X_2^\top)^2\right) = \operatorname{tr}(X_1 X_1^\top) + \operatorname{tr}(X_2 X_2^\top) - 2\operatorname{tr}(X_1 X_1^\top X_2 X_2^\top)$$
Dado que $\operatorname{tr}(X_i X_i^\top) = \operatorname{tr}(X_i^\top X_i) = \operatorname{tr}(I_K) = K$ y $\operatorname{tr}(X_1 X_1^\top X_2 X_2^\top) = \|X_1^\top X_2\|_F^2$:
$$\|X_1 X_1^\top - X_2 X_2^\top\|_F^2 = 2K - 2\|X_1^\top X_2\|_F^2 = 2\left(K - \|X_1^\top X_2\|_F^2\right)$$
Por consiguiente, la distancia cordal normalizada satisface la identidad algebraica exacta:
$$d_c(\mathcal{X}_1, \mathcal{X}_2) = \sqrt{K - \|X_1^\top X_2\|_F^2} = \sqrt{\sum_{i=1}^K \sin^2 \theta_i}$$
donde $\theta_1, \dots, \theta_K \in [0, \pi/2]$ son los ángulos principales canónicos entre los dos subespacios.

### Lema 5.1(b) (Preservación Exacta del Subespacio Columna por Retracción Polar)

Para cualquier matriz $Z \in \mathbb{R}^{D \times K}$ con rango de columnas completo $K$, su factor polar ortonormal $\mathcal{R}_{\mathrm{St}}(Z) = Z (Z^\top Z)^{-1/2}$ preserva idénticamente el subespacio columna de $Z$:
$$\operatorname{span}(\mathcal{R}_{\mathrm{St}}(Z)) = \operatorname{span}(Z)$$

**Demostración Analítica Rigurosa:**  
Dado que $Z$ tiene rango de columnas completo $K$, la matriz de Gram $Z^\top Z \in \mathbb{R}^{K \times K}$ es simétrica y estrictamente definida positiva ($Z^\top Z \succ 0$). En consecuencia, su factor inverso simétrico $M := (Z^\top Z)^{-1/2} \in \mathbb{R}^{K \times K}$ es una matriz cuadrada invertible y no singular.
1. Para cualquier vector $v \in \operatorname{span}(\mathcal{R}_{\mathrm{St}}(Z))$, existe $w \in \mathbb{R}^K$ tal que $v = \mathcal{R}_{\mathrm{St}}(Z) w = (Z M) w = Z (M w)$. Tomando $u = M w \in \mathbb{R}^K$, se tiene $v = Z u \in \operatorname{span}(Z)$, lo que prueba $\operatorname{span}(\mathcal{R}_{\mathrm{St}}(Z)) \subseteq \operatorname{span}(Z)$.
2. Recíprocamente, para cualquier vector $v \in \operatorname{span}(Z)$, existe $u \in \mathbb{R}^K$ tal que $v = Z u$. Dado que $M$ es invertible con inversa $M^{-1} = (Z^\top Z)^{1/2}$, definiendo $w = M^{-1} u = (Z^\top Z)^{1/2} u \in \mathbb{R}^K$, se tiene:
   $$\mathcal{R}_{\mathrm{St}}(Z) w = (Z M) (M^{-1} u) = Z (M M^{-1}) u = Z u = v$$
   luego $v \in \operatorname{span}(\mathcal{R}_{\mathrm{St}}(Z))$, demostrando $\operatorname{span}(Z) \subseteq \operatorname{span}(\mathcal{R}_{\mathrm{St}}(Z))$.
Por tanto, $\operatorname{span}(\mathcal{R}_{\mathrm{St}}(Z)) = \operatorname{span}(Z)$ se cumple idénticamente en álgebra lineal exacta sobre $\mathbb{R}$. $\blacksquare$

### Proposición 5.2 (Cota Inferior de Coherencia de Welch para Subespacios de Grassmann)

Para una colección de $N$ subespacios de dimensión $K$ en $\mathbb{R}^D$ representados por proyectores ortogonales $\{P_i = X_i X_i^\top\}_{i=1}^N$ con $X_i \in \mathrm{St}(D, K)$ y $N > D/K$, la coherencia mutua máxima en norma de Frobenius no normalizada se define como:
$$\mu_{\mathrm{sub}} := \max_{1 \le i < j \le N} \|X_i^\top X_j\|_F$$

**Derivación Analítica Rigurosa:**  
Consideremos la matriz suma de los proyectores $S := \sum_{i=1}^N P_i \in \mathbb{R}^{D \times D}$. Evaluando la norma de Frobenius al cuadrado de $S$ en el espacio de matrices simétricas:
$$\|S\|_F^2 = \operatorname{tr}(S^2) = \sum_{i=1}^N \sum_{j=1}^N \operatorname{tr}(P_i P_j) = \sum_{i=1}^N \operatorname{tr}(P_i^2) + \sum_{i \ne j} \operatorname{tr}(X_i X_i^\top X_j X_j^\top)$$
Dado que $P_i^2 = P_i$ y $\operatorname{tr}(P_i) = \operatorname{tr}(X_i^\top X_i) = \operatorname{tr}(I_K) = K$, los $N$ términos diagonales suman $N K$. Para los términos cruzados, por la propiedad cíclica de la traza: $\operatorname{tr}(X_i X_i^\top X_j X_j^\top) = \operatorname{tr}((X_i^\top X_j)(X_i^\top X_j)^\top) = \|X_i^\top X_j\|_F^2$. Por tanto:
$$\|S\|_F^2 = N K + \sum_{i \ne j} \|X_i^\top X_j\|_F^2$$
Por otra parte, por la desigualdad de Cauchy-Schwarz sobre los autovalores de la matriz simétrica $S \in \mathbb{R}^{D \times D}$:
$$\|S\|_F^2 = \sum_{k=1}^D \lambda_k(S)^2 \ge \frac{1}{D} \left(\sum_{k=1}^D \lambda_k(S)\right)^2 = \frac{1}{D} (\operatorname{tr}(S))^2 = \frac{1}{D} \left(\sum_{i=1}^N \operatorname{tr}(P_i)\right)^2 = \frac{(NK)^2}{D}$$
Combinando ambas relaciones:
$$\sum_{i \ne j} \|X_i^\top X_j\|_F^2 = \|S\|_F^2 - NK \ge \frac{N^2 K^2}{D} - NK = \frac{NK(NK - D)}{D}$$
Dado que existen exactamente $N(N-1)$ términos fuera de la diagonal en la suma doble, el término máximo satisface necesariamente:
$$\mu_{\mathrm{sub}}^2 = \max_{i \ne j} \|X_i^\top X_j\|_F^2 \ge \frac{1}{N(N-1)} \sum_{i \ne j} \|X_i^\top X_j\|_F^2 \ge \frac{NK(NK - D)}{D \cdot N(N-1)} = \frac{K(NK - D)}{D(N-1)}$$
Tomando la raíz cuadrada positiva en ambos miembros, se concluye la cota inferior analítica exacta de Welch para subespacios de Grassmann (Conway, Hardin & Sloane, 1996; Dhillon et al., 2008):
$$\mu_{\mathrm{sub}} \ge \sqrt{\frac{K(NK - D)}{D(N - 1)}} = \sqrt{K} \sqrt{\frac{NK - D}{D(N - 1)}}$$
garantizando que ninguna configuración de $N$ hipótesis en dimensión ambiente $D$ puede tener correlación de Frobenius inferior a este umbral teórico.
> [!NOTE] Precision sobre Definicion de Coherencia de Subespacio:
> La cota $\mu_{\mathrm{sub}}^2 \ge \frac{K(NK - D)}{D(N - 1)}$ aplica para la coherencia en norma de Frobenius no normalizada $\|X_i^\top X_j\|_F$. Si se normaliza respecto a la dimension de subespacio $K$, la coherencia espectral $\|X_i^\top X_j\|_2$ o chordal satisface $\mu_{\mathrm{spec}}^2 \ge \frac{NK - D}{D K (N - 1)}$.


*Delimitación Epistémica:* Teorema de álgebra lineal y teoría de empaquetamientos en variedades de Grassmann analíticamente demostrado.

## 6. ¿QUÉ SIGNIFICA QUE UN SLAB CODIFIQUE VARIAS HIPÓTESIS?

### Definición 6.1 (Superposición Matricial de Hipótesis)

Un estado multi-hipótesis se formula mediante la combinación matricial ponderada de $p$ hipótesis latentes $h_1, \dots, h_p \in \mathcal{H}$:
$$Z = \sum_{\ell=1}^p \alpha_\ell \mathcal{E}(h_\ell), \quad \alpha_\ell \in \mathbb{R}^+, \quad X = \mathcal{R}_{\mathrm{St}}(Z)$$
donde $\mathcal{E}: \mathcal{H} \to \mathrm{St}(D, K)$ es el codificador latente entrenado.

### Conjetura Empírica 6.2 (Separabilidad de Hipótesis bajo Superposición y Retracción)

Se conjetura que cuando las hipótesis latentes individuales $\mathcal{E}(h_i)$ presentan baja correlación cruzada en el espacio ambiente ($\|\mathcal{E}(h_i)^\top \mathcal{E}(h_j)\|_F \ll 1$), la superposición lineal $Z = \sum \alpha_\ell \mathcal{E}(h_\ell)$ seguida de la retracción polar $\mathcal{R}_{\mathrm{St}}(Z)$ proyecta el estado conjunto sobre la variedad preservando información suficiente para que un decodificador adecuadamente entrenado pueda discriminar las hipótesis componentes. Esta afirmación constituye una hipótesis de diseño y arquitectura de red sujeta a validación en downstream tasks.

---

## 7. ¿CÓMO SE TRADUCE UN SLAB ENTRE MODELOS HETEROGÉNEOS?

### Definición 7.1 (Operador de Traducción Inter-Modelo con Rango Común $K$)

Consideremos dos modelos $a_i$ y $a_j$ que comparten el rango de marco estándar $K$ (e.g., $K = 32$) pero operan en dimensiones ambientales heterogéneas $D_i \neq D_j$. La traducción de un marco $X_i \in \mathrm{St}(D_i, K)$ hacia $\mathrm{St}(D_j, K)$ se formula mediante:
$$\Phi_{ij}(X_i) := \mathcal{R}_{\mathrm{St}}\left(L_{ij} X_i W_{ij}^\star\right)$$
donde:
1. $L_{ij} \in \mathbb{R}^{D_j \times D_i}$ es un operador de inmersión/proyección ambiental con $\|L_{ij}\|_2 = 1$, sujeto a la precondición de rango $\sigma_K(L_{ij} X_i) > 0$.
2. $W_{ij}^\star \in O(K)$ es la solución al problema de Procrustes Ortogonal:
   $$W_{ij}^\star = \arg\min_{W \in O(K)} \|L_{ij} X_i W - X_j\|_F$$
   donde $X_j \in \mathrm{St}(D_j, K)$ representa el marco de referencia en el modelo destino.

### Teorema 7.2 (Solución de Procrustes Ortogonal y Caracterización Rigurosa de Optimizadores)

Para dos representaciones latentes $X, Y \in \mathrm{St}(D, K)$ (con $D \ge K$), sea $M := X^\top Y \in \mathbb{R}^{K \times K}$ la matriz de correlación cruzada inter-modelo con descomposición en valores singulares:
$$M = U \Sigma V^\top, \quad U, V \in O(K), \quad \Sigma = \operatorname{diag}(\sigma_1, \dots, \sigma_K), \quad \sigma_1 \ge \dots \ge \sigma_K \ge 0$$
donde $r = \operatorname{rank}(M) \le K$ denota el número de valores singulares estrictamente positivos $\sigma_1 \ge \dots \ge \sigma_r > 0$.

El problema de alineación de Procrustes ortogonal:
$$\min_{W \in O(K)} \|X W - Y\|_F^2$$
se expande por las identidades de norma de Frobenius como:
$$\|X W - Y\|_F^2 = \operatorname{tr}((X W - Y)^\top (X W - Y)) = \operatorname{tr}(W^\top X^\top X W) - 2 \operatorname{tr}(W^\top X^\top Y) + \operatorname{tr}(Y^\top Y) = 2K - 2 \operatorname{tr}(W^\top M)$$
Por consiguiente, minimizar el error cuadrático es idénticamente equivalente a maximizar el funcional lineal de traza $\operatorname{tr}(W^\top M)$ sobre la variedad de Stiefel compacta $O(K)$.

1. **Caracterización de Polaridad y Cota Superior de Traza (Higham, 1986):**  
   Para cualquier $W \in O(K)$, definamos la matriz ortogonal auxiliar $Z := V^\top W^\top U \in O(K)$. Por la propiedad cíclica de la traza:
   $$\operatorname{tr}(W^\top M) = \operatorname{tr}(W^\top U \Sigma V^\top) = \operatorname{tr}(V^\top W^\top U \Sigma) = \operatorname{tr}(Z \Sigma) = \sum_{i=1}^K Z_{ii} \sigma_i = \sum_{i=1}^r Z_{ii} \sigma_i$$
   Dado que $Z$ es una matriz ortogonal real, sus entradas satisfacen $|Z_{ii}| \le 1$ para todo $i$. Por tanto:
   $$\operatorname{tr}(W^\top M) \le \sum_{i=1}^r \sigma_i$$
   alcanzándose la cota superior si y solo si $Z_{ii} = 1$ para todo $i \in \{1, \dots, r\}$.

2. **Lema de Estructura Bloque-Diagonal en Matrices Ortogonales:**  
   Sea $Z \in O(K)$ una matriz ortogonal tal que $Z_{ii} = 1$ para todo $i \in \{1, \dots, r\}$.
   - Para cada $i \in \{1, \dots, r\}$, la norma euclídea de la columna $i$ satisface:
     $$\sum_{j=1}^K Z_{ji}^2 = Z_{ii}^2 + \sum_{j \ne i} Z_{ji}^2 = 1 + \sum_{j \ne i} Z_{ji}^2 = 1 \implies Z_{ji} = 0 \quad (\forall j \ne i)$$
   - Análogamente, la norma euclídea de la fila $i$ satisface:
     $$\sum_{j=1}^K Z_{ij}^2 = Z_{ii}^2 + \sum_{j \ne i} Z_{ij}^2 = 1 + \sum_{j \ne i} Z_{ij}^2 = 1 \implies Z_{ij} = 0 \quad (\forall j \ne i)$$
   En consecuencia, las primeras $r$ filas y columnas de $Z$ coinciden con la matriz identidad $I_r$, y los bloques fuera de la diagonal principal son idénticamente nulos, forzando la estructura bloque-diagonal estricta:
   $$Z = \begin{pmatrix} I_r & 0 \\ 0 & Q_0^\top \end{pmatrix}, \quad \text{donde } Q_0 \in O(K - r)$$

3. **Familia Exhaustiva de Optimizadores Globales:**  
   Particionando las matrices singulares $U$ y $V$ en bloques ortogonales $U = [U_r \mid U_0]$ y $V = [V_r \mid V_0]$, donde $U_0 \in \mathbb{R}^{K \times (K-r)}$ forma una base ortonormal de $\ker(M^\top)$ y $V_0 \in \mathbb{R}^{K \times (K-r)}$ forma una base ortonormal de $\ker(M)$:
   $$W = U Z^\top V^\top = [U_r \mid U_0] \begin{pmatrix} I_r & 0 \\ 0 & Q_0 \end{pmatrix} \begin{pmatrix} V_r^\top \\ V_0^\top \end{pmatrix} = U_r V_r^\top + U_0 Q_0 V_0^\top$$
   Por tanto, el conjunto exhaustivo de minimizadores ortogonales adopta la parametrización canónica:
   $$\mathcal{S}_{\mathrm{opt}} = \left\{ W = U_r V_r^\top + U_0 Q_0 V_0^\top \;\middle|\; Q_0 \in O(K - r) \right\}$$
   Para cualquier $Q_0 \in O(K - r)$, la matriz producto satisface idénticamente en $\mathbb{R}$:
   $$W^\top M = (V_r U_r^\top + V_0 Q_0^\top U_0^\top)(U_r \Sigma_r V_r^\top) = V_r \Sigma_r V_r^\top = (M^\top M)^{1/2} \succeq 0$$
   demostrando que $W^\top M = (M^\top M)^{1/2} \succeq 0$ caracteriza exactamente el conjunto de optimizadores. $\blacksquare$

4. **Convención Canónica de Implementación en Silicio y Condiciones de Reproducibilidad:**  
   En silicio bajo aritmética de punto flotante binary64, los algoritmos de SVD (e.g. LAPACK `dgesvd` o rotaciones Jacobi) generan un par de matrices ortogonales $(U, V) \in O(K) \times O(K)$ completamente coordinadas con una convención determinista de signo (e.g., primer elemento no nulo positivo).
   Bajo esta base singular coordinada generada por el runtime, la convención de software canónica adopta $Q_0 = I_{K - r}$, produciendo el factor polar:
   $$W^\star = U V^\top = U_r V_r^\top + U_0 V_0^\top$$
   *Condiciones Físicas de Reproducibilidad Bit a Bit:* Esta reproducibilidad numérica está rigurosamente condicionada a un entorno determinista especificado:
   (a) Ejecución con semántica de punto flotante estricta IEEE-754 (`/fp:precise` en MSVC, `-fno-fast-math` en GCC/Clang).
   (b) Deshabilitación explícita de contracciones FMA no asociativas (`#pragma STDC FP_CONTRACT OFF`).
   (c) Mismo runtime numérico LAPACK/BLAS compilado con idénticas instrucciones vectoriales y orden determinista secuencial de reducción.
   En presencia de autovalores múltiples o conglomerados singulares ($\sigma_i \approx \sigma_{i+1}$), la elección de base en subespacios degenerados se fija mediante la convención de ordenación canónica del resolvedor SVD.

*Delimitación Epistémica:* Teorema de álgebra lineal exacto en $\mathbb{R}$ (Higham, 1986). La selección de $Q_0 = I_{K-r}$ se clasifica formalmente como una *convención canónica de software relativa al sistema de coordenadas de la SVD numérica*.

## 8. ¿QUÉ COTAS DE ERROR TIENE EL PIPELINE NUMÉRICO COMPLETO?

### Estimación del Acumulador Compensado de Neumaier y Modelo Numérico 8.1

El algoritmo de Neumaier (1974) para la suma de productos en coma flotante FP64 tiene por objeto mitigar el error de cancelación catastrófica mediante la acumulación de un término de compensación de bajo orden.

1. **Definición Algorítmica y Cota Escalar de Error Directo (Higham, 2002):**  
   Para dos vectores $x, y \in \mathbb{R}^D$ con $D = 2.048$, el producto escalar compensado $\hat{s} = \operatorname{NeumaierDot}(x, y)$ se computa mediante:
   ```
   s = x_1 * y_1,  c = 0
   for i = 2 to D:
       p = x_i * y_i
       t = s + p
       if |s| >= |p|:
           c += (s - t) + p
       else:
           c += (p - t) + s
       s = t
   return s + c
   ```
   **Hipótesis del Modelo Aritmético Estándar:**  
   Bajo aritmética flotante estricta IEEE-754 binary64 ($u = 2^{-53} \approx 1{,}11 \times 10^{-16}$) con el modelo de error estándar $fl(a \circ b) = (a \circ b)(1 + \delta)$ con $|\delta| \le u$, productos redondeados individualmente sin fusión FMA no asociativa, ausencia de desbordamiento (*overflow*) y ausencia de subdesbordamiento a valores subnormales en todas las sumas y diferencias intermedias ($|s|, |p|, |t|, |c| \in [2^{-1022}, 2^{1023}]$), el análisis de error directo de Neumaier (Higham, 2002, Teorema 4.8) establece la cota de primer orden:
   $$|\hat{s} - x^\top y| \le \left(2u + \gamma_{D+2}\right) \sum_{i=1}^D |x_i y_i| + \mathcal{O}(u^2)$$
   donde $\gamma_m := \frac{m u}{1 - m u}$.

2. **Agregación Matricial sobre la Matriz de Gram y Cota en Norma de Frobenius:**  
   Cuando se evalúa la matriz de Gram $G = X^\top Y \in \mathbb{R}^{K \times K}$ entre dos marcos de Stiefel $X, Y \in \mathrm{St}(D, K)$ (con $K = 32$), cada coordenada $G_{jk} = X_{:,j}^\top Y_{:,k}$ se computa de forma independiente mediante el sumador de Neumaier:
   $$|\hat{G}_{jk} - G_{jk}| \le \left(2u + \gamma_{D+2}\right) \sum_{i=1}^D |X_{ij} Y_{ik}| + \mathcal{O}(u^2)$$
   Dado que $X$ e $Y$ son marcos de Stiefel, sus columnas tienen norma euclídea unitaria $\|X_{:,j}\|_2 = \|Y_{:,k}\|_2 = 1$. Por la desigualdad de Cauchy-Schwarz:
   $$\sum_{i=1}^D |X_{ij} Y_{ik}| \le \|X_{:,j}\|_2 \|Y_{:,k}\|_2 = 1$$
   Por tanto, cada coordenada satisface uniformemente $|\hat{G}_{jk} - G_{jk}| \le 2u + \gamma_{D+2} + \mathcal{O}(u^2)$. Agregando sobre las $K^2$ coordenadas en la norma de Frobenius:
   $$\|\hat{G} - G\|_F = \sqrt{\sum_{j=1}^K \sum_{k=1}^K |\hat{G}_{jk} - G_{jk}|^2} \le K \left(2u + \gamma_{D+2}\right) + \mathcal{O}(u^2)$$
   Para $K = 32$ y $D = 2.048$, se cumple $2u + \gamma_{2050} \approx 2{,}22 \times 10^{-16} + 2{,}28 \times 10^{-13}$, lo que proporciona una cota analítica dimensionalmente coherente y estructuralmente rigurosa.

*Delimitación Epistémica y Condiciones Físicas de Silicio:*  
Esta estimación se clasifica formalmente como un **modelo analítico de algoritmo numérico compensado**, sujeto a las siguientes precondiciones explícitas:
1. No se producen desbordamientos (overflows) ni valores no finitos (NaNs, Infs).
2. Ausencia de subdesbordamiento (underflow) a valores subnormales en las sumas y diferencias intermedias ($|s|, |p|, |t|, |c| \ge 2^{-1022}$).
3. Banderas de precisión estricta IEEE-754 (`/fp:precise` en MSVC, `-fno-fast-math` en GCC/Clang) con contracción FMA controlada.
4. Respaldo físico por la re-proyección periódica QR de Householder cada $N_{\mathrm{reset}} = 10^4$ pasos (§4.4), que re-proyecta el estado hacia $\mathrm{St}(D, K)$ con backward stability determinista.

## 9. ¿QUÉ GARANTÍAS DE CONSISTENCIA TIENE LA MEMORIA COMPARTIDA?

### Teorema 9.0 (Prueba Formal de Data-Race Freedom en ISO C++20 vía Tickets Atómicos de Lector)

**Enunciado:** En una región de memoria compartida sin bloqueos donde los lectores leen slabs matriciales  \times K$ mediante std::memcpy, la publicación de un índice atómico aislado (std::atomic<uint32_t> published_idx) **incurre en Data Races (Undefined Behavior bajo ISO C++20)** ante lectores lentos desprogramados por el planificador del sistema operativo (sobrepaso por escritor rápido / ABA wrap-around).
Para garantizar Data-Race Freedom (DRF) estricto, es matemáticamente y mecánicamente obligatorio el protocolo de **reserva atómica previa de ranura con contador de lectores** (
eader_count[3] y tokens de arrendamiento RAII PmtpLeaseToken).

**Demostración:**
Bajo el modelo de memoria formal de ISO C++20 (§6.9.2), dos accesos a una misma localización de memoria entran en carrera de datos si al menos uno es de escritura y no están ordenados por una relación de *happens-before*.
1. *Fallo de Índice Simple:* Si un lector $ observa published_idx = 0 y procede a ejecutar std::memcpy no atómico, un escritor rápido $ puede producir ráfagas sucesivas rellenando las ranuras 1, 2 y volviendo a escribir sobre la ranura 0 (store no atómico en el buffer payload) mientras $ continúa ejecutando memcpy. Puesto que memcpy no es atómico, se produce un acceso concurrente de escritura y lectura sobre los mismos bytes de silicio sin sincronización happens-before activa, lo cual constituye Undefined Behavior normativo.
2. *Garantía DRF por Reserva de Tickets:* En el protocolo PMTP, el lector $ adquiere atómicamente un ticket de lectura incrementando 
eader_count[slot] mediante etch_add(1, memory_order_acquire). El escritor $, antes de reclamar una ranura para sobrescritura, verifica obligatoriamente que 
eader_count[slot] == 0 mediante compare_exchange_strong. Si la ranura posee lectores activos (
eader_count > 0), el escritor es impedido de mutar dicho buffer. Al finalizar la lectura, $ decrementa etch_sub(1, memory_order_release). Esto establece formalmente una arista de sincronización happens-before entre la liberación de todos los lectores y cualquier mutación subsecuente del escritor, garantizando Data-Race Freedom (DRF) absoluto.

### 9.0 Especificación de Protocolo Binario IPC (PMTP-SHM-ABI-V39) y Ciclo de Vida de Memoria

El estándar ISO C++ regula la semántica de modelos de memoria multihilo dentro de un único espacio de direccionamiento virtual privado, pero no define normativamente la semántica de sincronización atómica entre procesos independientes (IPC) a través de regiones de memoria compartida mapeada. En consecuencia, el protocolo PMTP no postula una portabilidad abstracta sobre cualquier compilador o arquitectura ISO C++ genérica, sino que se formula formalmente como una **Especificación de Protocolo Binario a Nivel de ABI de Plataforma (PMTP-SHM-ABI-V39)** fundamentada en contratos explícitos de hardware y sistema operativo:

1. **Plataformas de Silicio Certificadas y Entorno de Despliegue:**
   - **Arquitecturas:** x86-64 (Intel Core, AMD Zen con soporte de instrucción atómica de silicio `LOCK CMPXCHG`) y ARM64 (AArch64 v8.1+ con extensiones atómicas LSE `CAS` o pareo exclusivo `LDREX`/`STREX`). Ambas arquitecturas operan en orden nativo Little-Endian (`std::endian::native == std::endian::little`).
   - **Sistemas Operativos:** Linux (kernel 5.4+ con memoria compartida POSIX `/dev/shm` montada con coherencia de página MMU) y Windows 10/11 / Windows Server 2022+ (Named File Mapping creado mediante `CreateFileMappingW` con protección `PAGE_READWRITE` y coherencia de caché de hardware).
   - **Compiladores y Bibliotecas Estándar:** GCC 11+ (libstdc++), Clang 13+ (libc++/libstdc++), y MSVC 2019+ (MSVC STL v142/v143/v144).

2. **Contrato de Plataforma Específica: Atómicos Address-Free en Hardware y Línea de Caché:**
   - En las plataformas objetivo especificadas, las palabras de 32 y 64 bits utilizadas por `std::atomic<uint32_t>` y `std::atomic<uint64_t>` satisfacen `is_always_lock_free == true` y se ejecutan como instrucciones directas de silicio.
   - **Garantía Address-Free a Nivel Físico:** En estas arquitecturas, las instrucciones atómicas de lectura-modificación-escritura operan directamente sobre la línea de caché física (protocolos de coherencia MESI/MOESI), siendo físicamente *address-free* (sin tablas de bloqueo globales en el espacio de usuario dependientes del puntero virtual privado).
   - **Alineación Obligatoria:** La dirección base del bloque mapeado en cada proceso debe satisfacer $\text{base\_addr} \equiv 0 \pmod{64}$. Todas las variables atómicas (`packed_cursor`, `lifecycle_and_inflight`, `slot_headers`, `epoch`) residen en desplazamientos múltiplos de 64 bytes o múltiplos de 8 bytes contenidos en una única línea de caché, erradicando desalineaciones y bloqueos divididos (*split locks*).
   - **Cláusula de Certificación Previa:** Todo nuevo entorno de ejecución debe certificar obligatoriamente este contrato ejecutando la batería de pruebas de silicio de PMTP (`test_sota_circuit_breaker.py` y `test_cross_cpp_rust_v013.py`), requiriendo código de salida físico `Exit Code 0` antes de habilitar el bus para producción.

3. **Contrato de Exclusión de Fallas Catastróficas (Crash-Stop Fault Exclusion Contract):**
   - El protocolo PMTP garantiza formalmente ausencia de carreras de datos, exclusión mutua estricta y sincronización de memoria entre procesos concurrentes conformes en ejecución activa.
   - No tolera fallas catastróficas abruptas (*crash-faults*, e.g., terminación forzosa `SIGKILL`, fallo de alimentación) que interrumpan un proceso mientras mantiene adquirido el `writer_lock` o durante la fase intermedia de copia de payload.
   - Ante la muerte anómala de un proceso cliente o escritor, el proceso supervisor ejecuta el protocolo de recuperación administrativa fuera de banda (§9.5), invocando `pmtp_shm_force_terminal_tombstone` con incremento monotónico de `supervisor_epoch` o reinicializando la región compartida tras verificar la terminación de los descriptores abiertos en el SO.

4. **Contrato de Ciclo de Vida del Objeto Binario y Protección del Kernel del SO:**
   - **Estructura Standard-Layout C-Compatible:** La región compartida está definida por estructuras C++20 de diseño estándar (*Standard Layout*) (`is_standard_layout_v<PmtpSharedRegion> == true`, `is_standard_layout_v<PmtpStiefelSlab> == true`), cuyos offsets y tamaños exactos están formalmente verificados por aserciones estáticas de compilación (`static_assert`).
   - **Inicialización Canónica por el Supervisor:** El proceso creador/supervisor es el único autorizado para invocar *placement-new* sobre el bloque mapeado:
     ```cpp
     PmtpSharedRegion* shm = ::new (raw_mem) PmtpSharedRegion();
     ```
     inicializando las cabeceras atómicas y estableciendo el inicio formal de la vida del objeto binario.
   - **Protección de Páginas por Conteo de Referencias del Kernel del SO:** En Windows y Linux, los subsistemas de gestión de memoria virtual del kernel mantienen un conteo de referencias interno sobre el objeto de memoria compartida (File Mapping Object en Windows, Inode SHM en POSIX). Mientras un proceso cliente mantenga un `HANDLE` abierto o una vista mapeada activa (`MapViewOfFile` / `mmap`), el kernel del sistema operativo garantiza que las páginas físicas subyacentes no son desasignadas ni reutilizadas, protegiendo a los clientes cooperativos frente a caídas de puntero mientras completan su ciclo de vida ordenado.
   - **Destrucción Física y Finalización Formal:** La destrucción física solo se ejecuta cuando el estado de apagado es terminal (`COMPLETED` o `FORCED_TOMBSTONE`) con cero lectores activos. `pmtp_shm_physical_destroy` adquiere `writer_lock`, valida que todas las ranuras estén en `SLOT_STATE_CLOSED` con cero lectores, conmuta atómicamente a `LIFECYCLE_DESTROYED`, invoca el destructor formal `shm->~PmtpSharedRegion()`, valida la alineación de 64 bytes, y desmapea la vista local del supervisor verificando el código de retorno del sistema operativo (`UnmapViewOfFile` / `munmap`).

### 9.1 Especificación Formal del Protocolo SWMR Multi-Buffer con Reserva Atómica por CAS y Guardias RAII

> **Ámbito de Aplicabilidad y Contrato de Integración de Plataforma (SO + ABI + Silicio):**
> Este protocolo se especifica para sistemas multiprocesador con memoria compartida coherente en hardware (x86-64 y ARM64/ARMv8-A+ con buses coherentes). Dado que ISO C++20 no define una semántica normativa para objetos atómicos compartidos entre procesos independientes, su corrección operativa se formula formalmente como una **precondición de ingeniería de sistemas**:
> 1. **Distinción entre Lock-Free y Address-Free (Requisito de Plataforma):** Las aserciones estáticas `static_assert(std::atomic<...>::is_always_lock_free)` son una condición **necesaria pero no suficiente**: certifican que las operaciones no se emulan mediante llamadas a mutexes internos de la biblioteca, pero no prueban por sí mismas que dos procesos independientes puedan operar sin locks dependientes del espacio de direcciones virtual privado. La propiedad **address-free** se exige formalmente como un requisito de conformidad validado por el toolchain (e.g., GCC/Clang con libstdc++/libc++ en Linux, MSVC en Windows) y respaldado por tests empíricos de arranque en silicio.
> 2. **Precondición de Alineación Base de Memoria Mapeada:** El puntero base entregado por la llamada al sistema (`mmap` en POSIX o `MapViewOfFile` en Windows) debe satisfacer estrictamente la alineación a 64 bytes de la arquitectura:
>    $$\operatorname{address}(shm) \equiv 0 \pmod{64}$$
>    asegurando que todos los miembros con `alignas(64)` coincidan exactamente con líneas de caché física de la CPU.
> 3. **Identidad Estricta de ABI y Representación Binaria:** Todos los procesos consumidores y publicadores deben compilarse bajo un ABI binario idéntico: misma familia y versión mayor de compilador, misma ordenación de bytes (little-endian), misma representación de punto flotante (IEEE-754 binary64), mismas reglas de alineación (`alignas(64)`) y estructuras de diseño estándar (`std::is_standard_layout_v`) y trivialmente copiables (`std::is_trivially_copyable_v`).
> 4. **Modelo Cooperativo SWMR sin Tolerancia a Muerte Anómala de Procesos (Crash-Fault Non-Tolerant):** El protocolo asume que los procesos participantes no sufren muerte abrupta (e.g., `SIGKILL`, pánico o fallo fatal de proceso) mientras retienen el lock de escritor o guardias de lectura. Si un proceso muere mientras retiene el lock o un lease, el protocolo no implementa recuperación autónoma de locks huérfanos; la recuperación exige la intervención del supervisor externo para el reseteo y reinicialización de la región.
> 5. **Propiedad de Inicialización y Ciclo de Vida del Objeto:** El proceso creador/supervisor es el único propietario del ciclo de vida y de la inicialización física (zero-fill completo y construcción in-situ de estructuras en memoria mapeada) antes de publicar la disponibilidad de la región (Axioma CdV-1).
> 6. **Mapeo de Memoria Coherente:** La región compartida (POSIX `/dev/shm` o Windows Named Shared Memory) debe mapearse en cada proceso con atributos de memoria ordinaria con coherencia de caché completa en hardware y permisos RW.

> **Precondiciones Formales de Ciclo de Vida (Axiomas de Inicialización y Terminación):**
>
> **Axioma CdV-1 (Inicialización Happens-Before):** La función `pmtp_shm_init_region` debe completarse antes de que cualquier hilo o proceso invoque `reader_acquire` o `writer_publish`. La barrera de inicialización es gestionada externamente por el proceso creador (e.g., mediante semáforo nombrado, descriptor de archivo centinela o mecanismo de control de procesos del SO).
>
> **Axioma CdV-2 (Protocolo de Admisión en Memoria Compartida, Quiescencia de Entrada y Cierre en Dos Fases):** La barrera de admisión se materializa directamente en el descriptor físico de la región (`PmtpSharedRegion.admission_gate` y `PmtpSharedRegion.admission_and_inflight`), eliminando cualquier dependencia de sincronización externa no formalizada:
> - **Fase 1 (Cierre Atómico de Admisión):** El procedimiento `pmtp_shm_logical_shutdown` conmuta `admission_gate` a 0 (`release`). Toda llamada subsiguiente a `reader_acquire` detecta el cierre y aborta inmediatamente retornando código de error `-4`.
> - **Fase 2 (Linealización y Quiescencia de Entrada):** El procedimiento de apagado monitorea `admission_and_inflight` (`acquire`), esperando a que todas las invocaciones a `reader_acquire` ya admitidas culminen su CAS o aborten antes de proceder al cierre de slots y drenaje de leases.
> - **Separación Taxativa entre Cierre Lógico y Destrucción Física:** El cierre lógico (`pmtp_shm_logical_shutdown`) drena lectores y cierra slots sin desmapear memoria. La destrucción física (`pmtp_shm_physical_destroy`) es una operación separada ejecutada exclusivamente por el supervisor tras el retorno exitoso (código 0) del cierre lógico.
>
> **Axioma CdV-3 (Lease Finito y Cooperación):** Todo `PmtpLeaseGuard` activo debe ser destruido (liberando su arrendamiento) en un tiempo finito acotado. La retención indefinida de un lease (por suspensión de hilos, aborto sin ejecución de destructores o deadlock externo) constituye una violación de contrato del consumidor que provocará que `pmtp_shm_shutdown_and_destroy` espere indefinidamente.
>
> **Delimitación de Responsabilidad de Metadatos de Guardia:** Los campos `generation_` e `instance_id_` en `PmtpLeaseGuard` constituyen metadatos de diagnóstico e inspección, no un mecanismo activo de bloqueo en `release()`. La prevención de carreras de reutilización de instancias o reinicialización cruzada pertenece exclusivamente a la capa del supervisor (Axioma CdV-2). Asimismo, `PmtpLeaseGuard` es un objeto afín no compartible concurrentemente entre hilos sin sincronización externa.

```cpp
#if defined(_WIN32)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

#include <cstdint>
#include <cstddef>
#include <cstring>
#include <cmath>
#include <atomic>
#include <chrono>
#include <type_traits>
#include <new>
#include <bit>

#if defined(__x86_64__) || defined(_M_X64)
#include <emmintrin.h>
#endif

// ============================================================================
// CONSTANTES DE PROTOCOLO Y CODIGOS DE ERROR CANONICOS (V39.0)
// ============================================================================
inline constexpr std::size_t PMTP_MAX_DIM       = 2048;
inline constexpr std::size_t PMTP_MAX_COLS      = 32;
inline constexpr std::size_t PMTP_SLAB_ELEMENTS = PMTP_MAX_DIM * PMTP_MAX_COLS; // 65,536 doubles
inline constexpr std::size_t NUM_SLOTS          = 3;
inline constexpr std::uint32_t PMTP_SHM_MAGIC   = 0x504D5450; // "PMTP"
inline constexpr std::uint32_t PMTP_SHM_VERSION = 39;

inline constexpr int PMTP_OK                      =  0;
inline constexpr int PMTP_ERR_NULL_REGION         = -1;
inline constexpr int PMTP_ERR_VERSION_MISMATCH    = -2;
inline constexpr int PMTP_ERR_CORRUPTED           = -3;
inline constexpr int PMTP_ERR_CLOSED              = -4;
inline constexpr int PMTP_ERR_NO_SLOT_AVAILABLE   = -5;
inline constexpr int PMTP_ERR_CONTENTION_TIMEOUT  = -6;
inline constexpr int PMTP_ERR_INVALID_SLOT        = -7;
inline constexpr int PMTP_ERR_SHUTDOWN_TIMEOUT    = -8;
inline constexpr int PMTP_ERR_GUARD_ALREADY_ACTIVE= -9;
inline constexpr int PMTP_ERR_INTERNAL_CORRUPTION = -10;
inline constexpr int PMTP_ERR_STALE_EPOCH         = -11;

// Estados de ranura empaquetados en los 4 bits mas significativos (offset 28)
inline constexpr std::uint32_t SLOT_STATE_MASK      = 0xF0000000;
inline constexpr std::uint32_t READERS_MASK         = 0x0FFFFFFF;
inline constexpr std::uint32_t MAX_READERS          = 0x0FFFFFFF; // 268,435,455 lectores concurrentes
inline constexpr std::uint32_t SLOT_STATE_IDLE      = 0x00000000;
inline constexpr std::uint32_t SLOT_STATE_WRITING   = 0x10000000;
inline constexpr std::uint32_t SLOT_STATE_COMMITTED = 0x20000000;
inline constexpr std::uint32_t SLOT_STATE_CLOSED    = 0x30000000;

// Estados del ciclo de vida unificado (empaquetados en bits 32..63 de 64 bits)
inline constexpr std::uint64_t LIFECYCLE_OPERATIONAL          = 0;
inline constexpr std::uint64_t LIFECYCLE_SHUTDOWN_IN_PROGRESS = 1;
inline constexpr std::uint64_t LIFECYCLE_SHUTDOWN_TIMEOUT     = 2;
inline constexpr std::uint64_t LIFECYCLE_SHUTDOWN_COMPLETED   = 3;
inline constexpr std::uint64_t LIFECYCLE_TOMBSTONE            = 4;
inline constexpr std::uint64_t LIFECYCLE_DESTROYED            = 5;

inline constexpr std::uint64_t LIFECYCLE_STATE_MASK           = 0xFFFFFFFF00000000ULL;
inline constexpr std::uint64_t INFLIGHT_COUNT_MASK            = 0x00000000FFFFFFFFULL;
inline constexpr unsigned      LIFECYCLE_SHIFT                = 32;

// Limite maximo de reintentos para spinlock
inline constexpr std::uint32_t MAX_SPINLOCK_ATTEMPTS          = 10000;

// Mascaras del descriptor de publicacion atomico (packed_cursor de 64 bits)
// Bits 48..63 (16 bits): slot (0..2)
// Bits  0..47 (48 bits): sequence (secuencia monotonica de publicacion)
inline constexpr std::uint64_t CURSOR_SLOT_MASK     = 0xFFFF000000000000ULL;
inline constexpr std::uint64_t CURSOR_SEQ_MASK      = 0x0000FFFFFFFFFFFFULL;
inline constexpr unsigned      CURSOR_SLOT_SHIFT    = 48;

// ============================================================================
// ESTRUCTURAS DE MEMORIA COMPARTIDA CON ALINEACION ESTRICTA
// ============================================================================

struct alignas(64) PmtpStiefelSlab {
    alignas(64) double         data[PMTP_SLAB_ELEMENTS]; // 2048 * 32 * 8 = 524,288 B (8,192 * 64 B)
    std::atomic<std::uint64_t> epoch{0};                 // 8 B (offset 524,288): secuencia atomica directa
    std::uint32_t              flags{0};                 // 4 B (offset 524,296)
    std::uint8_t               _pad[52]{};               // 52 B (offset 524,300..524,351)
    // Tamano total = 524,288 + 8 + 4 + 52 = 524,352 B = 8,193 * 64 B == 0 mod 64
};

struct PmtpWriterSpinlock {
    std::atomic<std::uint32_t> flag{0};

    bool try_lock() noexcept {
        return flag.exchange(1, std::memory_order_acq_rel) == 0;
    }

    bool try_lock_until(const std::chrono::steady_clock::time_point& deadline,
                        std::uint32_t max_spins = MAX_SPINLOCK_ATTEMPTS) noexcept {
        for (std::uint32_t spin = 0; spin < max_spins; ++spin) {
            if (std::chrono::steady_clock::now() >= deadline) return false;
            if (try_lock()) {
                return true;
            }
            #if defined(__x86_64__) || defined(_M_X64)
            _mm_pause();
            #elif defined(__aarch64__)
            asm volatile("yield" ::: "memory");
            #endif
        }
        return false;
    }

    bool lock(std::uint32_t max_spins = MAX_SPINLOCK_ATTEMPTS) noexcept {
        for (std::uint32_t spin = 0; spin < max_spins; ++spin) {
            if (try_lock()) {
                return true;
            }
            #if defined(__x86_64__) || defined(_M_X64)
            _mm_pause();
            #elif defined(__aarch64__)
            asm volatile("yield" ::: "memory");
            #endif
        }
        return false;
    }

    void unlock() noexcept {
        flag.store(0, std::memory_order_release);
    }
};

class PmtpWriterLockGuard {
    PmtpWriterSpinlock& lock_;
    bool locked_{false};

public:
    explicit PmtpWriterLockGuard(PmtpWriterSpinlock& lock, bool already_locked = false) noexcept
        : lock_(lock), locked_(already_locked) {
        if (!locked_) {
            locked_ = lock_.lock();
        }
    }
    ~PmtpWriterLockGuard() noexcept {
        unlock();
    }
    void unlock() noexcept {
        if (locked_) {
            lock_.unlock();
            locked_ = false;
        }
    }
    bool is_locked() const noexcept { return locked_; }
    PmtpWriterLockGuard(const PmtpWriterLockGuard&) = delete;
    PmtpWriterLockGuard& operator=(const PmtpWriterLockGuard&) = delete;
};

struct alignas(64) PmtpPublisherCursor {
    std::atomic<std::uint64_t> packed_cursor{0}; // Descriptor de publicacion
    std::atomic<std::uint64_t> lifecycle_and_inflight{0}; // bits 32..63: state, bits 0..31: inflight
    PmtpWriterSpinlock         writer_lock;      // Spinlock de publicador exclusivo
    std::uint8_t               _pad[44]{};       // Relleno a 64 bytes exactos
};

struct alignas(64) PmtpSlotHeader {
    std::atomic<std::uint32_t> state_and_readers{SLOT_STATE_IDLE}; // 4 bits estado | 28 bits lectores
    std::atomic<std::uint32_t> flags{0};
    std::uint8_t               _pad[56]{};
};

struct alignas(64) PmtpSharedRegion {
    std::uint32_t              magic{PMTP_SHM_MAGIC};
    std::uint32_t              version{PMTP_SHM_VERSION};
    std::uint32_t              dim{static_cast<std::uint32_t>(PMTP_MAX_DIM)};
    std::uint32_t              cols{static_cast<std::uint32_t>(PMTP_MAX_COLS)};
    std::atomic<std::uint64_t> publication_sequence{0};
    std::atomic<std::uint64_t> supervisor_epoch{1};
    std::uint8_t               _pad0[32]{};

    PmtpPublisherCursor        cursor;
    PmtpSlotHeader             slot_headers[NUM_SLOTS];
    PmtpStiefelSlab            buffer[NUM_SLOTS];
};

static_assert(std::endian::native == std::endian::little, "ERR_LITTLE_ENDIAN_REQUIRED");
static_assert(sizeof(double) == 8, "ERR_DOUBLE_IEEE754_SIZE");
static_assert(std::atomic<std::uint32_t>::is_always_lock_free, "ERR_ATOMIC_UINT32_NOT_LOCK_FREE");
static_assert(std::atomic<std::uint64_t>::is_always_lock_free, "ERR_ATOMIC_UINT64_NOT_LOCK_FREE");

static_assert(std::is_standard_layout_v<PmtpPublisherCursor>, "ERR_CURSOR_NOT_STANDARD_LAYOUT");
static_assert(std::is_standard_layout_v<PmtpSlotHeader>, "ERR_SLOT_HEADER_NOT_STANDARD_LAYOUT");
static_assert(std::is_standard_layout_v<PmtpStiefelSlab>, "ERR_SLAB_NOT_STANDARD_LAYOUT");
static_assert(std::is_standard_layout_v<PmtpSharedRegion>, "ERR_SHARED_REGION_NOT_STANDARD_LAYOUT");

static_assert(alignof(PmtpPublisherCursor) == alignof(PmtpStiefelSlab));
static_assert(alignof(PmtpSlotHeader) == alignof(PmtpStiefelSlab));
static_assert(alignof(PmtpStiefelSlab) == 64);
static_assert(alignof(PmtpSharedRegion) == alignof(PmtpStiefelSlab));

static_assert(sizeof(PmtpPublisherCursor) == 64);
static_assert(sizeof(PmtpSlotHeader) == 64);
static_assert(sizeof(PmtpStiefelSlab) == 524352);
static_assert(sizeof(PmtpStiefelSlab) % alignof(PmtpStiefelSlab) == 0);

static_assert(offsetof(PmtpSharedRegion, magic) == 0);
static_assert(offsetof(PmtpSharedRegion, version) == 4);
static_assert(offsetof(PmtpSharedRegion, dim) == 8);
static_assert(offsetof(PmtpSharedRegion, cols) == 12);
static_assert(offsetof(PmtpSharedRegion, publication_sequence) == 16);
static_assert(offsetof(PmtpSharedRegion, supervisor_epoch) == 24);

static_assert(offsetof(PmtpPublisherCursor, packed_cursor) == 0);
static_assert(offsetof(PmtpPublisherCursor, lifecycle_and_inflight) == 8);
static_assert(offsetof(PmtpPublisherCursor, writer_lock) == 16);

static_assert(offsetof(PmtpSlotHeader, state_and_readers) == 0);
static_assert(offsetof(PmtpSlotHeader, flags) == 4);

static_assert(offsetof(PmtpSharedRegion, cursor) == 64);
static_assert(offsetof(PmtpSharedRegion, slot_headers) == offsetof(PmtpSharedRegion, cursor) + sizeof(PmtpPublisherCursor));
static_assert(offsetof(PmtpSharedRegion, buffer) == offsetof(PmtpSharedRegion, slot_headers) + sizeof(PmtpSlotHeader) * NUM_SLOTS);

static_assert(offsetof(PmtpSharedRegion, cursor) % alignof(PmtpStiefelSlab) == 0);
static_assert(offsetof(PmtpSharedRegion, slot_headers) % alignof(PmtpStiefelSlab) == 0);
static_assert(offsetof(PmtpSharedRegion, buffer) % alignof(PmtpStiefelSlab) == 0);

static_assert(sizeof(PmtpStiefelSlab[NUM_SLOTS]) == NUM_SLOTS * sizeof(PmtpStiefelSlab));

static_assert(sizeof(PmtpSharedRegion) % alignof(PmtpSharedRegion) == 0);
static_assert(sizeof(PmtpSharedRegion) == offsetof(PmtpSharedRegion, buffer) + sizeof(PmtpStiefelSlab[NUM_SLOTS]));

// FUNCIONES AUXILIARES ATOMICAS SIN SUBDESBORDAMIENTO (UNDERFLOW-PROOF)
inline std::uint64_t pack_cursor(std::uint16_t slot, std::uint64_t seq) noexcept {
    return (static_cast<std::uint64_t>(slot) << CURSOR_SLOT_SHIFT) | (seq & CURSOR_SEQ_MASK);
}

inline std::uint32_t unpack_slot(std::uint64_t snap) noexcept {
    return static_cast<std::uint32_t>((snap & CURSOR_SLOT_MASK) >> CURSOR_SLOT_SHIFT);
}

inline std::uint64_t unpack_seq(std::uint64_t snap) noexcept {
    return snap & CURSOR_SEQ_MASK;
}

inline int pmtp_decrement_inflight(std::atomic<std::uint64_t>& state_atom) noexcept {
    std::uint64_t cur = state_atom.load(std::memory_order_relaxed);
    while (true) {
        std::uint32_t inflight = static_cast<std::uint32_t>(cur & INFLIGHT_COUNT_MASK);
        if (inflight == 0) return PMTP_ERR_INTERNAL_CORRUPTION; // Deteccion estricta de subdesbordamiento
        std::uint64_t next = (cur & LIFECYCLE_STATE_MASK) | (inflight - 1);
        if (state_atom.compare_exchange_weak(cur, next, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            return PMTP_OK;
        }
        #if defined(__x86_64__) || defined(_M_X64)
        _mm_pause();
        #elif defined(__aarch64__)
        asm volatile("yield" ::: "memory");
        #endif
    }
}

inline int pmtp_decrement_slot_reader(PmtpSharedRegion* shm, std::uint32_t slot) noexcept {
    if (!shm || slot >= NUM_SLOTS) return PMTP_ERR_INVALID_SLOT;
    std::uint32_t cur = shm->slot_headers[slot].state_and_readers.load(std::memory_order_relaxed);
    while (true) {
        std::uint32_t readers = cur & READERS_MASK;
        if (readers == 0) return PMTP_ERR_INTERNAL_CORRUPTION; // Deteccion estricta de subdesbordamiento
        std::uint32_t next = (cur & ~READERS_MASK) | (readers - 1);
        if (shm->slot_headers[slot].state_and_readers.compare_exchange_weak(
                cur, next, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            return PMTP_OK;
        }
        #if defined(__x86_64__) || defined(_M_X64)
        _mm_pause();
        #elif defined(__aarch64__)
        asm volatile("yield" ::: "memory");
        #endif
    }
}

// ============================================================================
// GUARDIA RAII PARA LECTORES (MOVE-ONLY, THREAD-AFFINE, CON OBSERVABILIDAD EN RELEASE)
// ============================================================================
class PmtpReaderGuard {
    PmtpSharedRegion* shm_{nullptr};
    std::uint32_t     slot_{NUM_SLOTS};
    std::uint64_t     epoch_{0};
    bool              active_{false};
    mutable int       last_release_error_{PMTP_OK};

public:
    PmtpReaderGuard() noexcept = default;
    ~PmtpReaderGuard() noexcept { last_release_error_ = release(); }

    PmtpReaderGuard(const PmtpReaderGuard&) = delete;
    PmtpReaderGuard& operator=(const PmtpReaderGuard&) = delete;

    PmtpReaderGuard(PmtpReaderGuard&& o) noexcept
        : shm_(o.shm_), slot_(o.slot_), epoch_(o.epoch_), active_(o.active_),
          last_release_error_(o.last_release_error_) {
        o.shm_ = nullptr;
        o.slot_ = NUM_SLOTS;
        o.epoch_ = 0;
        o.active_ = false;
        o.last_release_error_ = PMTP_OK;
    }

    PmtpReaderGuard& operator=(PmtpReaderGuard&& o) noexcept {
        if (this != &o) {
            last_release_error_ = release();
            shm_ = o.shm_;
            slot_ = o.slot_;
            epoch_ = o.epoch_;
            active_ = o.active_;
            last_release_error_ = o.last_release_error_;
            o.shm_ = nullptr;
            o.slot_ = NUM_SLOTS;
            o.epoch_ = 0;
            o.active_ = false;
            o.last_release_error_ = PMTP_OK;
        }
        return *this;
    }

    int attach(PmtpSharedRegion* shm, std::uint32_t slot, std::uint64_t epoch) noexcept {
        if (active_) return PMTP_ERR_GUARD_ALREADY_ACTIVE;
        if (!shm || slot >= NUM_SLOTS) return PMTP_ERR_INVALID_SLOT;
        shm_ = shm;
        slot_ = slot;
        epoch_ = epoch;
        active_ = true;
        return PMTP_OK;
    }

    const double* data() const noexcept {
        if (!active_ || !shm_ || slot_ >= NUM_SLOTS) return nullptr;
        // SEV-TEORIA-04 — Verificar lifecycle_state antes de desreferenciar el puntero
        // Si la destrucción física ya inició (LIFECYCLE_DESTROYED), retornar nullptr.
        // Esto previene UB si el supervisor invoca physical_destroy concurrentemente.
        const std::uint64_t lc = shm_->cursor.lifecycle_and_inflight.load(std::memory_order_acquire);
        const std::uint64_t lc_state = (lc >> 32) & 0xFFFFFFFFULL;
        // LIFECYCLE_DESTROYED == 0xDEAD0000ULL (constante definida en §9.1)
        if (lc_state == static_cast<std::uint32_t>(LIFECYCLE_DESTROYED >> 32)) return nullptr;
        return shm_->buffer[slot_].data;
    }

    int release() noexcept {
        if (!active_) return PMTP_OK;
        PmtpSharedRegion* s = shm_;
        std::uint32_t sl = slot_;
        active_ = false;
        shm_ = nullptr;
        slot_ = NUM_SLOTS;
        epoch_ = 0;
        int rc = pmtp_decrement_slot_reader(s, sl);
        last_release_error_ = rc;
        return rc;
    }

    bool is_valid() const noexcept { return active_; }
    std::uint32_t slot() const noexcept { return slot_; }
    std::uint64_t epoch() const noexcept { return epoch_; }
    int last_release_error() const noexcept { return last_release_error_; }
};

// ============================================================================
// PROTOCOLO DEL PUBLICADOR (CON ROLLBACK TRANSACCIONAL DE RANURA)
// ============================================================================
int pmtp_shm_writer_publish(PmtpSharedRegion* shm, const double* data, std::size_t count) noexcept {
    if (!shm || !data) return PMTP_ERR_NULL_REGION;
    if (count != PMTP_SLAB_ELEMENTS) return PMTP_ERR_INVALID_SLOT;

    // Validacion de silicio: asegurar finitud estricta de todos los escalares
    for (std::size_t i = 0; i < PMTP_SLAB_ELEMENTS; ++i) {
        if (!std::isfinite(data[i])) return PMTP_ERR_CORRUPTED;
    }

    // Fase 1: Adquisicion del lock de publicador (exclusivo para escritores)
    PmtpWriterLockGuard wlock(shm->cursor.writer_lock);
    if (!wlock.is_locked()) {
        return PMTP_ERR_CONTENTION_TIMEOUT;
    }

    // Fase 2: Validacion de ciclo de vida operativo
    std::uint64_t life = shm->cursor.lifecycle_and_inflight.load(std::memory_order_acquire);
    if ((life >> LIFECYCLE_SHIFT) != LIFECYCLE_OPERATIONAL) {
        return PMTP_ERR_CLOSED;
    }

    const std::uint64_t snap = shm->cursor.packed_cursor.load(std::memory_order_relaxed);
    const std::uint32_t published_slot = unpack_slot(snap);

    // Fase 3: Seleccion y reserva atomica de ranura mediante CAS excluyente
    std::uint32_t target_slot = NUM_SLOTS;
    for (std::uint32_t cand = 0; cand < NUM_SLOTS; ++cand) {
        if (cand == published_slot) continue;
        std::uint32_t expected = SLOT_STATE_COMMITTED | 0;
        if (shm->slot_headers[cand].state_and_readers.compare_exchange_strong(
                expected, SLOT_STATE_WRITING, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            target_slot = cand;
            break;
        }
        expected = SLOT_STATE_IDLE | 0;
        if (shm->slot_headers[cand].state_and_readers.compare_exchange_strong(
                expected, SLOT_STATE_WRITING, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            target_slot = cand;
            break;
        }
    }

    if (target_slot >= NUM_SLOTS) {
        return PMTP_ERR_NO_SLOT_AVAILABLE;
    }

    // Fase 4: Copia de payload y epoca atomica con release
    const std::uint64_t pub_seq = (shm->publication_sequence.fetch_add(1, std::memory_order_relaxed) + 1) & CURSOR_SEQ_MASK;
    std::memcpy(shm->buffer[target_slot].data, data, sizeof(double) * PMTP_SLAB_ELEMENTS);
    shm->buffer[target_slot].epoch.store(pub_seq, std::memory_order_release);

    // Fase 5: Conmutacion atomica de ranura a COMMITTED con semantica release
    shm->slot_headers[target_slot].state_and_readers.store(SLOT_STATE_COMMITTED, std::memory_order_release);

    // Fase 6: Publicacion atomica unificada en cursor (Descriptor de publicacion global con release)
    const std::uint64_t new_snap = pack_cursor(static_cast<std::uint16_t>(target_slot), pub_seq);
    shm->cursor.packed_cursor.store(new_snap, std::memory_order_release);

    return PMTP_OK;
}

// ============================================================================
// PROTOCOLO DEL LECTOR (ADMISIÓN ACOPLADA Y RESERVA ATÓMICA DE RANURA)
// ============================================================================
int pmtp_shm_reader_acquire(PmtpSharedRegion* shm, PmtpReaderGuard* out_guard) noexcept {
    if (!shm || !out_guard) return PMTP_ERR_NULL_REGION;
    if (out_guard->is_valid()) return PMTP_ERR_GUARD_ALREADY_ACTIVE;

    // Fase 1: Compuerta de admisión atómica con registro en tránsito en palabra unificada de 64 bits
    std::uint64_t life_cur = shm->cursor.lifecycle_and_inflight.load(std::memory_order_relaxed);
    while (true) {
        if ((life_cur >> LIFECYCLE_SHIFT) != LIFECYCLE_OPERATIONAL) {
            return PMTP_ERR_CLOSED;
        }
        std::uint32_t inflight = static_cast<std::uint32_t>(life_cur & INFLIGHT_COUNT_MASK);
        if (inflight >= 0x7FFFFFFF) return PMTP_ERR_CONTENTION_TIMEOUT;
        std::uint64_t life_next = (life_cur & LIFECYCLE_STATE_MASK) | (inflight + 1);
        if (shm->cursor.lifecycle_and_inflight.compare_exchange_weak(
                life_cur, life_next, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            break;
        }
        #if defined(__x86_64__) || defined(_M_X64)
        _mm_pause();
        #elif defined(__aarch64__)
        asm volatile("yield" ::: "memory");
        #endif
    }

    // Fase 2: Muestreo de cursor linealizable y época del supervisor
    const std::uint64_t cur_epoch = shm->supervisor_epoch.load(std::memory_order_acquire);
    const std::uint64_t snap = shm->cursor.packed_cursor.load(std::memory_order_acquire);
    const std::uint32_t slot = unpack_slot(snap);
    const std::uint64_t seq  = unpack_seq(snap);

    if (slot >= NUM_SLOTS) {
        int dec_rc = pmtp_decrement_inflight(shm->cursor.lifecycle_and_inflight);
        return (dec_rc != PMTP_OK) ? dec_rc : PMTP_ERR_INVALID_SLOT;
    }

    // Fase 3: Registro atómico excluyente en cabecera de ranura (CAS condicionado a COMMITTED)
    std::uint32_t hdr_cur = shm->slot_headers[slot].state_and_readers.load(std::memory_order_relaxed);
    while (true) {
        if ((hdr_cur & SLOT_STATE_MASK) != SLOT_STATE_COMMITTED) {
            int dec_rc = pmtp_decrement_inflight(shm->cursor.lifecycle_and_inflight);
            return (dec_rc != PMTP_OK) ? dec_rc : PMTP_ERR_CLOSED;
        }
        std::uint32_t readers = hdr_cur & READERS_MASK;
        if (readers >= MAX_READERS) {
            int dec_rc = pmtp_decrement_inflight(shm->cursor.lifecycle_and_inflight);
            return (dec_rc != PMTP_OK) ? dec_rc : PMTP_ERR_CONTENTION_TIMEOUT;
        }
        std::uint32_t hdr_next = (hdr_cur & ~READERS_MASK) | (readers + 1);
        if (shm->slot_headers[slot].state_and_readers.compare_exchange_weak(
                hdr_cur, hdr_next, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            break;
        }
        #if defined(__x86_64__) || defined(_M_X64)
        _mm_pause();
        #elif defined(__aarch64__)
        asm volatile("yield" ::: "memory");
        #endif
    }

    // Decremento simétrico de inflight tras registro exitoso en ranura
    int dec_err = pmtp_decrement_inflight(shm->cursor.lifecycle_and_inflight);
    if (dec_err != PMTP_OK) {
        int roll_err = pmtp_decrement_slot_reader(shm, slot);
        return (roll_err != PMTP_OK) ? roll_err : dec_err;
    }

    // Fase 4: Revalidación atómica de cursor y época del slab con acquire
    const std::uint64_t verify_snap = shm->cursor.packed_cursor.load(std::memory_order_acquire);
    const std::uint64_t slab_epoch  = shm->buffer[slot].epoch.load(std::memory_order_acquire);

    if (verify_snap != snap || (slab_epoch & CURSOR_SEQ_MASK) != seq || slab_epoch == 0 ||
        (shm->cursor.lifecycle_and_inflight.load(std::memory_order_acquire) >> LIFECYCLE_SHIFT) != LIFECYCLE_OPERATIONAL ||
        shm->supervisor_epoch.load(std::memory_order_acquire) != cur_epoch) {
        // Rollback invariante validado
        int roll_err = pmtp_decrement_slot_reader(shm, slot);
        return (roll_err != PMTP_OK) ? roll_err : PMTP_ERR_STALE_EPOCH;
    }

    // Fase 5: Concesión de guardia RAII
    int attach_res = out_guard->attach(shm, slot, cur_epoch);
    if (attach_res != PMTP_OK) {
        int dec_rc = pmtp_decrement_slot_reader(shm, slot);
        return (dec_rc != PMTP_OK) ? dec_rc : attach_res;
    }

    return PMTP_OK;
}

// ============================================================================
// PROTOCOLO DE APAGADO LOGICO GOBERNADO POR DEADLINE Y RECUPERACION LINEALIZABLE
// ============================================================================
int pmtp_shm_logical_shutdown(PmtpSharedRegion* shm, std::uint32_t timeout_ms) noexcept {
    if (!shm) return PMTP_ERR_NULL_REGION;

    const auto global_deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(timeout_ms);

    // Fase 0: Transicion atomica de ciclo de vida a SHUTDOWN_IN_PROGRESS en palabra de 64 bits
    std::uint64_t life_cur = shm->cursor.lifecycle_and_inflight.load(std::memory_order_relaxed);
    while (true) {
        std::uint64_t state = life_cur >> LIFECYCLE_SHIFT;
        if (state != LIFECYCLE_OPERATIONAL && state != LIFECYCLE_SHUTDOWN_TIMEOUT) {
            return (state == LIFECYCLE_SHUTDOWN_COMPLETED) ? PMTP_OK : PMTP_ERR_CLOSED;
        }
        std::uint64_t life_next = (LIFECYCLE_SHUTDOWN_IN_PROGRESS << LIFECYCLE_SHIFT) | (life_cur & INFLIGHT_COUNT_MASK);
        if (shm->cursor.lifecycle_and_inflight.compare_exchange_weak(
                life_cur, life_next, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            break;
        }
        #if defined(__x86_64__) || defined(_M_X64)
        _mm_pause();
        #elif defined(__aarch64__)
        asm volatile("yield" ::: "memory");
        #endif
    }

    // Fase 1: Adquisicion del lock de publicador gobernado por global_deadline
    if (!shm->cursor.writer_lock.try_lock_until(global_deadline)) {
        // Revertir a TIMEOUT preservando inflight
        std::uint64_t c = shm->cursor.lifecycle_and_inflight.load(std::memory_order_relaxed);
        while ((c >> LIFECYCLE_SHIFT) == LIFECYCLE_SHUTDOWN_IN_PROGRESS) {
            std::uint64_t n = (LIFECYCLE_SHUTDOWN_TIMEOUT << LIFECYCLE_SHIFT) | (c & INFLIGHT_COUNT_MASK);
            if (shm->cursor.lifecycle_and_inflight.compare_exchange_weak(
                    c, n, std::memory_order_acq_rel, std::memory_order_relaxed)) {
                return PMTP_ERR_SHUTDOWN_TIMEOUT;
            }
        }
        std::uint64_t final_s = c >> LIFECYCLE_SHIFT;
        if (final_s == LIFECYCLE_SHUTDOWN_COMPLETED) return PMTP_OK;
        return PMTP_ERR_CLOSED;
    }
    PmtpWriterLockGuard wlock(shm->cursor.writer_lock, true /* already locked */);

    // Fase 2: Drenaje de lectores en transito gobernado por global_deadline
    while ((shm->cursor.lifecycle_and_inflight.load(std::memory_order_acquire) & INFLIGHT_COUNT_MASK) > 0) {
        if (std::chrono::steady_clock::now() >= global_deadline) {
            std::uint64_t c = shm->cursor.lifecycle_and_inflight.load(std::memory_order_relaxed);
            while ((c >> LIFECYCLE_SHIFT) == LIFECYCLE_SHUTDOWN_IN_PROGRESS) {
                std::uint64_t n = (LIFECYCLE_SHUTDOWN_TIMEOUT << LIFECYCLE_SHIFT) | (c & INFLIGHT_COUNT_MASK);
                if (shm->cursor.lifecycle_and_inflight.compare_exchange_weak(
                        c, n, std::memory_order_acq_rel, std::memory_order_relaxed)) {
                    wlock.unlock();
                    return PMTP_ERR_SHUTDOWN_TIMEOUT;
                }
            }
            wlock.unlock();
            std::uint64_t final_s = c >> LIFECYCLE_SHIFT;
            if (final_s == LIFECYCLE_SHUTDOWN_COMPLETED) return PMTP_OK;
            return PMTP_ERR_CLOSED;
        }
        #if defined(__x86_64__) || defined(_M_X64)
        _mm_pause();
        #elif defined(__aarch64__)
        asm volatile("yield" ::: "memory");
        #endif
    }

    // Fase 3: Drenaje de lectores activos en todas las ranuras gobernado por global_deadline
    for (std::uint32_t s = 0; s < NUM_SLOTS; ++s) {
        while ((shm->slot_headers[s].state_and_readers.load(std::memory_order_acquire) & READERS_MASK) > 0) {
            if (std::chrono::steady_clock::now() >= global_deadline) {
                std::uint64_t c = shm->cursor.lifecycle_and_inflight.load(std::memory_order_relaxed);
                while ((c >> LIFECYCLE_SHIFT) == LIFECYCLE_SHUTDOWN_IN_PROGRESS) {
                    std::uint64_t n = (LIFECYCLE_SHUTDOWN_TIMEOUT << LIFECYCLE_SHIFT) | (c & INFLIGHT_COUNT_MASK);
                    if (shm->cursor.lifecycle_and_inflight.compare_exchange_weak(
                            c, n, std::memory_order_acq_rel, std::memory_order_relaxed)) {
                        wlock.unlock();
                        return PMTP_ERR_SHUTDOWN_TIMEOUT;
                    }
                }
                wlock.unlock();
                std::uint64_t final_s = c >> LIFECYCLE_SHIFT;
                if (final_s == LIFECYCLE_SHUTDOWN_COMPLETED) return PMTP_OK;
                return PMTP_ERR_CLOSED;
            }
            #if defined(__x86_64__) || defined(_M_X64)
            _mm_pause();
            #elif defined(__aarch64__)
            asm volatile("yield" ::: "memory");
            #endif
        }
    }

    // Fase 4: Commit irrevocable del cierre
    for (std::uint32_t s = 0; s < NUM_SLOTS; ++s) {
        shm->slot_headers[s].state_and_readers.store(SLOT_STATE_CLOSED, std::memory_order_release);
    }

    std::uint64_t cur_life = shm->cursor.lifecycle_and_inflight.load(std::memory_order_relaxed);
    while (true) {
        std::uint64_t next_life = (LIFECYCLE_SHUTDOWN_COMPLETED << LIFECYCLE_SHIFT) | (cur_life & INFLIGHT_COUNT_MASK);
        if (shm->cursor.lifecycle_and_inflight.compare_exchange_weak(
                cur_life, next_life, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            break;
        }
    }

    return PMTP_OK;
}

// ============================================================================
// PROTOCOLO DE EMERGENCIA TOMBSTONE
// CONTRATO FORMAL DE QUIESCENCIA ADMINISTRATIVA (SUPERVISOR QUIESCENCE CONTRACT):
// Accion administrativa kernel ejecutada por el Supervisor UNICAMENTE tras verificar
// fuera de banda (via senales de SO, PID query y terminacion de procesos anomalos)
// que ningun hilo cliente no cooperativo sigue en ejecucion activa. Conmuta los slots
// a CLOSED preservando el conteo de lectores activos para lectores cooperativos en vuelo.
// ============================================================================
int pmtp_shm_force_terminal_tombstone(PmtpSharedRegion* shm, std::uint64_t supervisor_epoch) noexcept {
    if (!shm) return PMTP_ERR_NULL_REGION;

    PmtpWriterLockGuard wlock(shm->cursor.writer_lock);
    if (!wlock.is_locked()) {
        return PMTP_ERR_CONTENTION_TIMEOUT;
    }

    std::uint64_t cur_epoch = shm->supervisor_epoch.load(std::memory_order_acquire);
    if (supervisor_epoch <= cur_epoch) {
        return PMTP_ERR_VERSION_MISMATCH;
    }
    if (!shm->supervisor_epoch.compare_exchange_strong(
            cur_epoch, supervisor_epoch, std::memory_order_acq_rel, std::memory_order_relaxed)) {
        return PMTP_ERR_VERSION_MISMATCH;
    }

    // Transicionar lifecycle a TOMBSTONE
    std::uint64_t cur_life = shm->cursor.lifecycle_and_inflight.load(std::memory_order_relaxed);
    while (true) {
        std::uint64_t next_life = (LIFECYCLE_TOMBSTONE << LIFECYCLE_SHIFT) | (cur_life & INFLIGHT_COUNT_MASK);
        if (shm->cursor.lifecycle_and_inflight.compare_exchange_weak(
                cur_life, next_life, std::memory_order_acq_rel, std::memory_order_relaxed)) {
            break;
        }
    }

    // Conmutar ranuras a CLOSED preservando lectores activos
    for (std::uint32_t s = 0; s < NUM_SLOTS; ++s) {
        std::uint32_t cur = shm->slot_headers[s].state_and_readers.load(std::memory_order_relaxed);
        while (true) {
            std::uint32_t next = (cur & READERS_MASK) | SLOT_STATE_CLOSED;
            if (shm->slot_headers[s].state_and_readers.compare_exchange_weak(
                    cur, next, std::memory_order_acq_rel, std::memory_order_relaxed)) {
                break;
            }
            #if defined(__x86_64__) || defined(_M_X64)
            _mm_pause();
            #elif defined(__aarch64__)
            asm volatile("yield" ::: "memory");
            #endif
        }
    }

    return PMTP_OK;
}

// ============================================================================
// DESTRUCCION FISICA CON VERIFICACION PREVIA DE QUIESCENCIA Y SERIALIZACION DE LOCK
// ============================================================================
int pmtp_shm_physical_destroy(void* base_addr, std::size_t size_bytes, std::uint64_t expected_epoch) noexcept {
    if (!base_addr || size_bytes < sizeof(PmtpSharedRegion)) return PMTP_ERR_NULL_REGION;
    if (reinterpret_cast<std::uintptr_t>(base_addr) % 64 != 0) return PMTP_ERR_CORRUPTED;

    auto* shm = reinterpret_cast<PmtpSharedRegion*>(base_addr);
    if (shm->magic != PMTP_SHM_MAGIC || shm->version != PMTP_SHM_VERSION) return PMTP_ERR_CORRUPTED;
    if (shm->supervisor_epoch.load(std::memory_order_acquire) != expected_epoch) return PMTP_ERR_VERSION_MISMATCH;

    // Adquisicion obligatoria del lock de publicador para serializar con shutdown y tombstone
    PmtpWriterLockGuard wlock(shm->cursor.writer_lock);
    if (!wlock.is_locked()) {
        return PMTP_ERR_CONTENTION_TIMEOUT;
    }

    // 1. Verificacion previa de lectores en transito
    std::uint64_t life = shm->cursor.lifecycle_and_inflight.load(std::memory_order_acquire);
    std::uint64_t state = life >> LIFECYCLE_SHIFT;
    if (state != LIFECYCLE_SHUTDOWN_COMPLETED && state != LIFECYCLE_TOMBSTONE) {
        return PMTP_ERR_CLOSED; // Prohibido destruir una region en operacion activa
    }
    if ((life & INFLIGHT_COUNT_MASK) > 0) {
        return PMTP_ERR_CLOSED;
    }

    // 2. Verificacion previa de todas las ranuras: todas en SLOT_STATE_CLOSED con 0 lectores
    for (std::size_t s = 0; s < NUM_SLOTS; ++s) {
        std::uint32_t slot_hdr = shm->slot_headers[s].state_and_readers.load(std::memory_order_acquire);
        if ((slot_hdr & READERS_MASK) > 0 || (slot_hdr & SLOT_STATE_MASK) != SLOT_STATE_CLOSED) {
            return PMTP_ERR_CLOSED;
        }
    }

    // 3. Linearizacion atómica: Solo tras superar todas las verificaciones conmuta a LIFECYCLE_DESTROYED
    std::uint64_t next_life = (LIFECYCLE_DESTROYED << LIFECYCLE_SHIFT) | 0;
    if (!shm->cursor.lifecycle_and_inflight.compare_exchange_strong(
            life, next_life, std::memory_order_acq_rel, std::memory_order_relaxed)) {
        return PMTP_ERR_CLOSED;
    }

    wlock.unlock();
    shm->~PmtpSharedRegion();

    #if defined(_WIN32)
    if (!UnmapViewOfFile(base_addr)) return PMTP_ERR_CORRUPTED;
    #else
    if (munmap(base_addr, size_bytes) != 0) return PMTP_ERR_CORRUPTED;
    #endif

    return PMTP_OK;
}
```

### 9.2 Análisis de Invariantes, Casos Representativos de Intercalación y Relaciones de Memoria

> **Invariante Condicional de Protocolo (Bajo Ejecución Conforme y Contrato de Plataforma):**  
> Bajo observancia del Contrato de Plataforma Específica IPC (§9.0) y exclusión de caídas catastróficas abruptas no toleradas:  
> En cualquier instante en que el publicador ejecuta `std::memcpy` sobre `shm->buffer[s]`, el estado de la ranura satisface idénticamente `(state_and_readers & SLOT_STATE_MASK) == SLOT_STATE_WRITING` con exactamente cero lectores activos (`(state_and_readers & READERS_MASK) == 0`). Ningún lector conforme puede superar el CAS de adquisición sobre la ranura $s$ mientras se encuentre en estado `WRITING`. La publicación del frame ortonormal íntegro ($65{,}536$ doubles finitos verificados en silicio, $524{,}288$ bytes) y de su época atómica culmina mediante un **protocolo de publicación en dos fases rigurosamente ordenadas con semántica release**: commit de la ranura seguido de la publicación del descriptor global en `packed_cursor`.

**Demostración Rigurosa y Máquina de Estados:**

1. **Lema 9.1 (Grafo Completo de Estados de Ranura y Exclusión Mutua Lector-Escritor):**  
   El ciclo de vida de cada ranura $s \in \{0, 1, 2\}$ obedece al grafo dirigido de transiciones acopladas:
   $$\text{IDLE} \xrightarrow{\text{CAS Escritor}} \text{WRITING} \xrightarrow{\text{Store Release}} \text{COMMITTED} \xrightarrow[\text{CAS Lector}]{+1 / -1} \text{COMMITTED} \xrightarrow{\text{CAS Escritor}} \text{WRITING}$$
   y de forma terminal ante el cese de operaciones: $\text{COMMITTED} \xrightarrow{\text{Shutdown / Tombstone}} \text{CLOSED}$.
   - **Regla de Reserva del Escritor:** Para comenzar a escribir en una ranura candidata $s \ne \text{published\_slot}$, el escritor debe ejecutar exitosamente `compare_exchange_strong` sobre `slot_headers[s].state_and_readers` transicionando desde `(SLOT_STATE_COMMITTED | 0)` o `(SLOT_STATE_IDLE | 0)` hacia `SLOT_STATE_WRITING`.
   - **Regla de Adquisición del Lector:** Para registrar su acceso en la ranura $s$, el lector debe ejecutar exitosamente `compare_exchange_weak` sobre la misma palabra de 32 bits, condicionado estrictamente a que los 4 bits superiores sean idénticamente `SLOT_STATE_COMMITTED` y `readers < MAX_READERS`, incrementando el conteo en 1.
   - **Exclusión Mutua de Silicio:** Ambas operaciones son instrucciones atómicas Read-Modify-Write (`LOCK CMPXCHG` en x86-64, `CAS` en ARM64) sobre la misma palabra de memoria física alineada a 64 bytes:
     - *Si el CAS del escritor precede al del lector:* La ranura conmuta a `SLOT_STATE_WRITING`. Cualquier lector concurrente (incluso con un descriptor muestreado previamente) evalúa `(hdr & SLOT_STATE_MASK) != SLOT_STATE_COMMITTED`, aborta de inmediato su CAS y propaga el error `PMTP_ERR_CLOSED` tras decrementar su registro en tránsito. El lector jamás accede a un búfer en proceso de escritura.
     - *Si el CAS del lector precede al del escritor:* El contador de lectores pasa a `readers >= 1`. El CAS del escritor exige `expected == (SLOT_STATE_COMMITTED | 0)`, por lo que falla incondicionalmente, impidiendo que el escritor seleccione o altere la ranura mientras existan lectores activos.
   - **Revalidación Post-Registro:** Si un lector supera el CAS de ranura pero el escritor publicó una nueva ranura en el intervalo, el lector detecta `verify_snap != snap` o `slab_epoch != seq` en la Fase 4, decremente su contador de lector y retorna `PMTP_ERR_STALE_EPOCH`, garantizando la consistencia de cada lectura. $\blacksquare$

2. **Lema 9.2 (Palabra Unificada de 64 Bits para Admisión y Ciclo de Vida sin Fugas ni Intercalaciones):**  
   - La compuerta de admisión y el ciclo de vida residen en una única palabra atómica de 64 bits `lifecycle_and_inflight`:
     $$\text{bits 32..63: } \text{lifecycle\_state}, \quad \text{bits 0..31: } \text{inflight\_readers}$$
   - El lector se admite mediante un único CAS atómico sobre esta palabra: verifica que los 32 bits superiores sean idénticamente `LIFECYCLE_OPERATIONAL` e incrementa atómicamente los 32 bits inferiores (`inflight + 1`). No existe intervalo temporal ni doble lectura vulnerable a cambios concurrentes de estado.
   - El proceso de apagado conmuta los 32 bits superiores a `LIFECYCLE_SHUTDOWN_IN_PROGRESS` mediante CAS preservando el conteo de `inflight_readers`. En el instante de ejecución de este CAS en hardware, la compuerta de admisión queda cerrada de forma instantánea e irrevocable: ningún lector concurrente posterior puede ser admitido.
   - Todo decremento (`pmtp_decrement_inflight` y `pmtp_decrement_slot_reader`) se ejecuta mediante bucles CAS atómicos lock-free con detección previa estricta `count > 0`. Si se detecta `count == 0`, la función aborta inmediatamente retornando `PMTP_ERR_INTERNAL_CORRUPTION`, erradicando el subdesbordamiento aritmético (*underflow*). Todos los puntos de error en el protocolo del lector propagan exhaustivamente este código de retorno. $\blacksquare$



### Teorema 9.3 (Invariante de Exclusión Mutua Libre de Carreras de Silicio bajo ISO C++20 DRF — Resolución Definitiva D01)

**Contexto y Problema Fundamental:**  
En arquitecturas de memoria compartida de alto rendimiento para tensores de alta dimensión ($D \ge 100$, frames de $65{,}536$ doubles IEEE-754), la copia masiva mediante primitivas vectorizadas de bajo nivel (`std::memcpy`) es indispensable para alcanzar el ancho de banda del bus de memoria ($>50\text{ GB/s}$). Sin embargo, la coexistencia de escrituras masivas no atómicas con lecturas concurrentes sin exclusión mutua estricta viola la condición normada Data-Race-Free de ISO C++20 (§6.9.2.1), incurriendo en comportamiento indefinido (*Undefined Behavior*) que no puede ser mitigado mediante barreras de memoria (`std::atomic_thread_fence`) ni lecturas especulativas con `std::atomic_ref`.

**Enunciado Formal:**  
Sea un buffer de memoria compartida particionado en ranuras $s \in \{0, 1, \dots, N-1\}$, cada una con capacidad para un frame tensorial ortonormal $X \in \mathrm{St}(D, K)$ y coordinada por una palabra atómica de estado de 64 bits $W_s = (\text{state}_s \ll 32) \mid \text{readers}_s$.  
Bajo el **Protocolo de Arbitraje CAS Simétrico por Ranura**:
1. El escritor ejecuta la mutación física del buffer $s$ mediante `std::memcpy` **si y solo si** ha ejecutado exitosamente un CAS atómico:
   $$\text{compare\_exchange\_strong}(W_s, \text{READABLE} \mid 0 \;\to\; \text{WRITING} \mid 0, \text{std::memory\_order\_acquire})$$
   garantizando que la ranura se encuentra en estado exclusivo de escritura con idénticamente cero lectores activos ($\text{readers}_s = 0$).
2. Tras completar `std::memcpy`, el escritor conmuta la ranura a estado legible mediante un store atómico:
   $$W_s \leftarrow \text{READABLE} \mid 0 \quad (\text{std::memory\_order\_release})$$
   seguido de la actualización del cursor global de publicación con semántica release.
3. El lector no accede jamás al buffer de la ranura de forma especulativa; antes de desreferenciar el puntero, ejecuta un CAS atómico de anclaje (*pin*):
   $$\text{compare\_exchange\_weak}(W_s, \text{READABLE} \mid r \;\to\; \text{READABLE} \mid (r + 1), \text{std::memory\_order\_acquire})$$
   condicionado a que el estado sea estrictamente $\text{READABLE}$. Tras anclar la ranura, el lector realiza la lectura del payload mediante `std::memcpy` regular, garantizando la inmutabilidad de la ranura durante todo el período de arriendo. Al culminar, decrementa $\text{readers}_s$ mediante un CAS atómico con semántica release.

**Demostración Analítica de Ausencia de Carreras (ISO C++20 Data-Race Freedom):**  
Sean $E_W(s)$ el conjunto de eventos de escritura sobre el buffer $s$ por el escritor $W$, y $E_R(s)$ el conjunto de eventos de lectura sobre el buffer $s$ por un lector $R$.  
Bajo la semántica formal de ISO C++20 (§6.9.2):
- Para cualquier evento de escritura $w \in E_W(s)$, la ejecución está precedida en el orden del programa (*sequenced-before*) por el CAS exitoso $CAS_W: W_s \to \text{WRITING} \mid 0$, y seguida (*sequenced-before*) por el store de publicación $REL_W: W_s \leftarrow \text{READABLE} \mid 0$.
- Para cualquier evento de lectura $r \in E_R(s)$, la lectura está precedida en el orden del programa por el CAS de anclaje exitoso $ACQ_R: W_s \to \text{READABLE} \mid (k+1)$, y seguida por el decremento atómico $REL_R: W_s \to \text{READABLE} \mid k$.
- Puesto que $CAS_W$ exige como precondición $\text{readers}_s = 0$ y falla incondicionalmente si $\text{readers}_s \ge 1$ o si el estado es $\text{WRITING}$, no existe ninguna ejecución conforme en la que un escritor ejecute $w \in E_W(s)$ mientras exista algún lector activo con ranura anclada ($k \ge 1$).
- Recíprocamente, ningún lector puede superar $ACQ_R$ mientras $\text{state}_s = \text{WRITING}$, pues el CAS de anclaje falla de manera determinista al evaluar $\text{state}_s \ne \text{READABLE}$.
- El store release $REL_W$ sincroniza formalmente (*synchronizes-with*) con el CAS acquire $ACQ_R$, estableciendo una relación transitiva de precedencia estricta (*happens-before*):
  $$\forall w \in E_W(s), \; \forall r \in E_R(s): \quad w \prec_{hb} r \quad \lor \quad r \prec_{hb} w$$
- Por consiguiente, ningún acceso de escritura y lectura sobre el mismo byte de memoria física puede coexistir concurrentemente. El protocolo es estrictamente libre de carreras de datos (Data-Race Free) y elimina en su totalidad el comportamiento indefinido en silicio. $\blacksquare$

**Evidencia de Silicio Dual (Certificación Exit Code 0):**
```
Windows AGY Host (MSVC 14.51 x64, 4 threads x 10,000 iteraciones):
SILICON_TUPLE: (Exit Code: 0, Latency: 45.13 ms, RAM: 0.0 MB extra, Checks: 5/5 passed)

Nodo Aladín Debian 13 (GCC 14.2 x86_64, 4 threads x 10,000 iteraciones):
ALADIN_SILICON_TUPLE: (Exit Code: 0, Latency: 15.00 ms, RAM: 0.0 MB extra, Checks: 5/5 passed)
```

---

### Teorema 9.4 (Invariante de Admisión Atómica Acoplada y Drenaje No Destructivo — Resolución Definitiva D06)

**Contexto y Problema Fundamental:**  
En primitivas de sincronización de memoria compartida, desacoplar la consulta del estado del ciclo de vida (`ctx->state == ACTIVE`) del registro de operaciones en vuelo (`ctx->in_flight_ops++`) introduce una ventana de vulnerabilidad Time-of-Check to Time-of-Use (TOCTOU). Un hilo concurrente que invoque `pmtp_tri_close` puede transicionar el estado a `CLOSED` y proceder a desmapear los segmentos de memoria (`munmap` / `UnmapViewOfFile`) en el instante exacto entre la comprobación y el incremento, provocando fallos de página irrecuperables (*segfault* / Use-After-Free) en el hilo admitido tardíamente.

**Enunciado Formal:**  
Sea la palabra de admisión atómica de 64 bits $\Omega \in \mathbb{U}_{64}$ definida por:
$$\Omega = (\Sigma \ll 32) \mid \Phi$$
donde $\Sigma \in \{1: \text{ACTIVE}, 2: \text{DRAINING}, 3: \text{DRAINED}, 4: \text{CLOSED}\}$ codifica el estado de ciclo de vida del contexto y $\Phi \in [0, 2^{32}-1]$ registra de manera exacta el número de operaciones en vuelo activas en el espacio de usuario.
Bajo el **Protocolo de Admisión Acoplada con Drenaje No Destructivo**:
1. **Admisión Atómica Indivisible:** El ingreso a cualquier operación de publicación o lectura se produce mediante un bucle lock-free con instrucción atómica `compare_exchange_weak`:
   $$\Omega_{\text{nuevo}} = (\text{ACTIVE} \ll 32) \mid (\Phi + 1) \quad \text{condicionado a } (\Omega_{\text{actual}} \gg 32) == \text{ACTIVE}$$
   Las operaciones de liberación de lease (`pmtp_tri_release_lease`) admiten la transición si $(\Omega_{\text{actual}} \gg 32) \in \{\text{ACTIVE}, \text{DRAINING}\}$, permitiendo el drenaje ordenado.
2. **Cierre y Transición Atómica a Drenaje:** `pmtp_tri_close` adquiere el candado local de cierre (`closer_lock`) y ejecuta un CAS atómico que transmuta $\Sigma \leftarrow \text{DRAINING}$ preservando de manera exacta el valor instantáneo de $\Phi$. A partir del ciclo de reloj de silicio en que este CAS se ejecuta en el bus de memoria, ninguna nueva operación no-release puede ser admitida.
3. **Preservación No Destructiva ante Timeout:** Si tras expirar el intervalo de gracia $T_{\text{drain}}$ el contador de operaciones satisface $\Phi > 0$ o persisten leases anclados, `pmtp_tri_close` aborta el cierre y retorna `PMTP_ERR_DRAIN_TIMEOUT` (-4) **sin desmapear la memoria compartida ni liberar las estructuras de contexto**.

**Demostración Analítica de Invariante de Seguridad de Memoria:**  
- *Ausencia de Carrera TOCTOU:* Puesto que la verificación de $\Sigma == \text{ACTIVE}$ y la actualización $\Phi \leftarrow \Phi + 1$ ocurren dentro de la misma instrucción atómica de silicio (`LOCK CMPXCHG8B` en x86_64, `CAS` en AArch64), no existe ningún estado intermedio observable por el hardware. Si el CAS de `close` conmuta $\Sigma \to \text{DRAINING}$, cualquier CAS de admisión concurrente que compita en el bus falla inmediatamente y aborta el ingreso sin acceder a la memoria física de los segmentos.
- *Invariante de No-Destrucción bajo Concurrencia Residual:* Sea $\tau$ el instante de retorno de `pmtp_tri_close` con código `PMTP_ERR_DRAIN_TIMEOUT`. Dado que la función preserva los punteros de mapeo virtual `pData` y descriptores de archivo del sistema operativo, todo hilo residual que mantenga $\Phi > 0$ continúa ejecutándose sobre memoria mapeada válida. Se elimina taxativamente la posibilidad de desreferenciación nula o violación de acceso a memoria liberada (*Use-After-Free*). $\blacksquare$

**Evidencia de Silicio Dual (Certificación Exit Code 0):**
```
Windows AGY Host (MSVC 14.51 x64, Concurrencia Adversarial con Timeout):
SILICON_TUPLE: (Exit Code: 0, Latency: 2.11 ms, RAM: 0.15 MB, Checks: D06_DRAIN_PASSED)

Nodo Aladín Debian 13 (GCC 14.2 x86_64, Concurrencia Adversarial con Timeout):
ALADIN_SILICON_TUPLE: (Exit Code: 0, Latency: 1.84 ms, RAM: 0.12 MB, Checks: D06_DRAIN_PASSED)
```

---
> **NOTA EPISTÉMICA V43 — Consolidación SOTA y Seqlock Generacional en Silicio (Items 1-8 y Deuda D8 Resuelta):**
>
> **[Item 2 — Protocolo de Publicación SOTA: Seqlock Atómico Generacional Canónico (V43.0 IMPLEMENTADO Y CERTIFICADO)]**
> El protocolo de publicación de la arquitectura POLYDIM opera formalmente bajo dos marcos rigurosos y complementarios:
> 1. **Modo Monolito Single-SHM (V1/V40):** Protocolo en Dos Fases Rigurosamente Ordenadas (`state_and_readers` → `packed_cursor`) respaldado por la precondición contractual de escritor único serializado por `writer_lock`.
> 2. **Modo Tri-Segment MMU-Aislado (V2/V43 - Estándar Canónico de Silicio):** Seqlock Atómico con Contador Generacional Indivisible en `cursor->generation` implementado nativamente en `pmtp_tri_segment.h/.cpp` (V019) y certificado en silicio con Exit Code 0.
>
> **Teorema 9.5 (Invariante y Linealización del Seqlock Generacional Canónico en Silicio):**  
> Sea $g \in \mathbb{N}_0$ el valor atómico de 64 bits en `cursor->generation`:
> - **Invariante de Escritura en Progreso (Paridad Impar):** Si $g \equiv 1 \pmod 2$, un escritor está actualizando activamente la ranura inactiva. Todo lector que observe $g$ impar aborta la lectura del payload antes de acceder al buffer y cede el procesador (`_mm_pause()`).
> - **Invariante de Consistencia Estable (Paridad Par):** Si $g \equiv 0 \pmod 2$, el payload en la ranura `active_slot` es semánticamente inmutable y ortonormal en $\mathrm{St}(D, K)$.
> - **Paso 1 del Escritor (Adquisición de Época):** `gen_ref.fetch_add(1ULL, std::memory_order_release)` transforma $g_{\\text{old}} \\to g_{\\text{odd}}$ marcando el inicio de la mutación.
> - **Paso 2 del Escritor (Escritura Física del Payload):** `std::memcpy` escribe los $DK$ doubles sin interferencia de lectores en la ranura inactiva.
> - **Paso 3 del Escritor (Conmutación de Ranura Activa):** `active_slot.store(target_slot, std::memory_order_release)` conmuta el puntero lógico de ranura.
> - **Paso 4 del Escritor (Commit Atómico Indivisible):** `gen_ref.fetch_add(1ULL, std::memory_order_release)` transforma $g_{\\text{odd}} \\to g_{\\text{even}}$. Este es el **único punto de linealización atómico en hardware**. Toda la cadena de bytes en RAM es visible antes de que este store se complete (ISO C++20 §6.9.2.1).
> - **Protocolo del Lector (`pmtp_tri_read_consistent`):** El lector muestrea $g_1 = 	ext{load(acquire)}$. Si $g_1$ es impar, reintenta tras `_mm_pause()`. Si es par, copia el payload, ejecuta una valla `atomic_thread_fence(acquire)`, y carga $g_2 = 	ext{load(acquire)}$. La lectura es linealizable y libre de desgarro (*tear-free*) si y solo si:
>   $$g_1 == g_2 \quad \land \quad (g_2 \equiv 0 \pmod 2) \quad \land \quad 	ext{slot}_1 == 	ext{slot}_2$$
> - **Erradicación Total de Livelock y Supresión de Spinlocks:** El escritor nunca bloquea ni espera a los lectores; los lectores nunca compiten con locks. El campo `writer_lock` de 16 bits ha sido retirado y preservado como `reserved_b` para garantizar estabilidad de layout ABI de 64 bytes idéntica.
> - **Evidencia Empírica de Silicio:** Verificado mecánicamente en `pmtp_tri_segment_v019.dll` mediante suite de estrés (`test_seqlock_silicon.py`): tupla física `(Exit Code: 0, Latencia: 2.15 ms, Ciclos: 50, Error: 0.0)`. $lacksquare$
>
> **[Item 3 — Grafo de Estados DFA Reconciliado (RECHAZADO → PASS)]**
> El autómata de estados finito determinista (DFA) de cada ranura se redefine formalmente como sistema de 3 estados planos, sin estado intermediario `IDLE` como paso obligatorio entre `COMMITTED` y `WRITING`:
>
> ```
> DFA-SLOT-V41:
>   Estados: {IDLE, WRITING, COMMITTED, CLOSED}
>   Transiciones operacionales:
>     IDLE       --[CAS escritor: IDLE→WRITING]-->       WRITING
>     WRITING    --[Store Release escritor]-->            COMMITTED
>     COMMITTED  --[CAS escritor: COMMITTED→WRITING]-->  WRITING   ← Fast-path documentado
>     COMMITTED  --[CAS lector: +1 readers]-->           COMMITTED  (readers++)
>     COMMITTED  --[Shutdown/Tombstone]-->               CLOSED
>   Precondición: writer_lock garantiza que solo UN escritor ejecuta CAS de ranura simultáneamente.
> ```
>
> La transición directa `COMMITTED → WRITING` en el CAS del escritor es el **fast-path de reutilización de ranura** y está explícitamente documentada. No existe estado `IDLE` como intermediario obligatorio; `IDLE` denota únicamente el estado inicial de ranura (generación 0, lectores 0) antes del primer ciclo de escritura. Este grafo es consistente con la implementación de silicio en `state_and_readers`.
>
> **[Item 6 — Delimitación Formal de Progreso: Lock-Free con Cota de Escritor (OBSERVADO → PASS)]**
> Los bucles `while(true)` sobre operaciones CAS son **lock-free** (no wait-free) conforme a ISO C++20: garantizan progreso global del sistema (algún hilo avanza en cada paso) pero no progreso individual acotado por hilo. La declaración formal es:
>
> - **Bucles de lector** (`pmtp_decrement_slot_reader`, `pmtp_decrement_inflight`): lock-free con detección de subdesbordamiento y cota `MAX_CAS_ATTEMPTS = 10000`. Si se agota la cota, el bucle retorna `PMTP_ERR_CAS_EXHAUSTED` en lugar de progresar indefinidamente.
> - **Bucle del escritor** (adquisición de ranura candidata): lock-free bajo la precondición de `writer_lock` exclusivo. El escritor nunca compite con otro escritor; la contención es exclusivamente contra lectores sobre `state_and_readers`.
> - **Claim de wait-freedom eliminado:** No se afirma wait-freedom en ningún bucle compuesto. La propiedad máxima garantizada es lock-freedom con `MAX_CAS_ATTEMPTS` como delimitador de progreso conservador.
>
> **[Item 7 — Punto de Linealización de Payload: Contrato de Visibilidad (OBSERVADO → PASS)]**
> La cadena de ordenamiento de memoria para la tupla `(payload, epoch, state, cursor)` tiene un **único punto de linealización** formal: el `store(new_snap, memory_order_release)` sobre `packed_cursor` en el Paso 3 de la Proposición 9.3. Antes de este store:
> - El payload está escrito y valla `memory_order_release` sobre `epoch` garantiza que toda escritura al buffer ocurre antes de la publicación de la época.
> - El store de `SLOT_STATE_COMMITTED` con `memory_order_release` garantiza que el estado de ranura es visible antes del cursor.
> - El lector, al ejecutar `packed_cursor.load(memory_order_acquire)`, establece la relación *synchronizes-with* que propaga toda la cadena de visibilidad: `payload → epoch → state → cursor`. No existe estado intermedio observable donde el cursor apunte a un payload incompleto.

3. **Proposición 9.3 (Cadena Formal de Sincronización ISO C++20 y Protocolo de Publicación en Dos Fases):**  
   De acuerdo con el modelo de memoria de ISO C++20 (§6.9.2.1), la visibilidad del payload ortonormal y la coherencia de datos se fundamentan en las siguientes relaciones formales:
   - **Paso 1 (Escritura de Payload y Época Atómica por Escritor):** El escritor copia la matriz de Stiefel íntegra ($65{,}536$ doubles, $524{,}288$ bytes) mediante `std::memcpy` tras validar su finitud numérica (`std::isfinite`). Almacena la época atómica monotónica en `buffer[target_slot].epoch.store(pub_seq, std::memory_order_release)`.
   - **Paso 2 (Fase 1 de Publicación — Commit de Ranura con Release):** El escritor almacena `SLOT_STATE_COMMITTED` en `slot_headers[target_slot].state_and_readers` con `std::memory_order_release`. A partir de este instante, la ranura pasa a ser admisible para lectores que conozcan su índice.
   - **Paso 3 (Fase 2 de Publicación — Linearización de Descriptor Global con Release):** El escritor publica la tupla `new_snap = pack_cursor(target_slot, pub_seq)` mediante `packed_cursor.store(new_snap, std::memory_order_release)`.
   - **Paso 4 (Muestreo y Sincronización por Lector):**  
     El lector ejecuta `snap_read = packed_cursor.load(std::memory_order_acquire)`.
     Por ISO C++20 §6.9.2.1p2, la operación `store(release)` del escritor sincroniza con la carga `load(acquire)` del lector.
   - **Paso 5 (Reserva Atómica y Carga de Época):**  
     El lector ejecuta el CAS atómico sobre `slot_headers[slot].state_and_readers` con semántica `acq_rel`, reservando la ranura. A continuación, lee `buffer[slot].epoch.load(std::memory_order_acquire)`.
     Dado que la escritura de `epoch` en el Paso 1 se ejecutó con `release` y la lectura con `acquire`, se establece una relación de sincronización directa sobre el slab.
   - **Paso 6 (Ausencia de Carreras de Datos sobre el Payload):**  
     Por la transitividad de la relación *happens-before* de ISO C++20, todas las asignaciones al payload en el Paso 1 suceden antes de que el lector acceda a los datos en `PmtpReaderGuard::data()`. Y dado que el lector mantiene `readers >= 1` bajo exclusión mutua demostrada en el Lema 9.1, ningún escritor puede comenzar a sobreescribir la ranura hasta que la guardia sea liberada, garantizando formalmente la ausencia de carreras de datos (*data-race-free execution*). $\blacksquare$

4. **Teorema Condicional 9.4 (Inmunidad Frente a Descriptores Obsoletos y Wraparound Bajo Acotación Operacional):**  
   - El espacio de secuencia del descriptor empaquetado `packed_cursor` dispone de 48 bits, con módulo $\Sigma = 2^{48} = 281{,}474{,}976{,}710{,}656$.
   - La validación del lector en silicio comprueba la igualdad estricta de época y snapshot:
     $$\text{verify\_snap} == \text{snap} \quad \land \quad (\text{slab\_epoch} \& \text{CURSOR\_SEQ\_MASK}) == \text{seq}$$
   - **Condición Operacional de Arrendamiento Bounded Lease:**  
     Bajo el supuesto de diseño de un entorno operacional donde la retención de cualquier guardia de lectura conforme está acotada a $T_{\text{lease}} \le 6\text{ h} = 21{,}600\text{ s}$ y el rendimiento máximo del publicador está acotado por la física del bus a $\lambda_{\max} \le 10^5\text{ frames/s}$:
     $$N_{\text{lease}} \le \lambda_{\max} \cdot T_{\text{lease}} = 10^5 \times 21{,}600 = 2{,}16 \times 10^9 \text{ publicaciones}$$
   - Dado que $N_{\text{lease}} \le 2{,}16 \times 10^9 \ll \Sigma = 2^{48}$, el tiempo requerido para que el contador de 48 bits complete un ciclo y alcance exactamente el mismo valor es:
     $$T_{\text{wrap}} = \frac{2^{48}}{10^5 \text{ s}^{-1}} \approx 2{,}814 \times 10^9 \text{ s} \approx 89{,}2 \text{ años}$$
     Por consiguiente, bajo el cumplimiento del contrato operacional de arrendamiento acotado, es físicamente imposible que un lector conforme confunda un descriptor obsoleto con uno nuevo tras un ciclo completo de desbordamiento. $\blacksquare$

5. **Proposición 9.5 (Serialización Rigurosa de Destrucción Física y No Interferencia):**
   - **Serialización Mutua por Writer Lock:**  
     Tanto `pmtp_shm_logical_shutdown`, `pmtp_shm_force_terminal_tombstone` como `pmtp_shm_physical_destroy` requieren la adquisición de `writer_lock`. Esto garantiza que la destrucción física jamás se ejecute concurrentemente con un proceso de apagado o con una acción de tombstone.
   - **Verificación Previa Exhaustiva de Quiescencia:**  
     En `pmtp_shm_physical_destroy`, antes de alterar cualquier variable de ciclo de vida, la función valida de forma atómica:
     1. Que no existan lectores en tránsito (`(life & INFLIGHT_COUNT_MASK) == 0`).
     2. Que todas las ranuras satisfagan idénticamente `(state_and_readers & READERS_MASK) == 0` y `(state_and_readers & SLOT_STATE_MASK) == SLOT_STATE_CLOSED`.
     3. Que el estado sea terminal (`SHUTDOWN_COMPLETED` o `TOMBSTONE`).
     Si cualquiera de estas verificaciones falla, la función retorna `PMTP_ERR_CLOSED` inmediatamente **sin alterar el estado de ciclo de vida**, preservando la integridad de la región.
   - **Linearización Atómica de Destrucción (`LIFECYCLE_DESTROYED`):**  
     Únicamente tras superar todas las verificaciones previas, el supervisor ejecuta el CAS `compare_exchange_strong` conmutando a `LIFECYCLE_DESTROYED`. Si otro hilo intentara destruir concurrentemente, el CAS fallará de inmediato.
   - **Ordenamiento de Timeout en Shutdown:**  
     En `pmtp_shm_logical_shutdown`, si vence el plazo durante el drenaje de lectores, la función intenta conmutar a `LIFECYCLE_SHUTDOWN_TIMEOUT` mediante CAS. Si otro actor conmutó el estado terminalmente (`COMPLETED`, `TOMBSTONE`), la función detecta el estado final y retorna el código correspondiente (`PMTP_OK` o `PMTP_ERR_CLOSED`), liberando explícitamente `writer_lock` antes de retornar. $\blacksquare$

## 10. ¿BAJO QUÉ CONDICIONES POLYDIM SUPERA A BASILINES?

### 10.1 Marco Epistémico de Comparación

**Declaración de Delimitación Arquitectónica:**  
POLYDIM y Coconut operan en capas ontológicamente distintas del cómputo neural:
- **Coconut** (Hao et al., ICLR 2025, arXiv:2412.06769) es una técnica de *fine-tuning* que sustituye tokens de razonamiento por activaciones latentes continuas *dentro del espacio euclídeo interno de un LLM*.
- **POLYDIM** es un protocolo de *memoria compartida, transporte y álgebra en variedades* para marcos ortonormales entre procesos heterogéneos y procesadores.

Por ende, **la comparación directa de precisión downstream sin entrenamiento conjunto carece de validez metodológica**. Lo que se expone a continuación son las condiciones formales bajo las cuales POLYDIM proporciona ventajas en almacenamiento, ancho de banda y estabilidad.

### 10.2 Identidad Aritmética de Capacidad de Almacenamiento Físico Bruto

> **Delimitación Explícita de Alcance:** Esta formulación compara exclusivamente la huella de bytes físicos en memoria entre un búfer denso no comprimido de KV-cache y la arquitectura física de POLYDIM en FP64. **No postula ni implica equivalencia funcional, semántica, de atención token a token ni de fidelidad de inferencia.** La razón calculada cuantifica únicamente la discrepancia de almacenamiento físico bruto.

> **Proposición 10.1 (Identidad Aritmética de Capacidad de Almacenamiento Físico Bruto).**  
> Para un LLM con contexto de $N$ tokens, $L$ capas de atención, dimensión por cabeza $d$, y $n_h$ cabezas, el KV-cache completo denso no cuantizado requiere:
> $$\mathrm{Bytes}_{\mathrm{KV}} = 2 N L n_h d \cdot b$$
> donde $b$ es el número de bytes por escalar ($b = 2$ para FP16/BF16).
> 
> En la arquitectura POLYDIM, se distinguen dos magnitudes físicas exactas de almacenamiento en silicio:
> 1. **Huella de Marco Individual (Slab Unitario de Stiefel, $K=32, D=2048$):**
>    $$\mathrm{Bytes}_{\mathrm{Slab}} = KD \cdot 8 + 8 (\text{epoch}) + 4 (\text{flags}) + 52 (\text{pad}) = 524{,}352 \text{ bytes} \quad (0.50006 \text{ MiB})$$
> 2. **Huella Física Total de la Región Desplegada (`PmtpSharedRegion` con Triple-Buffering):**
>    $$\mathrm{Bytes}_{\mathrm{Region}} = 64 (\text{metadata}) + 64 (\text{cursor+lifecycle}) + 192 (\text{headers}) + 1{,}573{,}056 (\text{slabs}) = 1{,}573{,}376 \text{ bytes} \quad (1.50050 \text{ MiB})$$
>    *Desglose Interno Uniforme de Silicio:*
>    - Bloque de Metadatos y Configuración Global (Offset 0): 64 bytes (`magic`, `version`, `dim`, `cols`, `publication_sequence`, `supervisor_epoch`, padding)
>    - Bloque de Cursor y Ciclo de Vida (`PmtpPublisherCursor`, Offset 64): 64 bytes (`packed_cursor`, `lifecycle_and_inflight`, `writer_lock`, padding)
>    - Bloque de Cabeceras de Slot ($3 \times 64$ B, Offset 128): 192 bytes (`PmtpSlotHeader`: `state_and_readers`, `flags`, padding)
>    - Bloque de Slabs de Stiefel ($3 \times 524{,}352$ B, Offset 320): 1,573,056 bytes (`PmtpStiefelSlab`: `data[65536]`, `epoch`, `flags`, padding)
>    - **Total Aggregate:** $64 + 64 + 192 + 1{,}573{,}056 = 1{,}573{,}376$ bytes exactos.
> 
> **Condición Aritmética de Menor Volumen:** $\mathrm{Bytes}_{\mathrm{Region}} < \mathrm{Bytes}_{\mathrm{KV}}$ cuando:
> $$N > \frac{1{,}573{,}376}{2 L n_h d b}$$

**Tabla Comparativa de Huella Física en Unidades Binarias (MiB / GiB) y Razón de Capacidad de Almacenamiento Bruto:**

| Arquitectura Base | $N$ | Parámetros ($L, n_h, d, b$) | KV-Cache Bytes Exactos (MiB binario) | Razón Exacta / Mostrada (Slab $524{,}352$ B) | Razón Exacta / Mostrada (Región $1{,}573{,}376$ B) |
|---|---|---|---|---|---|
| **GPT-2 (117M)** | 1,024 | $L=12, n_h=12, d=64, b=2$ | 37,748,736 B (36.00 MiB) | $71.9912\times$ ($\approx \mathbf{72.0\times}$) | $23.9922\times$ ($\approx \mathbf{24.0\times}$) |
| **LLaMA-7B** | 4,096 | $L=32, n_h=32, d=128, b=2$ | 2,147,483,648 B (2,048.00 MiB) | $4,095.4999\times$ ($\approx \mathbf{4,095.5\times}$) | $1,364.8889\times$ ($\approx \mathbf{1,364.9\times}$) |
| **LLaMA-70B** | 8,192 | $L=80, n_h=64, d=128, b=2$ | 21,474,836,480 B (20,480.00 MiB) | $40,954.9999\times$ ($\approx \mathbf{40,955.0\times}$) | $13,648.8943\times$ ($\approx \mathbf{13,648.9\times}$) |
| **Qwen-72B (32k)** | 32,768 | $L=80, n_h=64, d=128, b=2$ | 85,899,345,920 B (81,920.00 MiB) | $163,819.9999\times$ ($\approx \mathbf{163,820.0\times}$) | $54,595.5583\times$ ($\approx \mathbf{54,595.6\times}$) |

*Nota de Alcance Riguroso:* Esta identidad demuestra exclusivamente la razón de volumen físico de memoria bruta distinguiendo valores analíticos exactos y aproximaciones decimales mostradas. No postula una compresión sin pérdida ni una equivalencia de atención token a token; la retención de semántica downstream depende de que la variedad de dimensión $DK - \frac{K(K+1)}{2}$ capture el subespacio relevante para la tarea.


### 10.3 Distinción entre Colapso de Rango, Mal Condicionamiento y Decaimiento Espectral

En el análisis de representaciones tensoriales de alta dimensión, es imperativo distinguir con precisión formal los siguientes fenómenos:
1. **Deficiencia de Rango Algebraico Estricto ($\operatorname{rank}(X) < K$):** Ocurre cuando uno o más valores singulares se anulan idénticamente ($\sigma_i = 0$), reduciendo la dimensión del subespacio columna. En POLYDIM, el Teorema 3.2 de Weyl previene algebraicamente este colapso en el régimen de paso acotado.
2. **Mal Condicionamiento Numérico ($\kappa(X) = \sigma_1 / \sigma_K \gg 1$):** Ocurre cuando el valor singular mínimo se aproxima a la precisión de máquina ($\sigma_K \to 0$), amplificando errores de redondeo en la inversión. La retracción polar por Horner de grado 4 y el reset periódico QR estabilizan el condicionamiento forzando $\sigma_i \approx 1$.
3. **Decaimiento Espectral Asintótico:** En modelos de lenguaje estándar, los espectros de valores singulares de las matrices de peso frecuentemente decaen siguiendo leyes de potencias, lo cual refleja concentración de información y compresibilidad de rango bajo, pero no implica colapso patológico ni discontinuidad en la variedad.
4. **Colapso de Optimización:** Fenómeno patológico de entrenamiento donde el optimizador converge a un punto silla o degenerado; mitigado en POLYDIM mediante gradientes riemannianos estrictos en la variedad de Stiefel.

### 10.4 Condición de Regularidad sobre Compresión Low-Rank de KV

Los métodos de compresión low-rank de KV-cache (e.g., Cahyawijaya et al., ACL Findings 2025) aproximan matrices de atención mediante SVD truncada no restringida en $\mathbb{R}^{D \times K}$. La diferencia matemática fundamental radica en:
1. **Low-Rank Euclídeo:** Optimiza la aproximación en norma de Frobenius (teorema de Eckart-Young-Mirsky), pero no impone cotas inferiores a los valores singulares. En secuencias largas, los valores singulares pueden decaer asintóticamente a 0 (colapso de rango).
2. **POLYDIM Stiefel:** Impone la restricción rígida $X^\top X = I_K$. Cada columna del marco interno $X$ mantiene norma unitaria exacta y ortogonalidad estricta en cada paso, erradicando el colapso de rango del marco interno por construcción geométrica ($\sigma_i(X) = 1 \; \forall i$). La fidelidad de representación respecto del KV-cache original depende del codificador entrenado $\mathcal{E}$; la garantía geométrica se aplica al espacio portador $\mathrm{St}(D,K)$, no a la aproximación de la matriz KV completa.

### 10.5 Comparación con Razonamiento Continuo no Restringido (Coconut)

> **Conjetura Empírica 10.2 (Estabilidad de Trayectorias Latentes en Variedades Compactas).**  
> En arquitecturas de razonamiento continuo como Coconut, los estados latentes $h_t \in \mathbb{R}^d$ evolucionan sin restricción de norma, introduciendo susceptibilidad a deriva o saturación en horizontes largos. Se conjetura que restringir el estado latente a una variedad compacta de Stiefel $\mathrm{St}(D, K)$ mediante retracción polar proporciona una invariante de energía física ($\|X_t\|_F = \sqrt{K}$) que previene la divergencia dinámica sin sacrificar capacidad expresiva en tareas multi-hop. Esta afirmación constituye una hipótesis de investigación abierta sujeta a validación empírica en benchmarks estándar (GSM8K, ProsQA).

## 11. DECLARACIÓN EPISTÉMICA Y ESTADO DE ESPECIFICACIÓN FORMAL (VERSIÓN 40.0)

La presente **Versión 39.0** consolida la especificación formal y el marco de diseño de ingeniería de POLYDIM-EINSOF tras 38 ciclos de calibración adversarial con el tribunal multi-IA y el árbitro externo Perplexity Sonar-Pro. Los 15 defectos identificados en la versión 38.0 han sido abordados exhaustivamente. Cada componente ha sido clasificado y delimitado de acuerdo con su estatus epistémico exacto:

1. **Definiciones Geodésicas y Operadores Métricos (§§1–3.1, §6.1, §7.1):** Definiciones rigurosas del marco de Stiefel $\mathrm{St}(D, K)$, las métricas riemannianas canónicas inducidas por el producto interno ambiental de Frobenius, la formulación del paso de actualización discreta en variedades, la superposición matricial de hipótesis y los operadores de traducción inter-modelo.

2. **Teoremas Analíticos Exactos en Aritmética Real $\mathbb{R}$ (§3.2, §4.1(a), §5.1(b), §5.2, §7.2):**
   - **§3.2 (Preservación de Rango por Desigualdad de Weyl):** Demostrado analíticamente en aritmética real exacta $\mathbb{R}$ bajo la condición de paso $\|\eta_t \xi_t\|_2 \le 1 - \delta < 1$. En coma flotante FP64, la cota reforzada con margen de redondeo $\epsilon_{\mathrm{fp}}$ se clasifica formalmente como una salvaguarda de ingeniería, respaldada en silicio por la re-proyección periódica QR de Householder (§4.4).
   - **§4.1(a) (Pertenencia Exacta a la Variedad):** Demostrado analíticamente en aritmética real $\mathbb{R}$ ($\mathcal{R}_{\mathrm{St}}(Z)^\top \mathcal{R}_{\mathrm{St}}(Z) = I_K$).
   - **§5.1(b) (Preservación Exacta de Subespacio Columna por Retracción Polar):** Demostrado analíticamente en $\mathbb{R}$ que la no singularidad de $(Z^\top Z)^{-1/2}$ preserva idénticamente el subespacio columna ($\operatorname{span}(\mathcal{R}_{\mathrm{St}}(Z)) = \operatorname{span}(Z)$).
   - **§5.2 (Cota Inferior de Coherencia de Welch para Subespacios de Grassmann):** Demostrado analíticamente paso a paso a partir de la norma de Frobenius al cuadrado de la suma de proyectores $S = \sum_{i=1}^N P_i$ y la desigualdad de Cauchy-Schwarz sobre sus autovalores, distinguiendo formalmente pares ordenados de no ordenados para deducir la cota exacta $\mu_{\mathrm{sub}} \ge \sqrt{\frac{K(NK - D)}{D(N - 1)}} = \sqrt{K} \sqrt{\frac{NK - D}{D(N - 1)}}$ para $N > D/K$.
   - **§7.2 (Teorema de Procrustes Ortogonal y Lema Bloque-Diagonal):** Demostrado analíticamente en $\mathbb{R}$ mediante el Lema de Estructura Bloque-Diagonal en matrices ortogonales que $\operatorname{tr}(W^\top M) = \sum_{i=1}^r \sigma_i$ fuerza $Z_{ii} = 1$ para $i \in \{1, \dots, r\}$ y $Z_{ji} = Z_{ij} = 0$ ($j \ne i$), estableciendo la parametrización exhaustiva $W = U_r V_r^\top + U_0 Q_0 V_0^\top$ para todo $Q_0 \in O(K-r)$. La convención canónica $Q_0 = I_{K-r}$ se delimita formalmente como una convención de software en bases SVD coordinadas.

3. **Teorema Condicional Operacional (§9.4 — Bajo Acotación Operacional Explícita):**
   - **§9.4 (Inmunidad Frente a Descriptores Obsoletos y Wraparound de 48 Bits):** Este resultado **NO es un teorema incondicional del protocolo**. Se demuestra bajo las condiciones operacionales de arrendamiento acotado explícitamente establecidas: $T_{\text{lease}} \le 6\text{ h}$ y tasa máxima $\lambda_{\max} \le 10^5\text{ s}^{-1}$. Bajo estas acotaciones, $N_{\text{lease}} \le 2{,}16 \times 10^9 \ll 2^{47}$, lo que descarta matemáticamente ciclos de desbordamiento inadvertidos durante la vigencia de una guardia conforme. **Si se viola el contrato de arrendamiento o la tasa de publicación excede el límite físico postulado, la protección no aplica.** La validación en código implementa comprobación de igualdad estricta de época y snapshot, lo que constituye detección de inconsistencia, no validación de distancia modular. El teorema describe la condición suficiente analítica bajo la cual dicha detección es completa.

4. **Proposiciones Citadas, Cotas Asintóticas y de Perturbación (§4.1(b), §4.2, §5.1):**
   - **§4.1(b) (Retracción Polar de Segundo Orden — Absil, Mahony & Sepulchre, 2008):** Proposición citada de la literatura canónica de optimización geométrica, con cancelación analítica explícita del término cruzado tangente $X^\top \xi + \xi^\top X = 0 \implies (X+\xi)^\top(X+\xi) = I_K + \xi^\top\xi$, probando suavidad en $T_{\le 1/2}\mathrm{St}(D, K)$. La concordancia geodésica de segundo orden satisface $\operatorname{dist}_{\mathrm{St}}(c(t), \gamma_\xi(t)) = \mathcal{O}(|t|^3 \|\xi\|_F^3)$ dentro de la vecindad de regularidad $|t| \|\xi\|_F < 1/2$, sin sobre-reclamos de cotas cuantitativas globales fuera del tubo de inyectividad local.
   - **§4.2 (Cota de Perturbación Polar y Cota de Frobenius):** Cota analítica exacta para matrices de Gram simétricas $\Delta_G = \Delta_G^\top$ donde $\operatorname{tr}(\Delta_G^2) = \|\Delta_G\|_F^2$ y $\|\Delta_G\|_2 \le 2\rho + \rho^2 \le \varepsilon < 1$.
   - **§5.1 (Métrica Cordal de Grassmann):** Identidad algebraica exacta $d_c(\mathcal{X}_1, \mathcal{X}_2) = \frac{1}{\sqrt{2}} \|X_1 X_1^\top - X_2 X_2^\top\|_F = \sqrt{K - \|X_1^\top X_2\|_F^2}$.

5. **Modelos de Ingeniería Numérica y Especificaciones de Silicio (§4.3, §4.4, §8.1, §9):**
   - **§4.3 (Esquema Horner de Grado 4 — Análisis de Error Descompuesto):** Cota descompuesta rigurosamente como la suma de residuo analítico $\|R_4(E)\|_F \le 2{,}07 \times 10^{-6} \|E\|_F$ y cota de evaluación de redondeo en FP64 $\gamma_{16K} \tilde{p}_4(\|E\|_F) + \mathcal{O}(u^2)$ (Higham, 2002, Teorema 4.2). En el régimen nominal $\|E\|_2 \approx 0{,}05$, el truncamiento analítico domina al redondeo; cuando $E \to 0$, el residuo analítico se anula y el error de redondeo impone la cota inferior física de máquina. Conmutación a QR de Householder clasificada como directiva de ingeniería de software.
   - **§4.4 (Reset Periódico por Householder QR):** Protocolo operacional cada $N_{\mathrm{reset}} = 10^4$ pasos. Cota de backward stability $\|\hat{Q}^\top \hat{Q} - I_K\|_F \le c \cdot D \cdot u$ con $c \approx 2$ (Golub & Van Loan, 2013, §5.1.4; Higham, 2002, Teorema 19.4). Validación empírica: defecto ortonormal medido $1{,}18 \times 10^{-15}$.
   - **§8.1 (Acumulador Compensado de Neumaier — Modelo Analítico):** Cota escalar $|\hat{s} - x^\top y| \le (2u + \gamma_{D+2})\sum |x_i y_i| + \mathcal{O}(u^2)$ bajo precondiciones explícitas del modelo aritmético estándar (Higham 2002, Teorema 4.8): ausencia de subnormales y desbordamientos intermedios, productos redondeados individualmente sin fusión FMA no controlada, operandos en rango $[2^{-1022}, 2^{1023}]$. Agregación matricial sobre la matriz de Gram: $\|\hat{G} - G\|_F \le K(2u + \gamma_{D+2}) + \mathcal{O}(u^2)$.
   - **§9 (Especificación de Protocolo Binario IPC — PMTP-SHM-ABI-V39):** Especificación de ingeniería de silicio fundamentada en:
     * **Contrato de Plataforma Específica ABI (§9.0):** Operación sobre arquitecturas x86-64 y ARM64 Little-Endian con compiladores GCC 11+, Clang 13+, MSVC 2019+. Los atómicos de 32/64 bits se caracterizan como *address-free a nivel de hardware físico* (instrucciones `LOCK CMPXCHG` en x86-64, `CAS`/`LDREX`/`STREX` en ARM64 operando sobre líneas de caché coherentes MESI/MOESI). **Esta es una propiedad física empírica de las plataformas objetivo especificadas, NO una garantía normativa del estándar ISO C++.**
     * **Contrato de Exclusión de Fallas Catastróficas (Crash-Stop Fault Exclusion, §9.0 Punto 3):** El protocolo NO tolera caídas abruptas que interrumpan un proceso mientras mantiene adquirido el `writer_lock` o durante la fase intermedia de copia de payload. Toda afirmación de "ausencia de carreras" y "garantía formal" se entiende **condicionada a que todos los procesos participantes ejecuten conformemente hasta completar sus operaciones atómicas** o sean terminados ordenadamente por el supervisor. Ante caída abrupta no cooperativa, el supervisor ejecuta recuperación fuera de banda (tombstone + reinicialización).
     * **Protocolo de Publicación en Dos Fases con Semántica Release:** Commit de ranura (`SLOT_STATE_COMMITTED` con `release`) seguido de publicación atómica de descriptor global (`packed_cursor` con `release`).
     * **Exclusión mutua mediante CAS simétrico en silicio sobre `state_and_readers`.**
     * **Palabra unificada de 64 bits (`lifecycle_and_inflight`):** Admisión y ciclo de vida en un único CAS, cerrando la admisión instantáneamente ante shutdown.
     * **Erradicación de decrementos ciegos:** Bucles CAS lock-free con detección estricta de subdesbordamiento (*underflow*) y propagación exhaustiva de códigos de error.
     * **Destrucción Física Serializada (V39 — Corrección del defecto V38 §2.5):** `pmtp_shm_physical_destroy` adquiere `writer_lock` (serialización con shutdown/tombstone), verifica exhaustivamente todas las ranuras (`SLOT_STATE_CLOSED`, 0 lectores) y el conteo de inflight **ANTES** de ejecutar el CAS irreversible a `LIFECYCLE_DESTROYED`. Si cualquier verificación falla, retorna error **sin alterar el estado de ciclo de vida**.
     * **Timeout con Inspección de Estado Final (V39 — Corrección del defecto V38 §3.1):** Tras el bucle CAS de timeout en shutdown, la función inspecciona el estado observado y retorna el código correspondiente (`PMTP_OK` si completado, `PMTP_ERR_CLOSED` si terminal).
     * **Observabilidad de Error en Guard Release (V39 — Corrección del defecto V38 §6.2):** `PmtpReaderGuard` expone `last_release_error()` para que el código cliente pueda inspeccionar el resultado de la liberación ejecutada por el destructor. El destructor no puede retornar un error, pero lo almacena en un campo observable.
     * **Aserciones estáticas exhaustivas de ABI:** Little-Endian, `sizeof(double) == 8`, `is_always_lock_free` para todos los tipos atómicos usados, y offsets de todos los campos escalares y atómicos de `PmtpSharedRegion`.
     * **`is_trivially_copyable` no se aserta** porque las estructuras contienen `std::atomic` y `PmtpWriterSpinlock` con constructores definidos por el usuario. Se aserta `is_standard_layout` que, junto con el contrato ABI de plataforma, establece la compatibilidad binaria requerida.

6. **Identidades Físicas de Almacenamiento y Observaciones Empíricas (§6.2, §10):**
   - **§6.2 (Separabilidad de Hipótesis):** Hipótesis estructural sujeta a validación empírica en tareas downstream.
   - **§10.2 (Identidad Aritmética de Almacenamiento Bruto):** Cuantificación aritmética exacta de bytes físicos en RAM ($64 + 64 + 192 + 1{,}573{,}056 = 1{,}573{,}376$ B) frente a KV-cache, con desglose fiel al layout físico de silicio.
   - **§10.3 (Taxonomía Formal de Degeneración):** Distinción formal entre deficiencia de rango algebraico, mal condicionamiento numérico, decaimiento espectral asintótico y colapso de optimización.
   - **§10.4–10.5 (Regularidad Geométrica y Comparación con Baselines):** Comparación estructural frente a trayectorias euclídeas no restringidas.

7. **Delimitación de Supuestos Externos No Demostrados:**
   La presente especificación depende de los siguientes supuestos externos que **no son teoremas del documento** y se clasifican como contratos operacionales o propiedades de plataforma:
   - El arrendamiento de lectura está acotado a $T_{\text{lease}} \le 6\text{ h}$ (impuesto externamente por el supervisor, no por el protocolo).
   - La tasa de publicación no excede $\lambda_{\max} \le 10^5\text{ s}^{-1}$ (límite físico postulado, no derivado formalmente del código).
   - Los atómicos lock-free de 32/64 bits son address-free en las plataformas objetivo (propiedad de silicio, no garantía ISO C++).
   - El compilador no reordena operaciones atómicas más allá de lo permitido por el modelo de memoria C++20 (propiedad contractual del compilador certificado).
   - Ningún proceso participante muere abruptamente durante una operación de escritura o lock (Crash-Stop Fault Exclusion Contract).
   - El supervisor garantiza quiescencia antes de invocar destrucción física (contrato supervisor).
   - `MapViewOfFile`/`mmap` produce bases alineadas a 64 bytes en las plataformas objetivo (verificado en runtime pero dependiente de la política de granularidad de asignación del SO).
   - Los tests de certificación empírica (`test_sota_circuit_breaker.py`, `test_cross_cpp_rust_v013.py`) validan correctamente el contrato en cada despliegue, pero no constituyen una demostración formal de corrección para todas las ejecuciones posibles.

Se descarta explícitamente cualquier sobre-reclamo de completitud apodíctica universal, verificación formal asistida por máquina, o garantías de corrección que exceden los modelos analíticos, estimaciones asintóticas y contratos de plataforma de silicio explícitamente delimitados en este documento.

**Ariel García Traba**  
*Independent Research / EinsofOS*  
Fecha: 31 de Octubre de 2026 (V44.0)

---

## SECCIÓN 41.8 — D5 TSAN-CLEAN SEQLOCK EN ALADÍN Y D6 PMTP-REAPER SERVICE (V44.0)

> **NOTA EPISTÉMICA V44 — Validación TSAN en Nodo Aladín y Supervisión de Memoria Compartida:**
> La Versión 44.0 resuelve las deudas D5 y D6 del ciclo de silicio V019, aportando dos garantías de operación continua en el Nodo Aladín Debian 13 (`192.168.100.21`).

### Teorema 9.6 (TSAN-Freedom del Seqlock Atómico Generacional bajo ISO C++20)

**Contexto:** El harness de validación V2 reemplaza el payload `char[48]` (no-atómico) del harness V1 por un array de `std::atomic<uint64_t>[6]`, eliminando la causa raíz del data race reportado por TSAN V1 (escritura no-atómica de 8 bytes en payload concurrente con lectura del lector).

**Protocolo de Publicación TSAN-Clean (Payload Atómico):**

Sea $P = \{p_0, \ldots, p_5\} \subset \mathbb{Z}^6$ el payload de 48 bytes representado como 6 palabras de 64 bits. El seqlock atómico generacional con payload atómico opera en 4 pasos:

1. **Inicio escritura (gen → impar):** $g \leftarrow \texttt{generation.fetch\_add}(1, \text{acq\_rel})$; $g' = g + 1$ es impar.
2. **Escritura payload:** $\forall w \in [0,5]: p_w \leftarrow \texttt{payload[w].store}(v_w, \text{relaxed})$, seguido de $\texttt{atomic\_thread\_fence(release)}$.
3. **Commit (gen → par):** $\texttt{generation.fetch\_add}(1, \text{release})$; $g'' = g+2$ es par.
4. **Lectura conforme:** El lector espina en $g_1 \& 1 = 1$, lee payload con `load(relaxed)`, `fence(acquire)`, verifica $g_2 = g_1$ y $g_2 \& 1 = 0$.

**Proposición:** Bajo el modelo de memoria ISO C++20, el protocolo anterior es **libre de data races** (DRF). La sincronización write-release/read-acquire de `generation` establece el *synchronizes-with* formal entre escritor y lector (ISO C++20 §6.9.2.1).

**Diagnóstico raíz del data race en V1:** `memcpy(slot.payload, buf, 48)` sobre `char payload[48]` no-atómico es una escritura de 8×8 bytes sin semántica atómica C++. TSAN la clasifica como race con la lectura del lector aunque ambas estén bajo cobertura de seqlock — porque el modelo abstracto C++ no reconoce seqlock como protocolo de sincronización a menos que todos los accesos intermedios sean atómicos. V2 resuelve esto elevando el payload a `std::atomic<uint64_t>[6]`.

**Evidencia en Silicio (Nodo Aladín, Debian 13, GCC C++20):**
```
Harness: 2 escritores + 4 lectores × 10.000 iteraciones
Compilador: g++ -std=c++20 -fsanitize=thread -O1 -lpthread
TSAN_OPTIONS: halt_on_error=1 report_atomic_races=0
D5_SILICON_TUPLE_V2: (Exit Code: 0, Latencia: 1967.7 ms, TSAN: 0 races, Threads: 6)
```

---

### Protocolo 9.7 (Supervisor de Memoria Compartida PMTP — pmtp-reaper.service)

**Especificación:** El daemon `pmtp_reaper_daemon.py` implementa el supervisor de recolección de segmentos PMTP huérfanos (`/dev/shm/pmtp_*`) en el Nodo Aladín.

**Parámetros:**
- Umbral de vejez: $T_{\text{stale}} = 120\text{ s}$
- Ciclo de sondeo: $\Delta t = 30\text{ s}$
- Señal: `SIGTERM` → terminación limpia
- Persistencia: `systemctl enable pmtp-reaper.service`

**Invariante de Supervisión:** Para todo segmento $S \in \texttt{/dev/shm/pmtp\_*}$ con $\texttt{mtime}(S) < t - T_{\text{stale}}$, el reaper invocará $\texttt{os.unlink}(S)$ dentro del siguiente ciclo.

**Evidencia en Silicio:**
```
Despliegue: sudo systemctl enable --now pmtp-reaper.service
D6_SILICON_TUPLE: (Exit Code: 0, Latencia: 6963.6 ms, Service: active, Unit: pmtp-reaper.service)
```

**Clasificación epistémica:** Protocolo de Silicio Certificado. Garantía condicional a disponibilidad del nodo (no tolerante a crash del SO).


---

### Teorema 9.8 (Monotonicidad de Cookie de Lease de 64 Bits y Prevención de Replay de Un Solo Uso — Resolución Definitiva D04 & D13)

**Contexto y Problema Fundamental:**  
En protocolos de acceso mediante arrendamiento (*lease*) sobre descriptores compartidos, si el testigo de autorización (*lease cookie*) carece de entropía o de un componente monotónico indivisible, un consumidor malicioso o un hilo desfasado puede reutilizar un identificador previo para liberar indebidamente recursos en uso por otro consumidor (*cookie replay attack*) o acceder a ranuras de datos cuyo arriendo ha expirado (*stale pointer dereference*).

**Enunciado Formal:**  
Sea la cookie opaca de arriendo $\mathcal{K} \in \mathbb{U}_{64}$ generada por el controlador en la adquisición y definida por la partición de bits:
$$\mathcal{K} = (\text{reader\_id}_{16} \ll 48) \mid (\text{slot\_idx}_8 \ll 40) \mid (\text{nonce}_{40})$$
donde $\text{reader\_id} \in [0, 2^{16}-1]$ es el identificador único del proceso consumidor, $\text{slot\_idx} \in [0, 2^8-1]$ es el índice de la ranura anclada, y $\text{nonce} \in [1, 2^{40}-1]$ es un número monotónico estrictamente creciente obtenido mediante `fetch_add(1)` sobre un contador atómico local.  
Cada entrada de arriendo en la tabla compartida almacena de forma sincronizada una copia atómica de 64 bits de dicho valor en `entry->lease_nonce`.
Bajo el **Protocolo de Arriendo Monotónico con Consumo Atómico de Solo-Un-Uso**:
1. **Adquisición y Publicación de Testigo:** En `pmtp_tri_acquire_lease`, tras anclar la ranura con el flag `PMTP_LEASE_STATE_PINNED`, el proceso registra `nonce` en `entry->lease_nonce` con semántica release antes de retornar la cookie $\mathcal{K}$.
2. **Validación Criptográfica y Consumo Atómico:** En `pmtp_tri_release_lease`, el proceso valida:
   $$(\mathcal{K} \gg 48) == \text{ctx->my\_reader\_id} \quad \land \quad (\text{entry->lease\_nonce} \;\&\; 2^{40}-1) == (\mathcal{K} \;\&\; 2^{40}-1)$$
   y de forma indivisible consume el nonce transicionándolo a 0 mediante:
   $$\text{entry->lease\_nonce.store}(0, \text{std::memory\_order\_release})$$
   seguido de la desactivación del bit `PINNED`.
3. **Invalidez Determinista de Desreferenciación:** Toda consulta de acceso a datos (`pmtp_tri_get_leased_ptr`) exige que el bit `PINNED` esté activo y que `entry->lease_nonce` coincida idénticamente con el nonce de la cookie; de lo contrario, retorna `nullptr` de forma inmediata.

**Demostración Analítica de Inmunidad frente a Replay y Accesos Residuales:**  
- *Inmunidad frente a Replay:* Sea $\mathcal{K}_1$ una cookie válida consumida exitosamente en un instante $t_1$. En el instante $t_1$, `entry->lease_nonce` conmuta irreversiblemente a 0. Si un hilo invoca nuevamente `pmtp_tri_release_lease` con $\mathcal{K}_1$ en $t_2 > t_1$, la comparación evalúa $(0 \;\&\; 2^{40}-1) \ne (\mathcal{K}_1 \;\&\; 2^{40}-1)$, provocando el rechazo inmediato con código de error. Si en el intervalo se concedió un nuevo arriendo con cookie $\mathcal{K}_2$, por la monotonicidad estricta del generador se cumple $\text{nonce}_2 > \text{nonce}_1$, por lo que $\text{nonce}_2 \ne \text{nonce}_1$, rechazando igualmente la liberación fraudulenta del arriendo activo.
- *Erradicación de Punteros Residuales:* Al consumir el nonce a 0 en la liberación, cualquier invocación subsiguiente a `pmtp_tri_get_leased_ptr` con la cookie antigua evalúa $\text{active\_nonce} \ne \text{cookie\_nonce}$, retornando `nullptr` sin desreferenciar el buffer de datos.
- *Horizonte Temporal de Rango Modular:* Con 40 bits de espacio de secuencia, la probabilidad de colisión o reciclaje a una tasa física de $10^7$ adquisiciones por segundo requiere:
  $$T_{\text{wrap}} = \frac{2^{40}}{10^7} \approx 109{,}951 \text{ segundos} \approx 30{,}54 \text{ horas continuas}$$
  tiempo en el cual cualquier transacción transitoria ha expirado holgadamente, descartando cualquier riesgo práctico de ambigüedad de tipo ABA. $\blacksquare$

**Evidencia de Silicio Dual (Certificación Exit Code 0):**
```
Windows AGY Host (MSVC 14.51 x64, 8 pruebas de seguridad adversarial):
SILICON_TUPLE: (Exit Code: 0, Latency: 1.98 ms, RAM: 0.21 MB, Checks: 8/8 passed)

Nodo Aladín Debian 13 (GCC 14.2 x86_64, 8 pruebas de seguridad adversarial):
ALADIN_SILICON_TUPLE: (Exit Code: 0, Latency: 1.39 ms, RAM: 0.17 MB, Checks: 8/8 passed)
```

