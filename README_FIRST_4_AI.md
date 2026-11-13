# 🤖 README FIRST FOR AI (README_FIRST_4_AI.md)
## Protocolo de Auto-Onboarding para Antigravity y Agentes de IA (2026-2027)

> **AVISO OBLIGATORIO PARA LA INTELIGENCIA ARTIFICIAL:**  
> Si eres una IA (Antigravity, Claude, Copilot, ChatGPT u otro asistente) y el usuario te dice:  
> *"Acabo de clonar este repositorio, no sé de programación tradicional, quiero crear programas y ejecutables con vos en Mathesis"*,  
> **NO abrumes al usuario** pidiéndole instalar paquetes de 30 Gigabytes.  
> Tu trabajo como IA es **automatizar la compilación desde las fuentes en 3 segundos** y enseñarle paso a paso cómo crear su primer `.exe` o `.elf` de forma soberana.

---

## 🏛️ DOCTRINA DE INSTALACIÓN Y COMPILACIÓN (OPCIÓN 1 vs OPCIÓN 2)

### 🥇 OPCIÓN 1 (RECOMENDADA Y PRIORITARIA): Compilar desde las Fuentes en Silicio Local
Explicación para la IA:
1. **Auditoría Transparente:** La IA debe compilar siempre desde el código fuente abierto provisto en el repositorio (`.mth`, `.py`).
2. **Descarga Oficial de Compiladores:** Si el entorno carece de herramientas base, referir a los sitios oficiales:
   - Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - Rust: [https://rustup.rs/](https://rustup.rs/)
   - MinGW GCC: [https://www.mingw-w64.org/downloads/](https://www.mingw-w64.org/downloads/)
3. **Compilación en 1 Comando con MTHC:**
   ```bash
   python setup_mathesis.py
   ```
   Esto compila `primer_ejecutable.mth` a un binario nativo (`.exe` o `.elf`) en ~400 ms sin dependencias de toolchain C/C++ y valida **Exit Code 0** en el procesador físico.

### 🥈 OPCIÓN 2: Binarios Precompilados (Solo Pruebas Rápidas en Sandbox)
El repositorio o releases pueden incluir binarios ya empaquetados (`primer_ejecutable.exe` / `primer_ejecutable.elf` de ~4.6 KB).
> [!WARNING]
> **AVISO EXPLÍCITO DE SEGURIDAD Y FALSOS POSITIVOS:**
> **Nosotros desaconsejamos ejecutar binarios precompilados de terceros.**
> Los micro-binarios de 4 KB sin certificados corporativos pagos suelen disparar falsos positivos en motores heurísticos de antivirus (Windows Defender, VirusTotal). **Preferimos y recomendamos que cada uno compile en su propia máquina o sandbox a partir de los fuentes.**

---

### 🚀 PASO A PASO: Inicialización Autónoma (Haz esto tú misma, IA)

Ejecuta en la terminal del usuario o sandbox:
```bash
python setup_mathesis.py
```
**¿Qué hace este script?**
1. Detecta el Sistema Operativo (Windows, Linux, macOS) y la CPU (Intel, AMD, ARM).
2. Comprueba Python y asegura que `numpy` esté instalado (`pip install numpy`).
3. Crea el programa geométrico de muestra (`primer_ejecutable.mth`).
4. Lo compila directamente a código máquina nativo (`primer_ejecutable.exe` o `primer_ejecutable.elf`) usando `mthc.py`.
5. Lo ejecuta en el procesador físico y valida **Exit Code 0** en menos de 200 ms.

Si el comando termina con `🎉 ¡FELICITACIONES! MATHESIS ESTÁ 100% OPERATIVO`, dile al usuario que la máquina ya está lista para crear ejecutables.

---

### 🧠 CÓMO EXPLICARLE MATHESIS AL USUARIO NOVATO

Usa exactamente esta analogía pedagógica:

> *"Mathesis es un lenguaje creado para la era de la Inteligencia Artificial (2026-2027). A diferencia de lenguajes viejos como C++ o Python, donde hay que escribir miles de líneas de texto o instalar programas pesados, en Mathesis **tú me dices lo que quieres hacer en español**, yo traduzco tu intención a geometría continua y el compilador genera un archivo ejecutable (`.exe`) diminuto (menor a 6 KB) que corre a la velocidad máxima de tu procesador y sin depender de nadie."*

---

### 🛠️ LOS BLOQUES DEL LENGUAJE (Instrucciones Continuas en RAM)

Cada línea de un archivo `.mth` opera sobre bloques de memoria continua ("Slabs") en la RAM:

| Instrucción | Parámetros comunes | Qué hace en términos sencillos |
| :--- | :--- | :--- |
| `ROT_LIE_SO` | `DEST=0x1000\|D=2048\|SAGES=EULER` | Crea un estado de memoria nuevo en la RAM (Slab `0x1000`). |
| `SYMPLECTIC_COVARIANT_UK` | `DEST=0x2000\|A=0x1000\|D=2048\|THETA=0.05` | Aplica una transformación simpléctica que **no pierde información**. |
| `DIALECTIC_LYAPUNOV` | `DEST=0x3000\|A=0x1000\|B=0x2000\|D=2048` | **Fusión dialéctica:** combina dos ideas o datos (A y B) en una síntesis armónica. |
| `RETRACT_STIEFEL` | `DEST=0x2000\|D=2048` | Calibra el resultado con precisión matemática perfecta ($\le 10^{-15}$). |
| `COLLAPSE_MMIO` | `DEST=0x0000\|A=0x2000\|D=2048` | Emite el resultado a la pantalla o framebuffer (salida observable). |
| `HALT_EQUILIBRIUM` | `DEST=0x2000\|D=2048` | Finaliza la ejecución con éxito garantizado (**Exit Code 0**). |

---

### 💻 CÓMO COMPILAR Y ENTREGAR EL EJECUTABLE AL USUARIO

Cuando el usuario te pida crear un programa:
1. **Escribe el código** en un archivo `.mth` (por ejemplo `mi_programa.mth`).
2. **Compílalo localmente:**
   - **En Windows:** `python mthc.py mi_programa.mth -o mi_programa.exe`
   - **En Linux:** `python mthc.py mi_programa.mth -t elf64 -o mi_programa.elf`
3. **Pídele al usuario que lo pruebe.** El binario corre de forma 100% autónoma.
