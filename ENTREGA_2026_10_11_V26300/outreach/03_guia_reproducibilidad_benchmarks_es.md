# GUÍA DE REPRODUCIBILIDAD POLYDIM: BENCHMARKING EN HARDWARE ESTUDIANTIL

**Institución:** UTN-FRBA / Cátedras de Sistemas y Posgrado en IA  
**Régimen de Auditoría:** Regla 10 (Veto Empírico) y Regla 34 (Rigor Pedagógico Diario)  

---

## 1. PROPÓSITO Y RIGOR METODOLÓGICO
Bajo el principio de que ninguna métrica de rendimiento se publica sin un script de reproducción ejecutable y salida de terminal verificable (`Exit Code 0`), esta guía detalla los pasos para ejecutar la suite de conformidad POLYDIM V26155 en hardware de consumo de alumnos:
* AMD APU Dual-Core / Quad-Core (AMD A4, Ryzen 3/5).
* Intel Core i3 / i5 / i7 / i9 (Generaciones 8+).
* Apple Silicon (M1/M2/M3) vía entorno estándar o arm64 nativo.
* Equipos portátiles de 4 GB a 16 GB de memoria RAM DDR3/DDR4/DDR5.

---

## 2. REQUISITOS Y CONFIGURACIÓN DEL ENTORNO

### 2.1 Dependencias
POLYDIM V26155 requiere únicamente Python 3.10+ y bibliotecas científicas estándar:
```bash
pip install numpy scipy
```
Opcional (para aceleración nativa; activa fallback a referencia pura de NumPy si no se encuentran presentes):
* Compilador C++20 (WinLibs GCC 14.2 o Clang 18)
* Toolchain de Rust (rustc 1.80+)

### 2.2 Semillas Deterministas, Tolerancias y Políticas Numéricas
Para garantizar reproducibilidad absoluta entre entornos heterogéneos:
* **Semilla Determinista:** Toda inicialización ortogonal aleatoria emplea semilla fija (`seed = 42` o factorización QR determinista).
* **Umbral de Tolerancia de Ortogonalidad:** Se exige $\|X^\top X - I_k\|_F \le \tau_{\mathrm{orth}} = 10^{-14}$ para números de condición estándar ($\kappa \approx 1$).
* **Distinción entre Corrección Matemática y Rendimiento:** La conformidad de silicio (Exit Code 0) valida estrictamente las 29 invariantes matemáticas (protección de aliasing, inmunidad a NaNs y subnormales, verificación dimensional, ortogonalidad). Las métricas de tiempo y latencia se reportan con fines de diagnóstico y no invalidan la corrección funcional en procesadores estudiantiles lentos.

---

## 3. EJECUCIÓN DE LA SUITE DE CONFORMIDAD

Ejecutar la suite directamente desde la línea de comandos:

```bash
python E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26155\polydim_v26155_monolito.py
```

### 3.1 Salida Esperada y Verificación de los 29 Checks
Al ejecutarse sobre la CPU del host, la suite evalúa 29 comprobaciones deterministas. El registro en terminal debe finalizar exactamente con:

```text
========================================================================================
POLYDIM V26155 UNIVERSAL SILICON ORCHESTRATOR & PMTP BUS CONFORMANCE
========================================================================================
Summary: 29 / 29 checks PASSED.
CONFORMANCE RESULT: SUCCESS (Exit Code 0)
```

---

## 4. DIAGNÓSTICO DE ERRORES Y CASOS DE BORDE

| Mensaje de Error | Causa Raíz | Solución |
| :--- | :--- | :--- |
| `ALIAS_VIOLATION` | Arreglos comparten punteros de memoria | El monolito rechaza punteros solapados; reservar arreglos independientes. |
| `NOT_UNIT` | La matriz $X$ viola $X^\top X = I_k$ | Re-ortonormalizar utilizando `scipy.linalg.qr(X, mode='economic')[0]`. |
| `NOT_TANGENT` | El vector viola $X^\top Z + Z^\top X = 0$ | Proyectar $Z \to T_X \mathrm{St}(n, k)$ mediante $Z - X \mathrm{sym}(X^\top Z)$. |
| Alta Latencia ($> 100\text{ ms}$) | Ahorro de energía térmico en la CPU | Conectar la laptop al cargador; seleccionar perfil de Alto Rendimiento. |
