# ⚡ ATELIER Native Silicon Kernels — Variedad de Stiefel $\text{St}(k, D)$
> **Sub-ecosistema de Aceleración en Silicio de POLYDIM SUITE**  
> **Director de Investigación:** Ariel García Traba — EinsofOS / Nodo ALADIN  
> **Licencia:** MIT  

---

## 🏛️ Protocolo Tripartito de Ejecutables (Estándar 2030)
Para garantizar soberanía computacional, cero cajas negras y erradicación total de conflictos con Windows Defender o Gatekeeper:

### 1. 📖 Código Fuente Abierto y Auditable
* **C++20 ISO Nativo:** [`atelier_stiefel.cpp`](file:///E:/SUITE/tools/atelier_kernel/atelier_stiefel.cpp) — Retracción polar Newton-Schulz Ord. 10 con acumuladores Neumaier y mapeo de memoria compartida Windows Zero-Copy (`Local\PMTP_ATELIER_SLAB`).
* **Rust Soberano:** [`atelier_stiefel.rs`](file:///E:/SUITE/tools/atelier_kernel/atelier_stiefel.rs) — Implementación en Rust puro (`std` nativo, cero dependencias `Cargo.lock` externas).

### 2. 🛠️ Instrucciones de Compilación Local en Silicio
Para compilar localmente en tu propia máquina:
* **Rust:**
  ```cmd
  rustc -O atelier_stiefel.rs -o atelier_stiefel_rs.exe
  ```
* **C++20 (MSVC x64 con vectorización AVX):**
  ```cmd
  call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
  cl.exe /std:c++20 /O2 /arch:AVX /EHsc /utf-8 atelier_stiefel.cpp /Fe:atelier_stiefel_cpp.exe
  ```
* **Script Automático Unificado:**
  ```cmd
  build.bat
  ```

### 3. 📦 Binarios Compilados In-Situ con Certificación de Silicio
Los ejecutables se generan en la misma carpeta:
* `atelier_stiefel_cpp.exe`
* `atelier_stiefel_rs.exe`

---

## 📊 Medición Empírica y Tupla de Verificación (Regla 19)
Ambos ejecutables aceptan parámetros posicionales opcionales `[D]` y `[k]` (por defecto $D=1024, k=16$):
```text
(ExitCode=0, Latency=XX.Xus, NormErr=X.XXe-16, D=1024, k=16, Checks=4/4)
SLAB_ID: ATELIER_STIEFEL_SHM | MANIFOLD: St(k, D) | SHM: Local\PMTP_ATELIER_SLAB
```
* **Defecto de Isometría:** $\|\mathbf{W}^T \mathbf{W} - \mathbf{I}_k\|_\infty \le 10^{-15}$ (`TIER_STIEFEL_FLOOR_15` o `TIER_MACHINE_EPS_16`).
* **Latencia:** En el orden de microsegundos ($\mu\text{s}$).
