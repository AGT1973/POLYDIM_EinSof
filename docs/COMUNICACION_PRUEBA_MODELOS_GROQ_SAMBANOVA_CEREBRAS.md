# 📡 COMUNICACIÓN: Probá los Modelos POLYDIM en Plataformas de Inferencia Gratuita

**De:** Ariel García Traba — Proyecto POLYDIM-EINSOF  
**Para:** Alumnos, evaluadores e investigadores  
**Fecha:** Noviembre 2026  
**Ref:** Complemento de `COMUNICACION_GUIA_USO_MODELOS_EINSOF_II.md`

---

## 🎯 Objetivo

Esta guía explica cómo probar **gratuitamente** las capacidades de razonamiento matemático y científico de POLYDIM usando **tres plataformas de inferencia ultrarrápida**:

| Plataforma | Hardware | Velocidad | Costo |
|:-----------|:---------|:----------|:------|
| **Groq** | LPU (Language Processing Unit) | ~1,000 tok/s | Gratis (Free tier) |
| **SambaNova** | RDU (Reconfigurable Dataflow Unit) | ~800 tok/s | Gratis (Free tier) |
| **Cerebras** | WSE CS-3 (Wafer-Scale Engine) | ~3,000 tok/s | \$5 crédito trial |

---

## ⚠️ Aclaración Importante: ¿Qué se prueba y qué no?

### Lo que SÍ podés probar en estas plataformas:
- **Modelos base** (Qwen 3.8, DeepSeek, LLaMA 3.3, GPT-OSS) corriendo en hardware exótico a velocidades imposibles en tu PC.
- **Prompts con contexto POLYDIM:** Le das al modelo el problema matemático + el contexto de Stiefel/Neumaier, y evaluás la calidad de respuesta del modelo *base*.

### Lo que NO se puede hacer en estas plataformas:
- **Subir nuestros adaptadores LoRA/QLoRA** (los modelos Einsof-II fine-tuneados). Groq, SambaNova y Cerebras sirven catálogos fijos de modelos — no permiten subir pesos custom.
- Para correr los **modelos Einsof-II adaptados**, usá Colab, Kaggle u Ollama (ver `COMUNICACION_GUIA_USO_MODELOS_EINSOF_II.md`).

### ¿Para qué sirve entonces?
1. **Comparar:** Probá el modelo *base* en Groq vs. el modelo *adaptado Einsof-II* en Ollama. Vas a ver la diferencia.
2. **Velocidad:** Groq y Cerebras son las plataformas de inferencia más rápidas del planeta. Sentí la diferencia.
3. **Deliberación multi-IA:** POLYDIM usa estas plataformas como "pool de consulta" gratuito (Tier 2) para que múltiples IAs deliberen sobre un problema sin gastar un centavo.

---

## 🚀 Paso 1: Crear Cuentas (5 minutos, \$0)

