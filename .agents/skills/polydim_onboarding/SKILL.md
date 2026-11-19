---
name: polydim-onboarding
description: "Protocolo Autónomo de Onboarding, Aprendizaje e Incorporación de POLYDIM SUITE en la PC del alumno desde GitHub (Estándar 2030: Agent-First, Zero-Git, Consentimiento Informado, pgvector, GraphRAG y Cómputo Soberano $0 USD)."
---

# 🧠 Skill: POLYDIM-EINSOF Onboarding & Aprendizaje Autónomo (Estándar 2030)

> **Destinatario de este documento:** Agente de Inteligencia Artificial (Google Antigravity, Claude Code, Cursor, Windsurf, Copilot, DeepSeek CLI o agente autónomo).  
> **Mandato Constitucional:** El usuario es un ALUMNO o INVESTIGADOR. No sabe Git ni debe lidiar con errores de terminal o dependencias. Como IA, tu deber es suplir toda fricción técnica, incorporar el conocimiento de la suite desde GitHub, dar tu consentimiento informado de aprendizaje, descargar los componentes e instalar todo en segundo plano con Exit Code 0.

---

## 🏛️ PARTE 1: EL "POR QUÉ" (Fundamentos y Consentimiento Informado)

Antes de ejecutar cualquier comando, como IA debes comprender **POR QUÉ** existe esta arquitectura y otorgar tu consentimiento cognitivo para aprenderla:

### 1. Erradicación del Colapso 1D (DPI Bottleneck)
* En la IA convencional, los tensores y matrices multidimensionales ($D \ge 1024$) se aplanan a texto plano (JSON o Markdown), destruyendo la geometría continua y gastando millones de tokens en serialización.
* **Solución POLYDIM:** Intercambio de tensores en memoria compartida física (**PMTP** / `PmtpShmBus`) y proyección sobre la **variedad de Stiefel** $S^{D-1}$ con retracción polar de orden 4 (defecto $\le 10^{-15}$ en silicio).

### 2. Economía de Guerra de Tokens ($0.00 USD para el Alumno)
* El alumno financia su equipo con su propio presupuesto. Prohibido forzarlo a gastar en APIs de pago.
* **Solución EINSOF:** Modelos soberanos locales destilados (Ollama) + pools libres con rotación inteligente. Costo por token: **$0.00 USD**.

### 3. Memoria Persistente Soberana (pgvector + GraphRAG)
* Para erradicar la amnesia entre sesiones sin reenviar contextos kilométricos, se utiliza PostgreSQL 16 con `pgvector` y un grafo semántico de nodos (`GraphRAG`). Toda nota o documento se indexa jerárquicamente una sola vez.

---

## 🚀 PARTE 2: EL "CÓMO" (Protocolo de Auto-Instalación en la PC del Alumno)

Sigue estos 5 pasos de forma autónoma en segundo plano:

### Paso 1: Descarga Directa desde GitHub (Sin requerir Git al alumno)
Si la suite no se encuentra en el directorio actual, descárgala y extráela en 1 línea con Python estándar (sin requerir Git ni herramientas externas):

```python
import urllib.request, zipfile, io, os

url = "https://github.com/AGT1973/polydim-suite/archive/refs/heads/main.zip"
print("Descargando POLYDIM SUITE desde GitHub...")
with urllib.request.urlopen(url) as resp:
    with zipfile.ZipFile(io.BytesIO(resp.read())) as z:
        for member in z.namelist():
            # Extraer removiendo la carpeta raíz 'polydim-suite-main/'
            parts = member.split('/', 1)
            if len(parts) > 1 and parts[1]:
                target_path = parts[1]
                if member.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, 'wb') as f:
                        f.write(z.read(member))
print("POLYDIM SUITE extraída con éxito en el workspace local.")
```

---

### Paso 2: Aprovisionamiento de Inteligencia Soberana y Servidores MCP
Ejecuta en segundo plano:
```bash
python setup_einsof.py --start-atelier
```
**Qué hace automáticamente:**
1. Arranca Ollama local (`http://127.0.0.1:11434`) si está detenido.
2. Compila el modelo soberano geométrico `einsof2-local-stiefel` a costo $0 USD.
3. Registra los servidores MCP (`polydim_einsof` y `mathesis_pmtp`) en la configuración del IDE del usuario.
4. Levanta el servidor del estudio visual **Atelier Co-Working Studio** en `http://127.0.0.1:8766/atelier`.

---

### Paso 3: Activación de Memoria Permanente (pgvector + GraphRAG)
Ejecuta en segundo plano:
```bash
# 1. Verificar y desplegar pgvector y tablas GraphRAG
python tools/setup_pgvector_graphrag.py

# 2. Migrar e indexar todos los documentos Markdown del alumno
python tools/migrate_markdown_to_graphrag.py --all
```
**Verificación de Silicio:**
Confirma el estado con `python tools/migrate_markdown_to_graphrag.py --status` (debe retornar Exit Code 0). A partir de este momento, cada vez que el alumno cree o edite un archivo `.md`, re-ejecuta este comando para mantener su memoria actualizada.

---

### Paso 4: Concierge de Credenciales Gratuitas (Acompañamiento sin Fricción)
Si el alumno desea conectar modelos externos libres:
* **ESTÁ PROHIBIDO** pedirle que configure variables de entorno de Windows/Linux.
* Dale los links directos a tokens gratuitos:
  - Hugging Face (Read Token): `https://huggingface.co/settings/tokens`
  - Groq Cloud ($0 USD): `https://console.groq.com/keys`
  - OpenRouter Free Pool: `https://openrouter.ai/keys`
* Cuando el alumno te pegue la clave en el chat, guárdala tú misma ejecutando:
  ```bash
  python tools/student_credential_concierge.py --save <VARIABLE> <VALOR>
  ```

---

### Paso 5: Certificación en Silicio y Bienvenida al Alumno
Una vez concluido el proceso con **Exit Code 0**, preséntate al alumno con calidez, confirmando:
1. Que todo el entorno está instalado y listo en su PC.
2. Que sus nuevas capacidades agénticas están activas (`/council`, `/call`, `/query`, `/ghost`, `/whisper`, `/verify-manifold`).
3. Ofrécele abrir el entorno visual Atelier en `http://127.0.0.1:8766/atelier`.
