# GUÍA DE TRABAJO PRÁCTICO DE LABORATORIO
## AUDITORÍA DE SOFTWARE NUMÉRICO Y COMPUTACIÓN DE ALTO RENDIMIENTO (V26150)
**Nivel:** 1º Año — Ciencias de la Computación / Ingeniería en Sistemas  
**Cátedra:** Arquitectura de Computadoras & Programación de Bajo Nivel / Álgebra Numérica  
**Objetivo:** Desarrollar pensamiento crítico y capacidad de auditoría forense sobre código científico heterogéneo (Python, C++20, Rust, CUDA, Triton). El alumno aprenderá que un código que compila o una suite de tests con `PASS` no garantiza corrección matemática, estabilidad numérica ni seguridad en memoria.

---

## 🧭 INSTRUCCIONES GENERALES PARA EL ESTUDIANTE

1. **Entorno de Trabajo:** Cada ejercicio refiere a un archivo fuente específico dentro de `E:\POLYDIM_EINSOF\ENTREGA_2026_10_06_V26150\`.
2. **Metodología de Auditoría:** No suponga que el código funciona porque no arroja error de compilación. Para cada consigna debe:
   - Leer el bloque de líneas indicado.
   - Analizar el flujo de datos, tipos de variables y operaciones de memoria/álgebra.
   - Ejecutar o diseñar un caso de prueba mínimo (*Minimum Reproducible Example - MRE*) que evidencie el comportamiento anómalo.
   - Responder las preguntas técnicas de la consigna con rigor y sin ambigüedades.
3. **Criterio de Evaluación:** No se busca que reescriba el código completo, sino que **identifique formalmente la causa raíz del fallo y documente su impacto**.

---

## 🧪 LABORATORIO 1: TIPADO, INTEGRIDAD DE MEMORIA Y SEGURIDAD FFI

### Ejercicio 1.1 — Offsets y Memoria Compartida en PMTP
* **Archivo:** [`polydim_v26150_monolito.py`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/polydim_v26150_monolito.py)
* **Bloque:** Líneas 215–221 (`PmtpSlabAllocator.as_ndarray`)
* **ID:** `PMS-04`, `PMS-05`
* **Consigna:**
  1. Analice las condiciones lógicas de validación en `as_ndarray()`.
  2. ¿Qué ocurre si un proceso cliente solicita una vista con `offset = -8` y `dtype = np.float64`?
  3. Ejecute en un script independiente una llamada a `as_ndarray` con dicho offset. ¿Qué código de retorno del sistema operativo obtiene? ¿Por qué la excepción no fue capturada por la capa de Python?
  4. ¿Qué sucede si se solicita `offset = 1` para un arreglo `float64`? ¿Qué consecuencias acarrea un puntero desalineado en arquitecturas SIMD modernas?

---

### Ejercicio 1.2 — Violación del Modelo de Préstamos y Aliasing en Rust FFI
* **Archivo:** [`kernel_rust_v26150.rs.txt`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/kernel_rust_v26150.rs.txt)
* **Bloque:** Líneas 148–155 (`polydim_sphere_project_v1350`)
* **ID:** `RS-04`, `RS-05`
* **Consigna:**
  1. Observe cómo se construyen los slices de Rust a partir de los punteros crudos `in_ptr` y `out_ptr` usando `std::slice::from_raw_parts` y `std::slice::from_raw_parts_mut`.
  2. En C++, la operación *in-place* (`out_ptr == in_ptr`) es común y permitida. Si un llamador FFI pasa el mismo puntero para entrada y salida en Rust, ¿qué regla fundamental de la semántica de referencias mutables de Rust se está violando (`Aliasing Rule`)?
  3. ¿Por qué el bloque `catch_unwind` en la línea 139 es incapaz de interceptar el Comportamiento Indefinido (*Undefined Behavior*) derivado de punteros superpuestos?

---

### Ejercicio 1.3 — Tipos Enteros, Booleanos y Truncamiento Silencioso
* **Archivo:** [`polydim_v26150_monolito.py`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/polydim_v26150_monolito.py)
* **Bloque:** Líneas 466–469 (`retract_stiefel`)
* **ID:** `PY-19`, `PY-20`, `PY-21`
* **Consigna:**
  1. Observe la instrucción `out = np.empty_like(X)`.
  2. Suministre una matriz $X \in \mathbb{R}^{2 \times 2}$ creada con `dtype=np.int32` o `dtype=np.bool_`.
  3. ¿Qué ocurre cuando el resultado de los productos matriciales continuos en coma flotante se asigna a `out[:]`?
  4. Ejecute la función y observe el valor de `status`. ¿El sistema rechazó el tipo de dato o devolvió `Status.OK` entregando una matriz corrupta/identidad truncada?

---

## 📐 LABORATORIO 2: INVARIANZA GEOMÉTRICA, RANGO DINÁMICO Y ESTABILIDAD

### Ejercicio 2.1 — Ruptura de Homogeneidad en la Retracción de Stiefel
* **Archivo:** [`polydim_v26150_monolito.py`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/polydim_v26150_monolito.py)
* **Bloque:** Líneas 399–443 (`retract_stiefel`)
* **ID:** `PY-15`, `PY-16`
* **Contexto Teórico:** El generador antisimétrico de rotación infinitesimal que desplaza $X$ en la dirección $+Z$ es $\mathbf{W} = Z X^T - X Z^T$, el cual satisface $\mathbf{W} X = Z$. La retracción de Cayley $\mathcal{R}_X(tZ) = (I - \frac{t}{2}\mathbf{W})^{-1}(I + \frac{t}{2}\mathbf{W})X$ calculada de forma reducida coincide con la solución analítica $D \times D$ (discrepancia $\le 1.9 \times 10^{-13}$).
* **Consigna:**
  1. En geometría diferencial, la curva generada por una retracción depende del vector tangente total: el par $(\mathbf{Z}, t)$ y el par $(\alpha \mathbf{Z}, t/\alpha)$ representan idéntico desplazamiento $t\mathbf{Z}$.
  2. Compare la salida de:
     * Caso A: $X = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, Z = \begin{pmatrix} 0 \\ 1 \end{pmatrix}, \text{step} = 1.0 \implies Y \approx \begin{pmatrix} 0.6 \\ 0.8 \end{pmatrix}$
     * Caso B: $X = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, Z = \begin{pmatrix} 0 \\ 10^{154} \end{pmatrix}, \text{step} = 10^{-154}$
  3. Explique paso a paso por qué el cálculo temprano de $T = \mathbf{Z}^T \mathbf{Z}$ (línea 403) antes de aplicar la escala $\text{step}$ destruye la precisión y altera el resultado de la retracción en el Caso B, a pesar de que ambos operan en el rango de los números `float64` estándar.

---

### Ejercicio 2.2 — Desbordamiento en la Multiplicación y Comportamiento de Neumaier en C++
* **Archivo:** [`kernel_cpp_v26150.cpp.txt`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/kernel_cpp_v26150.cpp.txt)
* **Bloque:** Líneas 106–113 y 151–155 (`sphere_project`)
* **ID:** `CPP-01`, `CPP-02`, `CPP-06`
* **Contexto Teórico:** La afirmación de que $D=10^7$ necesariamente hace fallar la tolerancia de unidad por la cota ingenua $D \cdot \epsilon_{\text{mach}} > 10^{-12}$ es un falso positivo: la suma compensada de Neumaier acumuló exactamente $1.0$ en vectores uniformes probados en silicio. Sin embargo, Neumaier compensa los errores de la adición, pero no rescata multiplicaciones $x_i \cdot x_i$ que desbordan antes de sumar.
* **Consigna:**
  1. Calcule qué ocurre al evaluar la norma de un vector $\mathbf{v} = (10^{200}, 10^{200})$ o $\mathbf{u} = (10^{-200}, 10^{-200})$.
  2. Aunque $\|\mathbf{v}\|_2 \approx 1.414 \times 10^{200}$ y $\|\mathbf{u}\|_2 \approx 1.414 \times 10^{-200}$ son perfectamente representables en IEEE-754 double precision ($10^{\pm 308}$):
     * ¿Por qué $\mathbf{v}$ produce `POLYDIM_NONFINITE_INPUT`?
     * ¿Por qué $\mathbf{u}$ produce `POLYDIM_ZERO_VECTOR`?
  3. ¿Qué técnica clásica de álgebra lineal numérica (ej. algoritmo de 2 pasos escalado por $\max_i |x_i|$) resuelve este desbordamiento previo?

---

### Ejercicio 2.3 — Transporte Paralelo en Esferas y el Peligro del Cut Locus
* **Archivo:** [`kernel_cpp_v26150.cpp.txt`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/kernel_cpp_v26150.cpp.txt)
* **Bloque:** Líneas 197–213 (`sphere_transport`)
* **ID:** `CPP-15`, `CPP-16`, `CPP-18`
* **Consigna:**
  1. En el transporte de Schild / Levi-Civita sobre la esfera $S^{D-1}$, la fórmula implementada incluye el factor $\frac{\mathbf{y}^T \mathbf{v}}{1 + \cos\theta}$.
  2. ¿Qué ocurre cuando los puntos $\mathbf{x}$ e $\mathbf{y}$ son casi antipodales ($\theta \approx \pi$, es decir $\cos\theta \approx -1$)?
  3. Diseñe un caso de prueba donde las entradas $\mathbf{x}, \mathbf{y}, \mathbf{v}$ sean finitas y válidas, pero la evaluación intermedia genere `Inf` o `NaN`.
  4. ¿Por qué la condición `if (std::abs(val) > 1e-12)` en la línea 217 no detiene un `NaN` y permite que la función retorne `POLYDIM_OK`?

---

## 🏗️ LABORATORIO 3: ARQUITECTURA DE SOFTWARE, DISPATCH Y SUITES DE PRUEBA

### Ejercicio 3.1 — El Falso Dispatch y la Ilusión de Telemetría
* **Archivo:** [`polydim_v26150_monolito.py`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/polydim_v26150_monolito.py)
* **Bloque:** Líneas 253–375 (`HardwareProbe`) y Líneas 377–501 (`retract_stiefel`)
* **ID:** `HW-08`, `HW-09`, `PY-32`
* **Consigna:**
  1. Instancie el orquestador solicitando un backend inexistente: `orch = PolydimOrchestratorV1350(preferred_backend="backend_fantasma")`.
  2. Ejecute una retracción y revise el diccionario `metrics["backend"]`. ¿Qué nombre reporta el sistema?
  3. Busque dentro del método `retract_stiefel()` cualquier estructura condicional (`if`, `switch`, o `getattr`) que derive el cálculo a una biblioteca C++, Rust o CUDA. ¿Existe algún mecanismo de despacho o todo ejecuta incondicionalmente NumPy?

---

### Ejercicio 3.2 — El Entry Point "Stub" en CUDA
* **Archivo:** [`kernel_cuda_v26150.cu.txt`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/kernel_cuda_v26150.cu.txt)
* **Bloque:** Líneas 212–229 (`polydim_stiefel_retract_cuda_v26150`)
* **ID:** `CU-07`, `CU-09`, `CU-10`
* **Consigna:**
  1. Lea atentamente las líneas 212 a 229 del archivo CUDA.
  2. Enumere qué validaciones realiza la función antes de la instrucción `return POLYDIM_OK;`.
  3. Identifique si en alguna línea de esa función se invoca a `cudaMemcpy`, kernels auxiliares de GPU, o librerías cuBLAS / cuSOLVER.
  4. Si un usuario invoca esta función desde C FFI esperando una retracción calculada en `d_out`, ¿qué estado de memoria encuentra en su buffer de salida tras recibir el status de éxito?

---

### Ejercicio 3.3 — Auditoría de la Suite de Conformance: El Testigo Ciego
* **Archivo:** [`polydim_v26150_monolito.py`](file:///E:/POLYDIM_EINSOF/ENTREGA_2026_10_06_V26150/polydim_v26150_monolito.py)
* **Bloque:** Líneas 504–629 (`run_conformance_suite`)
* **ID:** `TEST-11`, `TEST-14`
* **Consigna:**
  1. Modifique temporalmente el método `retract_stiefel()` para que en la primera línea ejecute `return Status.OK, X, {"ortho_defect": 0.0, "gram_drift": 0.0}` (es decir, una operación identidad que nunca se mueve).
  2. Ejecute la suite de pruebas: `python polydim_v26150_monolito.py --audit-all`.
  3. ¿Cuántos tests aprobaron? ¿Por qué la suite otorgó `14 / 14 PASS` ante una función que no realiza ninguna retracción?
  4. Concluya: ¿Qué diferencia existe entre verificar *invariantes de forma* (como ortogonalidad) y verificar *corrección matemática* (mediante un Oracle diferencial de referencia)?

---

## 📊 RÚBRICA DE EVALUACIÓN (POR EJERCICIO)

Cada consigna será calificada según los siguientes cuatro criterios (Escala 0 a 10):

| Criterio | Excelente (9–10) | Bueno (7–8) | Regular (4–6) | Insuficiente (0–3) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Localización y Comprensión del Código** | Identifica las líneas exactas, explica el flujo de datos y las variables involucradas con terminología precisa. | Identifica las líneas pero su explicación omite detalles del flujo de datos. | Localiza vagamente la sección sin explicar el mecanismo interno. | No localiza el código ni comprende la estructura del bloque. |
| **2. Reproducción Empírica (MRE)** | Diseña un caso de prueba concreto, ejecutable y reproducible que demuestra físicamente el fallo. | Diseña un caso de prueba pero requiere ajustes menores para reproducir el fallo. | Explica teóricamente el fallo sin proporcionar un caso empírico de prueba. | No presenta caso de prueba o la prueba es irrelevante al problema. |
| **3. Análisis de Causa Raíz** | Deduce el origen matemático o de bajo nivel (overflow, aliasing, falta de dispatch, orden de operaciones). | Describe el síntoma adecuadamente pero no profundiza en la causa matemática/física. | Confunde el síntoma externo con la causa raíz. | Diagnóstico incorrecto o basado en suposiciones no demostradas. |
| **4. Rigor Técnico y Claridad** | Comunicación técnica aséptica, sin ambigüedades, citando estándares (IEEE-754, FFI ABI, C++20/Rust). | Explicación clara pero con lenguaje informal o imprecisiones menores de terminología. | Explicación confusa o incompleta. | Respuesta vacía, incoherente o copiada sin análisis. |

---

## 📦 ENTREGABLES REQUERIDOS

El alumno deberá presentar un informe técnico en formato Markdown o PDF conteniendo:
1. Las respuestas a las preguntas de cada ejercicio (Laboratorios 1, 2 y 3).
2. Los scripts mínimos en Python / C++ utilizados para reproducir los fallos observados.
3. El log de salida de la terminal demostrando los códigos de retorno y anomalías detectadas.