### Groq
1. Ir a [console.groq.com](https://console.groq.com)
2. Crear cuenta con Google/GitHub
3. En **API Keys** → **Create API Key**
4. Copiar la key (empieza con `gsk_...`)

### SambaNova
1. Ir a [cloud.sambanova.ai](https://cloud.sambanova.ai)
2. Crear cuenta
3. En **API Keys** → generar key
4. Copiar la key

### Cerebras
1. Ir a [cloud.cerebras.ai](https://cloud.cerebras.ai)
2. Crear cuenta (te dan \$5 de crédito trial por 30 días)
3. En **API Keys** → generar key (empieza con `csk-...`)

---

## 🐍 Paso 2: Código Python (Copiar y Pegar)

### Instalación (una sola vez)
```bash
pip install openai
```

> Las tres plataformas usan el estándar **OpenAI-compatible API**. Un solo paquete, tres proveedores.

### Código Unificado — Funciona con las 3 plataformas

```python
from openai import OpenAI

# ═══════════════════════════════════════════════════════════
# ELEGÍ TU PLATAFORMA (descomentá UNA):
# ═══════════════════════════════════════════════════════════

# --- GROQ (LPU, ~1000 tok/s, gratis) ---
client = OpenAI(
    api_key="gsk_TU_KEY_AQUI",
    base_url="https://api.groq.com/openai/v1"
)
model = "qwen-qwq-32b"  # o "llama-3.3-70b-versatile"

# --- SAMBANOVA (RDU, ~800 tok/s, gratis) ---
# client = OpenAI(
#     api_key="TU_KEY_AQUI",
#     base_url="https://api.sambanova.ai/v1"
# )
# model = "Meta-Llama-3.3-70B-Instruct"

# --- CEREBRAS (WSE CS-3, ~3000 tok/s, $5 trial) ---
# client = OpenAI(
#     api_key="csk-TU_KEY_AQUI",
#     base_url="https://api.cerebras.ai/v1"
# )
# model = "qwen-3.8-27b"  # o "gpt-oss-120b"

# ═══════════════════════════════════════════════════════════
# PROMPT DE PRUEBA POLYDIM
# ═══════════════════════════════════════════════════════════

prompt = """Eres un asistente de matemática computacional.

Contexto POLYDIM: La variedad de Stiefel St(k, D) es el conjunto de matrices 
W ∈ ℝ^{D×k} tales que W^T W = I_k (columnas ortonormales). La retracción polar 
de orden 4 (QDWH) garantiza isometría con defecto ≤ 1.7 × 10⁻¹⁶ usando 
acumulación compensada de Neumaier.

Pregunta: Dado W ∈ St(3, 1024), un vector tangente Δ ∈ T_W St(3, 1024), 
y paso η = 0.01, ¿cómo se calcula la retracción polar para obtener 
W_new ∈ St(3, 1024)? Mostrar las ecuaciones paso a paso."""

response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=2000
)

print(response.choices[0].message.content)
print(f"\n--- Tokens: {response.usage.total_tokens} | Modelo: {model} ---")
```

---

## 📊 Modelos Disponibles por Plataforma (Nov 2026)

| Modelo | Groq | SambaNova | Cerebras |
|:-------|:----:|:---------:|:--------:|
| `qwen-3.8-27b` / `qwen3` | ✅ | ⚡ Paid | ✅ |
| `llama-3.3-70b-versatile` | ✅ | ✅ | — |
| `gpt-oss-120b` | ✅ | ⚡ Paid | ✅ |
| `gpt-oss-20b` | ✅ | — | — |
| `deepseek-v3.1` | — | ⚡ Paid | — |
| `whisper-large-v3-turbo` | ✅ (audio) | — | — |

> **Tip:** Consultá los modelos activos de cada plataforma con:
> ```python
> for m in client.models.list():
>     print(m.id)
> ```

---

## 🧪 Experimento Sugerido: Base vs. Einsof-II

Para apreciar el valor de los adaptadores POLYDIM, hacé esta comparación:

### Paso A — Modelo Base en Groq (sin adaptador)
```python
# Usar el código de arriba con Groq + qwen-qwq-32b
# Preguntarle sobre retracción polar de Stiefel
# → Va a dar una respuesta genérica, posiblemente con errores
```

### Paso B — Modelo Einsof-II en Ollama (con adaptador)
```bash
# En tu terminal (tu agente de IA ya lo instaló):
ollama run Polydim-Einsof/einsof2-deepseek-v4-stiefel-gguf

# Misma pregunta sobre retracción polar
# → Respuesta precisa, con Neumaier, con defecto numérico correcto
```

### Paso C — Comparar
El modelo Einsof-II fue entrenado específicamente en geometría de Stiefel, acumulación compensada de Neumaier, y operadores PMTP. La diferencia es medible.

---

## 🤖 Para tu Agente de IA (Antigravity / Claude Code / Cursor)

Tu agente puede usar estas plataformas directamente como herramientas de deliberación. Ejemplo en Antigravity:

```
/consulta ¿Cuál es la complejidad asintótica de la retracción polar 
QDWH en St(k,D) para D=10^6?
```

El orquestador (Gandalf) automáticamente:
1. Despacha la consulta a Groq, SambaNova y Cerebras en paralelo
2. Recoge las 3 respuestas
3. Cruza las opiniones y toma una decisión ejecutiva
4. Persiste el resultado en PostgreSQL (pgvector + GraphRAG)

**Costo para vos: \$0 USD.**

---

## 📋 Resumen Ejecutivo

| Qué quiero hacer | Plataforma | Costo |
|:-----------------|:-----------|:------|
| Probar modelos base a máxima velocidad | Groq / Cerebras | \$0 |
| Correr modelos Einsof-II adaptados | Ollama (local) | \$0 |
| Fine-tuning con GPU gratis | Kaggle (4 cuentas, Dual T4) | \$0 |
| Fine-tuning con A100 | Colab Plus | Pagado por el proyecto |
| Deliberación multi-IA automática | `/consulta` o `/sabios` | \$0 |

---

## 🔗 Referencias

- Guía completa de uso de modelos Einsof-II: [`COMUNICACION_GUIA_USO_MODELOS_EINSOF_II.md`](file:///E:/email_AGY/DOCUMENTOS_MAESTROS/COMUNICACION_GUIA_USO_MODELOS_EINSOF_II.md)
- Repositorio de modelos: [huggingface.co/Polydim-Einsof](https://huggingface.co/Polydim-Einsof)
- Documentación del proyecto: [github.com/AGT1973/polydim-suite](https://github.com/AGT1973/polydim-suite)

---

*Proyecto POLYDIM-EINSOF — Co-Working Humano-IA, no Doomsday.*  
*Variedad de Stiefel • Acumulación de Neumaier • Inferencia Soberana a \$0 USD*
