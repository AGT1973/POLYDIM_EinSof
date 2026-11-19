# 📘 GUÍA OFICIAL PARA EL ALUMNO: CÓMO USAR LOS MODELOS EINSOF-II & POLYDIM (A COSTO $0 USD)
**Docente:** Ariel García Traba | **Ecosistema:** POLYDIM-EINSOF | **Doctrina:** Soberanía en Silicio & Cero Costo

---

> [!IMPORTANT]
> ### 🛑 AVISO FUNDAMENTAL ANTES DE COMENZAR (HUGGING FACE vs SILICIO):
> 1. **Hugging Face (`Polydim-Einsof`) es un REGISTRO DE PESOS (`.safetensors` / LoRA), NO un servidor de inferencia serverless.**
> 2. **NO intentes hacerle peticiones HTTP a la Inference API de Hugging Face ni pagues "Inference Endpoints" ($0.50/h).**
> 3. Todos los modelos y adaptadores de **EINSOF-II** son **100% PÚBLICOS**.
> 4. Tu `HF_TOKEN` gratuito de Hugging Face solo sirve para autorizar la descarga del modelo base con licencia (ej. Mistral o LLaMA) a la GPU donde lo vas a ejecutar. **La inferencia corre en tu propio silicio (Google Colab, Kaggle o tu PC) y el costo es $0.**

---

## 1. 🐍 CÓMO USARLOS DESDE PYTHON (Google Colab, Kaggle o GPU Local)

Esta es la vía nativa para trabajar con PyTorch, adaptadores LoRA y probar tanto **texto** como **inyección vectorial continua (`inputs_embeds`)**.

### Código Universal de Ejecución:

```python
# =====================================================================
# 1. Instalar dependencias necesarias
# =====================================================================
# En Colab o Kaggle:
# !pip install -q transformers peft accelerate bitsandbytes torch huggingface_hub

import torch
from huggingface_hub import login
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# =====================================================================
# 2. Autenticación Gratuita (Solo para modelos base con licencia)
# =====================================================================
# Pega tu token gratuito de Hugging Face (o configúralo en Colab Secrets)
login("hf_TU_TOKEN_GRATUITO_AQUI")

# =====================================================================
# 3. Selección del Modelo Base y Adaptador EINSOF-II
# =====================================================================
# Ejemplos disponibles en Polydim-Einsof:
# - "Polydim-Einsof/einsof2-mistral-7b-whatsapp-mail-adapter" (Triage y mensajería)
# - "Polydim-Einsof/einsof2-granite-8b-qiskit-stiefel-adapter" (Computación Cuántica)
# - "Polydim-Einsof/einsof2-deepseek-prover-v2-stiefel-adapter" (Matemática Formal)

base_model_id = "mistralai/Mistral-7B-Instruct-v0.3"
adapter_id = "Polydim-Einsof/einsof2-mistral-7b-whatsapp-mail-adapter"

print("⏳ Descargando modelo base y montando en GPU (4-bit NF4)...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    load_in_4bit=True,
    device_map="auto"
)

print("⏳ Fusionando adaptador Stiefel de EINSOF-II...")
model = PeftModel.from_pretrained(model, adapter_id)
model.eval()
print("✅ ¡Modelo cargado exitosamente en GPU a costo $0!")

# =====================================================================
# 4. Modo A: Inferencia Convencional con Texto Plano
# =====================================================================
prompt = "Usuario: Hola, ¿cómo aplico la retracción de Stiefel en mi tesis?"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)

respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("\n--- Respuesta del Modelo ---")
print(respuesta)

# =====================================================================
# 5. Modo B: Inferencia Tensorial Directa (PMTP - inputs_embeds)
# =====================================================================
# Al correr en tu propia GPU, puedes alimentar directamente embeddings continuos:
input_embeddings = model.get_input_embeddings()(inputs.input_ids)

# Aquí puedes inyectar o sumar un vector continuo proyectado en Stiefel S^(D-1):
# input_embeddings[:, -1, :] += vector_stiefel

with torch.no_grad():
    vector_outputs = model.generate(inputs_embeds=input_embeddings, max_new_tokens=100)

print("\n--- Respuesta generada vía inputs_embeds ---")
print(tokenizer.decode(vector_outputs[0], skip_special_tokens=True))
```

---

## 2. 🦙 CÓMO USARLOS DESDE OLLAMA (Local en tu PC, CPU o GPU, Sin Internet)

Ollama es la herramienta ideal si no quieres programar en Python y deseas chatear con los modelos desde la terminal o mediante una API local en tu propia computadora.

### Vía A: Chatear desde la Terminal (CLI)
Para correr los modelos pedagógicos optimizados de la cátedra:
```bash
# Modelos SLM soberanos de EINSOF:
ollama run qwen2.5:1.5b
ollama run deepseek-r1:7b
```

### Vía B: Crear un Modelo EINSOF-II con un `Modelfile`
Si descargaste un archivo GGUF de la suite (`.gguf`), crea un archivo llamado `Modelfile`:
```dockerfile
FROM ./einsof2-glm4-9b-stiefel.Q4_K_M.gguf

SYSTEM """Eres EINSOF-II, un asistente de razonamiento matemático especializado en la variedad de Stiefel S^(D-1), retracción polar de orden 4 y protocolo PMTP."""

PARAMETER temperature 0.7
PARAMETER num_ctx 4096
```
Y luego en tu terminal ejecutas:
```bash
ollama create einsof2-glm4 -f Modelfile
ollama run einsof2-glm4
```

