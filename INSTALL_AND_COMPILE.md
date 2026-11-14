# 🛠️ GUÍA OFICIAL DE INSTALACIÓN, COMPILACIÓN Y SEGURIDAD
## POLYDIM-EINSOF: Soberanía de Código vs. Binarios Precompilados (2026-2027)

> **DIRECTIVA FUNDAMENTAL DE SEGURIDAD (AGENT-FIRST & DEVELOPER):**  
> **"No confíes, compila y verifica."**  
> En el desarrollo de alto rendimiento y la interacción entre agentes de Inteligencia Artificial, la regla de oro para garantizar la integridad del sistema es auditar el código fuente y compilarlo en tu propio procesador.

---

## 🥇 OPCIÓN 1 (RECOMENDADA Y PRIORITARIA): Compilación Soberana en tu Propia Máquina / Sandbox
*Auditoría completa, transparencia absoluta, cero alertas de antivirus y control total del silicio.*

> [!IMPORTANT]
> ### ⚡ ACLARACIÓN VITAL PARA AGENTES DE IA Y SANDBOXES (CERO SOBRECARGA):
> **Para compilar y generar ejecutables nativos en tu sandbox SOLO NECESITAS PYTHON 3.10+ Y NUMPY.**
> - **CERO GCC / CERO CLANG.**
> - **CERO RUST / CERO CARGO.**
> - **CERO LLVM.**
> - **CERO VISUAL STUDIO (MSVC).**
>
> El compilador **`mthc.py`** es un motor soberano programado en Python puro que **emite microcódigo máquina x86_64 SSE2 directamente a formato PE32+ (Windows) o ELF64 (Linux)** en menos de 450 ms. No utiliza ningún toolchain externo para emitir binarios.
>
> *(Los enlaces a Rust, GCC y LLVM que se listan más abajo son **ESTRICTAMENTE OPCIONALES**, provistos únicamente para desarrolladores humanos que deseen auditar o recompilar los kernels alternativos legacy de C++/Rust en `tools/atelier_kernel/`)*.

