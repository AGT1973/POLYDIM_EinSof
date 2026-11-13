# 🛠️ GUÍA OFICIAL DE INSTALACIÓN, COMPILACIÓN Y SEGURIDAD
## POLYDIM-EINSOF: Soberanía de Código vs. Binarios Precompilados (2026-2027)

> **DIRECTIVA FUNDAMENTAL DE SEGURIDAD (AGENT-FIRST & DEVELOPER):**  
> **"No confíes, compila y verifica."**  
> En el desarrollo de alto rendimiento y la interacción entre agentes de Inteligencia Artificial, la regla de oro para garantizar la integridad del sistema es auditar el código fuente y compilarlo en tu propio procesador.

---

## 🥇 OPCIÓN 1 (RECOMENDADA): Compilación Soberana en tu Propia Máquina / Sandbox
*Auditoría completa, transparencia absoluta, cero alertas de antivirus y control total del silicio.*

Recomendamos enfáticamente que cada usuario, alumno o agente de IA compile las fuentes directamente en su propia máquina o sandbox.

### 1. Enlaces de Descarga Oficiales de Compiladores y Entornos
Si tu entorno no cuenta con las herramientas base, descárgalas exclusivamente de sus sitios oficiales:
- **Python 3.10+ (Entorno Base del Compilador Soberano MTHC):**  
  🔗 [https://www.python.org/downloads/](https://www.python.org/downloads/)  
  *(Requiere únicamente NumPy: `pip install numpy`)*
- **Rust Toolchain (Para compilación nativa de alta gama):**  
  🔗 [https://rustup.rs/](https://rustup.rs/)
- **MinGW-w64 / GCC (Cadena de compilación clásica C/C++ en Windows):**  
  🔗 [https://www.mingw-w64.org/downloads/](https://www.mingw-w64.org/downloads/)
- **LLVM / Clang Oficial:**  
  🔗 [https://releases.llvm.org/](https://releases.llvm.org/)

### 2. Clonado de Fuentes Oficiales
```bash
git clone https://github.com/AGT1973/POLYDIM_EinSof.git
cd POLYDIM_EinSof
```

### 3. Compilación Autónoma en 1 Paso (Zero C Toolchain)
Para que no dependas de gigabytes de compiladores externos (MSVC de 30 GB o Makefiles rotos), POLYDIM incluye **MTHC (`mthc.py`)**, un compilador nativo directo escrito en Python puro que emite microcódigo máquina x86_64 SSE2 en formato binario ejecutable en menos de 450 ms:

Ejecuta el asistente de verificación en silicio:
```bash
python setup_mathesis.py
```

**¿Qué hace este comando en tu propia máquina?**
1. Genera el código fuente geométrico de prueba (`primer_ejecutable.mth`).
2. Lo compila en memoria directamente a un binario nativo:
   - **En Windows:** `primer_ejecutable.exe` (PE32+ de 4608 bytes).
   - **En Linux / Docker:** `primer_ejecutable.elf` (ELF64 estático de 6702 bytes).
3. Lo ejecuta en el procesador físico local y valida **Exit Code 0** e invariante ortogonal de Stiefel ($\le 10^{-15}$).

### 4. Compilación Manual de tus Propios Programas `.mth`
- **Windows (PE32+):**
  ```bash
  python mthc.py mi_programa.mth -o mi_programa.exe
  ```
- **Linux / Servidores Cloud (ELF64):**
  ```bash
  python mthc.py mi_programa.mth -t elf64 -o mi_programa.elf
  ```
- **Emisión de Objeto COFF/ELF para linkear con C/Rust (`-c`):**
  ```bash
  python mthc.py mi_programa.mth -c -o mi_programa.obj
  ```

---

## 🥈 OPCIÓN 2 (ACCESO RÁPIDO): Ejecutables Precompilados
*El trabajo ya empaquetado para pruebas rápidas en sandboxes efímeras.*

Para pruebas inmediatas en contenedores descartables donde se desee evaluar el rendimiento sin invocar Python, el repositorio puede acompañar binarios de referencia precompilados:
- `primer_ejecutable.exe` (PE32+, 4.6 KB)
- `primer_ejecutable.elf` (ELF64, 6.7 KB)

> [!WARNING]
> ### ⚠️ AVISO EXPLÍCITO: POR QUÉ NO RECOMENDAMOS BINARIOS PRECOMPILADOS Y EL RIESGO DE ANTIVIRUS
> **Nosotros avisamos y dejamos constancia de que preferimos que cada usuario compile en su propia máquina:**
> 1. **Falsos Positivos Heurísticos de Antivirus:**  
>    Los ejecutables de Mathesis son micro-binarios puros de menos de 5 KB. A diferencia del software comercial inflado con megabytes de runtime de C/C++ (CRT) y firmas digitales corporativas de pago (\$500/año ante Microsoft o Symantec), estos binarios contienen código máquina directo. Los motores heurísticos de antivirus comerciales (Windows Defender, VirusTotal, etc.) analizan ejecutables minúsculos desconocidos y emiten alertas preventivas genéricas (*"Trojan:Win32/Wacatac"*, *"Generic Heuristic"*).
> 2. **Higiene y Seguridad de la IA:**  
>    Un agente de IA o un desarrollador responsable no debe ejecutar binarios ciegos bajados de la web cuando tiene acceso transparente y verificable a todo el código fuente.
> 
> **Reiteramos:** Descargar binarios precompilados corre bajo la responsabilidad de quien requiera un atajo en un entorno sandbox desechable; la vía soberana y recomendada es la **Opción 1**.