### Vía C: Consultar a Ollama mediante HTTP Local desde Cualquier Script:
Ollama expone un puerto local (`11434`) totalmente gratuito y compatible con la API de OpenAI:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:1.5b",
  "prompt": "Explica la diferencia entre proyección euclidiana y retracción polar en Stiefel",
  "stream": false
}'
```

---

## 3. 🚀 CÓMO USARLOS DESDE ANTIGRAVITY (IDE Agéntico de Google)

En **Antigravity**, puedes usar los modelos de EINSOF-II de tres formas directas:

### Opción A: A través de Ollama Local (API OpenAI-Compatible)
Antigravity puede consultar directamente a tu Ollama local sin gastar tokens de la nube:
1. Asegúrate de que Ollama esté corriendo en segundo plano (`ollama serve`).
2. Configura el endpoint local en tus ajustes de modelo o proveedor:
   - **Base URL:** `http://localhost:11434/v1`
   - **API Key:** `ollama` (o cualquier texto, no se valida)
   - **Model:** `qwen2.5:1.5b` o `deepseek-r1:7b`

### Opción B: A través del Nodo ALADIN (Si estás en la red de la cátedra)
Si tienes acceso a la red del laboratorio:
   - **Base URL:** `http://192.168.100.21:11434/v1`
   - **Modelos disponibles en ALADIN:**
     * `polydim-comms-slm:latest`
     * `clases-tutor-slm:latest`
     * `mathesis-quantum:1.5b`
     * `deepseek-r1:7b`

### Opción C: Mediante Servidores MCP (Model Context Protocol)
La suite incluye herramientas MCP en `.agents/skills/` y `mcp_servers/` que permiten a Antigravity ejecutar consultas matemáticas en la Variedad de Stiefel o recuperar nodos de memoria RAG sin salir del chat.

---

## 4. 🤖 CÓMO USARLOS DESDE CLAUDE CODE (claudework / CLI de Anthropic)

Cuando estás trabajando con **Claude Code** en tu terminal, puedes integrar los modelos de EINSOF-II sin fricción:

### Vía 1: Servidor MCP Local de Ollama
Claude Code soporta servidores MCP de forma nativa. Agrega a tu archivo de configuración de Claude Code (`~/.claude/claude_code_config.json` o mediante flag CLI):
```json
{
  "mcpServers": {
    "ollama-einsof": {
      "command": "npx",
      "args": ["-y", "mcp-server-ollama"],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```
Esto le da a Claude Code herramientas (`tools`) para delegarle tareas pesadas de razonamiento local o embeddings a tu motor EINSOF-II en Ollama sin consumir tu saldo de Claude.

### Vía 2: Delegación por Scripts en la Terminal
Como Claude Code tiene acceso a tu terminal, simplemente dile a Claude:
> *"Claude, ejecuta el script `test_inferencia_stiefel.py` usando el adaptador `Polydim-Einsof/einsof2-mistral-7b-whatsapp-mail-adapter` en Python y muéstrame los resultados de las activaciones."*

Claude Code ejecutará el entorno virtual local de Python, correrá el forward pass con `inputs_embeds` y te devolverá el dictamen de silicio con **Exit Code 0**.

---

## 📋 TABLA RÁPIDA DE LOS MODELOS EINSOF-II PUBLICADOS EN HUGGING FACE

| Adaptador en Hugging Face | Misión / Dominio | Cómo cargarlo en Python (`PeftModel`) |
| :--- | :--- | :--- |
| **`Polydim-Einsof/einsof2-mistral-7b-whatsapp-mail-adapter`** | Triage omnicanal (WhatsApp + Mail) | Base: `mistralai/Mistral-7B-Instruct-v0.3` |
| **`Polydim-Einsof/einsof2-granite-8b-qiskit-stiefel-adapter`** | Computación cuántica Qiskit / Heron | Base: `ibm-granite/granite-8b-code-instruct` |
| **`Polydim-Einsof/einsof2-deepseek-prover-v2-stiefel-adapter`** | Razonamiento formal y Lean 4 | Base: `deepseek-ai/DeepSeek-Prover-V2-7B` |
| **`Polydim-Einsof/einsof2-kimi-16b-stiefel-adapter`** | MoE 16B (2.4B activos) | Base: Moonshot Kimi MoE |
| **`Polydim-Einsof/einsof2-gemma4-31b-stiefel-adapter`** | Auditoría y verificación profunda | Base: Google Gemma 4 31B |
| **`Polydim-Einsof/einsof2-eurollm-9b-stiefel-adapter`** | Lingüística soberana multipolar | Base: EuroLLM 9B Instruct |
| **`Polydim-Einsof/einsof2-glm4-9b-stiefel-adapter`** | Agentes y síntesis dialéctica | Base: `THUDM/glm-4-9b-chat` |
| **`Polydim-Einsof/einsof2-qlora-dual-t4-adapter`** | Checkpoint de referencia Kaggle T4 | Base: Mistral / LLaMA |

---

### 🎓 REGLA DE ORO PARA EL ALUMNO:
1. **Para pruebas de 1 Clic:** Usa **Google Colab** (GPU T4 gratis).
2. **Para pruebas locales sin internet:** Usa **Ollama** (`ollama run qwen2.5:1.5b`).
3. **Para experimentos continuos de 30 horas:** Usa **Kaggle** (Dual T4 gratis).
4. **Costo para tu bolsillo:** **$0.00 USD en todos los casos.**