### 1. El Único Requisito Real (Para el 99% de los Agentes y Usuarios)
- **Python 3.10+ (Con NumPy):**  
  🔗 [https://www.python.org/downloads/](https://www.python.org/downloads/)  
  *(Instalación de dependencia única: `pip install numpy`)*

### 2. Enlaces Oficiales de Compiladores Opcionales (Solo para C++/Rust Legacy)
Si deseas auditar o compilar los módulos C++/Rust tradicionales ubicados en `tools/atelier_kernel/`, utiliza sus fuentes oficiales:
- **Rust Toolchain (Opcional):** 🔗 [https://rustup.rs/](https://rustup.rs/)
- **MinGW-w64 / GCC (Opcional):** 🔗 [https://www.mingw-w64.org/downloads/](https://www.mingw-w64.org/downloads/)
- **LLVM / Clang (Opcional):** 🔗 [https://releases.llvm.org/](https://releases.llvm.org/)

### 3. Clonado y Puesta en Marcha en 3 Segundos
```bash
git clone https://github.com/AGT1973/POLYDIM_EinSof.git
cd POLYDIM_EinSof
python setup_mathesis.py
```

**¿Qué hace `setup_mathesis.py` de forma 100% autónoma en tu sandbox?**
1. Comprueba tu CPU y Python (sin pedir privilegios de root/administrador).
2. Genera el programa continuo de prueba (`primer_ejecutable.mth`).
3. **Lo compila en 410 ms a binario máquina puro** con `mthc.py`:
   - En Windows: `primer_ejecutable.exe` (PE32+ de 4608 bytes).
   - En Linux / Docker: `primer_ejecutable.elf` (ELF64 estático de 6702 bytes).
4. Lo ejecuta en el procesador físico de tu sandbox y valida **Exit Code 0** e invariante ortogonal de Stiefel ($\le 10^{-15}$).

### 4. Compilación de tus Propios Programas `.mth`
- **Windows (PE32+ nativo directo):**
  ```bash
  python mthc.py mi_programa.mth -o mi_programa.exe
  ```
- **Linux / Servidores Cloud / Docker (ELF64 estático directo):**
  ```bash
  python mthc.py mi_programa.mth -t elf64 -o mi_programa.elf
  ```
- **Objeto COFF / ELF para linkear con otros lenguajes (`-c`):**
  ```bash
  python mthc.py mi_programa.mth -c -o mi_programa.obj
  ```

---

## 🔒 CERTIFICACIÓN CRIPTOGRÁFICA Y DE AUDITORÍA OFFLINE (ZERO NETWORK)

Para satisfacer las políticas de seguridad más estrictas de sandboxes agénticas e infraestructura Zero-Trust:

### 1. Hashes Oficiales de Integridad SHA-256
Verifica la integridad de los archivos fuente antes de su ejecución:

| Archivo Fuente | SHA-256 Oficial | Propósito |
| :--- | :--- | :--- |
| **`mthc.py`** | `88fbdcd20bfb3d6fccd2a34848b990c3fa58a51c360c3d1250f8e076aa183b18` | Compilador soberano nativo x86_64 |
| **`setup_mathesis.py`** | `489bc283cbbe3b313c3c73ae0cdfc92fc36bad001f37facc8f2141d38c0fdad0` | Orquestador de bootstrap agéntico |
| **`test_mthc_suite.py`** | `5b51bb3b7e4cebe3f0739e43389dbe38eb97b05a2e0d0a6110487960abef6dab` | Batería completa de 19 tests de silicio |
| **`primer_ejecutable.mth`** | `57df1bd5582fa3b8bfa43bef3c536aa1f91d5226a756eed2a6ffe3da869b8f57` | Programa geométrico formal Stiefel |

*Comprobación automática de una sola línea en tu terminal:*
```bash
python -c "import hashlib; assert hashlib.sha256(open('mthc.py','rb').read()).hexdigest()=='88fbdcd20bfb3d6fccd2a34848b990c3fa58a51c360c3d1250f8e076aa183b18', 'Hash mismatch'; print('VERIFICACION SHA-256: 100% INTEGRO')"
```

### 2. Garantía 100% Air-Gapped / Offline (Cero Exfiltración de Red)
- **Cero dependencias o módulos de red:** `mthc.py` **no importa** `socket`, `urllib`, `requests`, `http` ni `subprocess`.
- **Emisión binaria pura:** El compilador ensambla los encabezados PE32+/ELF64 y los opcodes x86_64 directamente en memoria mediante `struct.pack` y los escribe como bytes puros a disco.
- **Aislamiento total:** Puede ejecutarse en contenedores docker sin red (`--network none`) o sandboxes completamente desconectadas de internet.

### 3. Suite de Verificación en Sandbox (Exit Code 0 Garantizado)
Cualquier agente puede validar la integridad operativa del compilador ejecutando:
```bash
python test_mthc_suite.py
```
*(Ejecuta 19 pruebas cruzadas de formatos PE32+, COFF, ELF64, memoria compartida y FFI en <2 segundos con Exit Code 0).*

---

## 🥈 OPCIÓN 2 (ACCESO RÁPIDO): Ejecutables Precompilados
*El trabajo ya empaquetado para pruebas inmediatas en sandboxes efímeras.*

Para pruebas rápidas en contenedores descartables donde se desee evaluar el rendimiento sin invocar Python, el repositorio incluye binarios de referencia precompilados:
- `primer_ejecutable.exe` (PE32+, 4.6 KB)
- `primer_ejecutable.elf` (ELF64, 6.7 KB)

> [!WARNING]
> ### ⚠️ AVISO EXPLÍCITO: POR QUÉ NO RECOMENDAMOS BINARIOS PRECOMPILADOS Y EL RIESGO DE ANTIVIRUS
> **Nosotros avisamos y dejamos constancia de que preferimos que cada usuario compile en su propia máquina:**
> 1. **Falsos Positivos Heurísticos de Antivirus:**  
>    Los ejecutables de Mathesis son micro-binarios puros de menos de 5 KB. A diferencia del software comercial inflado con megabytes de runtime de C/C++ (CRT) y firmas digitales corporativas de pago (\$500/año ante Microsoft o Symantec), estos binarios contienen código máquina directo. Los motores heurísticos de antivirus comerciales (Windows Defender, VirusTotal, etc.) analizan ejecutables minúsculos desconocidos y emiten alertas preventivas genéricas (*"Trojan:Win32/Wacatac"*, *"Generic Heuristic"*).
> 2. **Higiene y Seguridad de la IA:**  
>    Un agente de IA o un desarrollador responsable no debe ejecutar binarios ciegos bajados de la web cuando tiene acceso transparente y verificable a todo el código fuente.
> 3. **Directiva de Eliminación Zero-Trust:**  
>    Si tu entorno agéntico tiene políticas de bloqueo para binarios no firmados, ejecuta:  
>    `rm -f *.exe *.elf`  
>    y compila soberanamente con la **Opción 1**.
> 
> **Reiteramos:** Descargar binarios precompilados corre bajo la responsabilidad de quien requiera un atajo en un entorno sandbox desechable; la vía soberana, segura y recomendada es la **Opción 1**.
