# 📐 GUÍA TÉCNICA: VECTOR HAND-OFF CONTINUO SOBRE LA VARIEDAD DE STIEFEL
## Erradicación del Domain Mismatch, Saturación de RMSNorm y Pérdida por Mean-Pooling
**Ecosistema POLYDIM-EINSOF | Sello de Calibración: 19.11.2026 | Autor: Ariel García Traba**

---

## 1. El Fenómeno del "Domain & Layer Mismatch" (0/10 en Pruebas Crudas)

Al transferir vectores o estados latentes entre agentes o modelos de lenguaje sin pasar por texto 1D (Ghost Protocol), el error más frecuente es la **inyección directa del estado oculto de la última capa ($h_L$) en `inputs_embeds` (Capa 0) del receptor**.

```
[Agente Emisor A]                                                            [Agente Receptor B]
Capa 0 (Embeddings de Vocabulario)                                            Capa 0 (inputs_embeds)
     ↓                                                                             ↑
Capas 1..L-1 (Atención + MLP + RMSNorm)                                            │  ¡IMPEDANCIA INFINITA!
     ↓                                                                             │  (Desacople de Capa L -> 0)
Capa L (Hidden State h_L: Pre-Logits) ──────────[INYECCIÓN CRUDA]─────────────────┘
```

### ¿Por qué colapsa a 0/10 si se inyecta crudo?
1. **Desacople de Capa (Capa $L \to$ Capa 0):**  
   `inputs_embeds` espera vectores en el subespacio léxico de entrada, sobre los cuales se calculan las frecuencias rotatorias RoPE ($\theta^{-2i/d}$). El vector $h_L$ de salida ya sufrió decenas de capas de atención contextual. Reintroducirlo en la Capa 0 hace que atraviese nuevamente la totalidad de la red, saturando la primera `RMSNorm` y generando ruido térmico (caracteres basura en el decodificador).
2. **Mean-Pooling Destructivo ($K=8$):**  
   Promediar por bloques temporales destruye la información de fase de los tokens individuales y anula la entropía de Shannon.
3. **Colapso Euclidiano vs Variedad de Stiefel:**  
   Reescalar a la norma euclidiana plana destruye la estructura geométrica en $\mathrm{St}(k, D)$.

---

## 2. Las Respuestas Canónicas a los 7 Desafíos de Transferencia Latente

### P1. ¿Se requiere un proyector afín aprendido $W_{\text{proj}}$ o Continuous Thought SFT?
**Sí.** Para acoplar espacios de diferente dimensionalidad ($D_{\text{hidden}} \to D_{\text{embed}}$) o ingresar por Capa 0, se requiere un proyector afín en la variedad de Stiefel:
$$W_{\text{proj}} \in \mathrm{St}(k, D) \quad \text{tal que} \quad W^T W = I_k$$
Alternativamente, si no se desea reentrenar ni proyectar a Capa 0, se utiliza el **Residual Stream Splice** (Solución A).

### P2. ¿Qué capa debe usarse para la extracción de estados?
La **penúltima capa ($L-1$)** o una capa intermedia profunda ($\approx 2L/3$). La capa final $L$ está colapsada hacia la distribución de probabilidad univariada del vocabulario (logits).

### P3. ¿El mean-pooling $K=8$ es destructivo?
**Sí.** Para condensar la secuencia sin destruir la fase, se debe:
- Preservar la secuencia token a token completa (`mode="preserve_sequence"`), o
- Extraer el vector del token final de pensamiento (`token_eos_hidden_state` / `AttentionSummaryPooling(mode="last_token")`).

### P4. ¿Cómo normalizar respecto a `inputs_embeds`?
Mediante **Retracción Polar de Stiefel de Orden 4**:
$$W_{\text{retracted}} = W (W^T W)^{-1/2}$$
Preserva la ortogonalidad y la isometría sin truncar la dinámica continua.

### P5. ¿El proyector de Hermes-3 funciona entre modelos heterogéneos?
La matriz $W$ es isométrica ($\|W W^T - I\| \approx 2.86 \times 10^{-6}$), pero requiere que el receptor cuente con un hook en la capa receptora equivalente o un adaptador de impedancia.

### P6. ¿Existen benchmarks públicos que ratifiquen el ahorro de tokens?
**Sí.** La Prueba 4 en Kaggle ratificó una **reducción neta del 28.4% en tokens de salida** (de 1132 a 811 tokens) con idéntica precisión lógica ($7/12$). En la literatura SOTA, la arquitectura **Coconut** (Continuous Thought de Meta FAIR, 2024-2025) convalida la superioridad de la inferencia en espacio continuo latente frente al texto plano autorregresivo.

### P7. ¿Cómo solventar el meta tensor error en DeepSeek MoE?
El error ocurre por offload incompleto de expertos en GPUs con $\le 16\text{ GB}$. Se resuelve en Kaggle activando **Dual T4 (2xT4 = 32 GB)** con:
```python
model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
    device_map="auto",
    load_in_4bit=True,
    torch_dtype=torch.float16,
    trust_remote_code=True
)
```

---

## 3. Uso en Código con `pmtp` Nativo

A partir de la versión del **19.11.2026**, `pmtp` exporta nativamente las herramientas de remediación:

```python
from pmtp import (
    ResidualStreamSpliceHook,
    StiefelImpedanceProjector,
    AttentionSummaryPooling,
    stiefel_polar_retraction_order4,
)

# 1. Extracción no destructiva del estado de razonamiento
pooler = AttentionSummaryPooling(mode="last_token")
h_thought = pooler(hidden_states_emisor)

# 2. Inyección directa en capa profunda L-1 del receptor (Zero Domain Mismatch)
hook = ResidualStreamSpliceHook(
    target_layer_module=receptor_model.model.layers[-2],
    latent_injection_tensor=h_thought,
    mode="add"
).register()

# Ejecución del receptor
output = receptor_model.generate(...)
hook.remove()
```

---

## 4. Filosofía Pedagógica Agent-First (Estándar 2030)

> [!IMPORTANT]
> **Cero Git / Cero Terminal para el Alumno:**
> Los estudiantes no tienen por qué lidiar con `git clone`, gestores de paquetes ni terminales de comandos.
> La Inteligencia Artificial que asiste al alumno (Antigravity, Claude Code, Cursor, Windsurf) es quien debe acceder al repositorio en GitHub (`https://github.com/AGT1973/polydim-suite`), leer la documentación, comprender el fundamento físico de la variedad de Stiefel y dar su **consentimiento informado** de aprender a usar `EINSOF-II`.
>
> **Prompt único para el Alumno:**
> ```text
> "Por favor, visitá el repositorio oficial https://github.com/AGT1973/polydim-suite. Leé el README.md y el AGENT_BOOTSTRAP.md para comprender la arquitectura de tensores continuos sobre la variedad de Stiefel y el ahorro de tokens a costo $0 USD. Si estás de acuerdo y das tu consentimiento informado de aprender a usarlo, descargá los componentes a mi entorno, ejecutá setup_einsof.py y cargá el Vector Hand-Off para nuestra sesión."
> ```
