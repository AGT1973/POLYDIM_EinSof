# 💰 Costo Real de Fine-Tuning: Lo que Paga la Industria vs. Lo que Paga POLYDIM

**Fecha:** Noviembre 2026 | **Fuentes:** Precios de mercado verificados por búsqueda web + registros de silicio en PostgreSQL

---

## 1. Lo que Cobra la Industria (Precios de Mercado Nov 2026)

### A. Fine-Tuning "Managed" (APIs Comerciales)

| Plataforma | Modelo | Método | Costo por 1M tokens entrenados | Notas |
|:-----------|:-------|:-------|:------|:------|
| **OpenAI** | GPT-4.1 | SFT managed | **\$25.00/1M tok** | ⚠️ Deprecado Jan 2027 |
| **OpenAI** | GPT-4.1 mini | SFT managed | **\$5.00/1M tok** | ⚠️ Deprecado Jan 2027 |
| **OpenAI** | GPT-4o | SFT managed | **\$25.00/1M tok** | ⚠️ Deprecado Jan 2027 |
| **Fireworks.ai** | ≤16B params | LoRA SFT | **\$0.50/1M tok** | Hosting incluido |
| **Fireworks.ai** | 16B–80B | LoRA SFT | **\$3.00/1M tok** | |
| **Fireworks.ai** | 80B–300B | LoRA SFT | **\$6.00/1M tok** | |
| **Together.ai** | Qwen/LLaMA/etc | LoRA SFT | **\$0.48–\$3.00/1M tok** | |
| **Google Vertex AI** | Gemma (open) | Custom Training | **\$0.70–\$5.50/hora GPU** | Pago por compute |
| **Alibaba Bailian** | Qwen 3.8 | SFT-LoRA | **~\$2–8/1M tok** (varía región) | Deploy LoRA gratis |

> **Dato brutal:** OpenAI **cerró su plataforma de fine-tuning** (deadline 6 Ene 2027). Los modelos fine-tuneados mueren con el modelo base. La soberanía de pesos es ilusoria en plataformas cerradas.

### B. Fine-Tuning "Self-Hosted" (GPU en la Nube)

| GPU | Precio On-Demand/h | Neocloud/h | Spot/h |
|:----|:-------------------|:-----------|:-------|
| **A100 40GB** | \$1.50 – \$2.50 | \$1.10 – \$1.40 | **\$0.80 – \$1.10** |
| **A100 80GB** | \$2.50 – \$3.00 | \$1.50 – \$2.20 | **\$1.10 – \$1.50** |
| **H100 PCIe** | \$3.50 – \$4.50 | \$2.20 – \$2.80 | **\$1.49 – \$1.99** |
| **H100 SXM5** | \$5.00 – \$7.00 | \$2.50 – \$3.50 | **\$1.99 – \$2.50** |
| **H200 141GB** | \$6.50 – \$9.00 | \$4.00 – \$4.50 | **\$2.50 – \$3.50** |

### C. Costo Total por Corrida (Estimaciones de Mercado)

| Modelo | Método | Hardware | Tiempo | **Costo Total** |
|:-------|:-------|:---------|:-------|:----------------|
| 7B–8B | QLoRA 4-bit | 1× A100 40GB | 1–2h | **\$2 – \$5** |
| 7B–8B | LoRA fp16 | 1× A100 80GB | 2–4h | **\$5 – \$12** |
| 27B–31B | QLoRA 4-bit | 1× A100 80GB | 3–6h | **\$10 – \$25** |
| 70B | QLoRA 4-bit | 1× H100 | 3–6h | **\$10 – \$25** |
| 70B | Full FT | 8× H100 | 10–30h | **\$1,000 – \$4,000+** |
| 109B MoE | Full FT | 16× H100 | 24–72h | **\$5,000 – \$15,000+** |

---

## 2. Lo que Pagó POLYDIM: \$0 USD (Excepto Colab Plus)

### Flota Completada — Costos Reales de Silicio

| # | Modelo | Plataforma | GPU | Horas | **Costo USD** |
|:--|:-------|:-----------|:----|:------|:--------------|
| 1 | Qwen 3.8 27B SFT | Alibaba Bailian | Cloud (gratis Bailian) | ~2h | **\$0** ¹ |
| 2 | Gemma 4 31B QLoRA | Kaggle Free (cursosagt) | Dual T4 | ~4h | **\$0** |
| 3 | Granite 8B Qiskit QLoRA | Kaggle Free (agt1973) | Dual T4 | ~3h | **\$0** |
| 4 | EuroLLM 9B QLoRA | Kaggle Free (arielgarciat) | Dual T4 | ~3h | **\$0** |
| 5 | Mathesis Quantum 1.5B | Kaggle Free (polydimcla) | Dual T4 | ~1h | **\$0** |
| 6 | Kimi Moonlight 16B MoE | Kaggle Free | Dual T4 | ~4h | **\$0** |
| 7 | DeepSeek V4 Distill | Kaggle Free | Dual T4 | ~3h | **\$0** |
| 8 | GLM-4 9B Dense | Kaggle Free | Dual T4 | ~3h | **\$0** |
| 9 | QLoRA Dual T4 Adapter (Qwen 2.5 1.5B) | Kaggle Free | Dual T4 | ~2h | **\$0** |
| 10 | 18 adaptadores PMTP Stiefel (fleet HF) | Kaggle Free (4 cuentas) | Dual T4 | ~20h total | **\$0** |
| 11 | LLaMA 4 Scout 17B-16E | Colab Plus (A100) | A100 80GB | ~6h | **~\$12** ² |
| — | **TOTAL** | — | — | **~51h GPU** | **~\$12** |

> ¹ Bailian ofrece créditos gratis para SFT-LoRA de modelos Qwen. Deploy LoRA sin cargo adicional.  
> ² Colab Plus: \$11.99/mes. Único costo pagado por el proyecto.

### El Equivalente de Mercado

Si hubiéramos pagado precios de mercado por las mismas corridas:

| Concepto | Mercado | POLYDIM |
|:---------|:--------|:--------|
| 10 modelos QLoRA (7B–31B) en A100 | ~\$50 – \$150 | **\$0** |
| 18 adaptadores PMTP Stiefel | ~\$36 – \$90 | **\$0** |
| 1 modelo 109B MoE en A100 | ~\$25 – \$50 | **\$12** (Colab Plus) |
| **Total estimado mercado** | **\$111 – \$290** | **\$12** |

**Ahorro: 90–96%**

---

## 3. ¿Cómo es Posible? — La Infraestructura de \$0

```
┌──────────────────────────────────────────────────┐
│          INFRAESTRUCTURA POLYDIM GRATIS           │
├──────────────────────────────────────────────────┤
│                                                  │
│  KAGGLE (4 cuentas × 30h/semana = 120h GPU/sem) │
│  ├─ agt1973gmailcom ───── Dual T4 (30h gratis)  │
│  ├─ arielgarciat ──────── Dual T4 (30h gratis)  │
│  ├─ polydimcla ────────── Dual T4 (30h gratis)  │
│  └─ cursosagt ─────────── Dual T4 (30h gratis)  │
│                                                  │
│  ALIBABA BAILIAN (SFT gratis para Qwen)          │
│  └─ Créditos de entrenamiento incluidos          │
│                                                  │
│  ALADIN NODE (192.168.100.21) — Nodo local       │
│  ├─ Ollama: 7 modelos activos                    │
│  ├─ PMTP SHM Bus: inferencia zero-copy           │
│  └─ Costo: electricidad del hogar (~$3/mes)      │
│                                                  │
│  HUGGING FACE (storage + distribución gratis)    │
│  └─ 28 repos públicos en Polydim-Einsof          │
│                                                  │
│  GROQ + SAMBANOVA (inferencia deliberativa)      │
│  └─ 4+9 API keys en rotación = ∞ consultas       │
│                                                  │
│  Colab Plus: $11.99/mes (único gasto)            │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 4. Comparación con Proyectos Comerciales Equivalentes

| Proyecto/Empresa | Qué hacen | Costo estimado mensual |
|:-----------------|:----------|:----------------------|
| Startup IA típica | Fine-tune 3–5 modelos, serve 24/7 | **\$2,000 – \$10,000/mes** |
| Lab universitario | 1 modelo 70B en H100 cluster | **\$500 – \$3,000/mes** |
| OpenAI fine-tune | 1 modelo GPT-4o custom | **\$100 – \$500/corrida** |
| **POLYDIM-EINSOF** | **28 modelos fine-tuned + desplegados** | **\$12/mes** |

---

## 5. La Trampa de las Plataformas Cerradas

| Aspecto | OpenAI / Anthropic / Google | POLYDIM |
|:--------|:----------------------------|:--------|
| ¿Sos dueño de los pesos? | ❌ No | ✅ Sí (HF público) |
| ¿Se pueden migrar? | ❌ Mueren con la API | ✅ Ollama/Colab/cualquier GPU |
| ¿Fine-tuning disponible? | ⚠️ OpenAI cierra Ene 2027 | ✅ Siempre (pesos abiertos) |
| ¿Costo recurrente por servir? | 💸 \$3–\$15/1M tok | ✅ \$0 (Ollama local) |
| ¿Offline / sin internet? | ❌ Imposible | ✅ ALADIN funciona offline |

---

> **Conclusión:** Un fine-tuning real que en el mercado cuesta entre \$2 y \$25 por corrida (QLoRA en 7B–31B), POLYDIM lo ejecuta a **\$0** usando 120 horas semanales de GPU Kaggle gratuita distribuidas en 4 cuentas, más Bailian gratis para Qwen. El único gasto es Colab Plus (\$12/mes) para modelos >31B que necesitan A100. Los pesos son soberanos, migrables y eternos.

*Proyecto POLYDIM-EINSOF — Soberanía a costo de sueldo docente.*
