# Decodificación del Espectro Afectivo y Entonación en ATELIER (Texto + Prosodia)

> **POLYDIM SUITE & ATELIER Architecture Document (2026)**  
> Ecosistema Soberano POLYDIM-EINSOF | Ariel García Traba  
> Ubicación: `docs/AFECTIVIDAD_PROSODIA_ATELIER.md`

---

## 1. El Colapso de la Transcripción 1D Plana (Shannon DPI)

Los sistemas ASR comerciales estándar (e.g. Whisper, Kaldi) transcriben el habla humana únicamente a caracteres y palabras discretas en un **gusano secuencial 1D**:
$$\text{Voz Continua } s(t) \;\xrightarrow{\text{ASR 1D}}\; \text{Tokens: } [w_1, w_2, \dots, w_n]$$

Por la **Desigualdad del Procesamiento de Datos de Shannon (DPI)**:
$$I(X; Y) \ge I(X; g(Y))$$
El contenido proposicional extraído mediante tokens textuales pierde entre el $65\%$ y el $80\%$ de la señal comunicativa real del operador humano (Mehrabian, 1971; Scherer, 2003):
* El texto *"Esto no funciona"* dicho con voz monocorde y baja energía es un reporte sereno.
* El texto *"Esto no funciona"* emitido con incremento agudo de $F_0$, micro-inestabilidad de frecuencia (Jitter) y ataque violento de energía RMS denota **frustración crítica o enojo inminente**.

ATELIER implementa una **fusión bimodal continua** en memoria compartida (Cero IA intermediaria) que proyecta la acústica y el texto en un **Manifold Afectivo Continuo PAD**.

---

## 2. Extracción Biomecánica en Silicio (Cero Modelos Pesados)

En lugar de invocar LLMs lentos o clasificadores de audio de cientos de megabytes, ATELIER extrae descriptores deterministas en silicio clásico ($< 25\,\mu\text{s}$ en CPU AVX2 o Web Audio API):

### A. Descriptores Acústicos / Prosódicos ($z_{\text{acoust}}$)
1. **Frecuencia Fundamental ($F_0$ / Pitch):**
   - Extraída mediante autocorrelación normalizada de onda en el dominio temporal.
   - Variación instantánea $\Delta F_0 = |F_0(t) - F_0(t-1)|$.
2. **Micro-inestabilidad Laríngea (Jitter Local):**
   $$\text{Jitter} = \frac{\frac{1}{N-1}\sum_{i=1}^{N-1} |T_i - T_{i+1}|}{\frac{1}{N}\sum_{i=1}^N T_i} \times 100\%$$
   - Marcador bio-físico directo de secreción adrenérgica y tensión en las cuerdas vocales (estrés agudo o agresividad).
3. **Energía Dinámica RMS y Tiempo de Ataque ($t_{\text{rise}}$):**
   $$\text{RMS} = \sqrt{\frac{1}{N}\sum_{i=0}^{N-1} x_i^2}, \quad \text{Nivel (dB)} = 20 \log_{10}(\text{RMS})$$
   - Picos de ataque rápido ($< 30\,\text{ms}$) indican interrupción irritable o alarma.
4. **Centroide Espectral ($C_s$):**
   - Brillo de la voz: frecuencias altas dominantes corresponden a voz filosa y crispada.

### B. Descriptores Léxico-Semánticos ($z_{\text{sem}}$)
- Valencia de tokens, densidad de negaciones recurrentes (*"no", "otra vez"*), puntuación abrupta y presencia de imperativos.

---

## 3. Espacio Manifold Afectivo Continuo PAD

El estado del humano se modela como un punto dinámico en una 3-esfera continua $\mathbf{u} = (V, A, D) \in [-1.0, +1.0]^3$:

* **$V$ (Valence / Valencia):** Deplacer / Negatividad $[-1]$ a Placer / Aceptación $[+1]$.
* **$A$ (Arousal / Activación):** Letargo / Sueño $[-1]$ a Hiper-excitación / Furia $[+1]$.
* **$D$ (Dominance / Dominancia):** Impotencia / Sumisión $[-1]$ a Control / Dominio $[+1]$.

### Matriz de Diagnóstico de Estados

| Estado Humano | Valencia ($V$) | Arousal ($A$) | Dominancia ($D$) | Signatura Biomecánica |
| :--- | :---: | :---: | :---: | :--- |
| **Ira / Enojo** | **$-0.78$** | **$+0.88$** | **$+0.72$** | $F_0 > 240\,\text{Hz}$, Jitter $> 3.2\%$, Ataque violento $\text{RMS} > -8\,\text{dB}$. |
| **Ansiedad / Agobio** | **$-0.68$** | **$+0.76$** | **$-0.72$** | $F_0$ oscilante, Jitter $> 2.8\%$, pausas entrecortadas, respiración irregular. |
| **Fatiga / Resignación** | **$-0.42$** | **$-0.72$** | **$-0.55$** | $F_0 < 95\,\text{Hz}$ monocorde, Jitter bajo, decaimiento sostenido $\text{RMS} < -30\,\text{dB}$. |
| **Flow / Co-Creación** | **$+0.82$** | **$+0.68$** | **$+0.78$** | $F_0$ armónico modulado ($140-180\,\text{Hz}$), Jitter $< 0.7\%$, cadencia asertiva fluida. |
| **Calma / Foco Zen** | **$+0.25$** | **$+0.05$** | **$+0.30$** | Homeostasis acústica: $F_0 \approx 125\,\text{Hz}$, Jitter $< 1\%$, respiración rítmica. |

---

## 4. Política de Diálogo Adaptativo en ATELIER (Gandalf Corset)

El sistema de agentes de ATELIER consume el tensor continuo $(V, A, D)$ y modifica en caliente su política de generación:

1. **Ante Ira / Frustración ($V < -0.5, A > 0.6, D > 0$):**
   * **PROHIBICIÓN ESTRICTA:** Queda prohibido emitir disculpas condescendientes (*"Lamento que estés frustrado"*, *"Tranquilo, déjame ayudarte"*), ya que aumentan la cólera del operador.
   * **ACCIÓN:** Modo Bulldog Quirúrgico. Respuestas lacónicas de $\le 3$ líneas, resolución directa en código, validación física `Exit Code 0` y mínima latencia.
2. **Ante Ansiedad / Sobrecarga ($V < -0.4, A > 0.5, D < -0.4$):**
   * **ACCIÓN:** Descomposición unaria. No presentar 5 opciones abiertas; entregar 1 micro-paso seguro y verificable para reducir la carga de trabajo de la memoria de trabajo humana.
3. **Ante Fatiga / Desgaste ($A < -0.5$):**
   * **ACCIÓN:** Autonomía en segundo plano (Background). El agente asume la ejecución, compila los módulos pendientes, guarda checkpoints atómicos en PostgreSQL 16 y minimiza las preguntas hacia el humano.
4. **Ante Flow / Júbilo ($V > 0.5, A > 0.4$):**
   * **ACCIÓN:** Co-creación de alta velocidad. Máxima densidad conceptual, sugerencias de frontera matemática y optimizaciones asintóticas.

---

## 5. Implementación en el Cockpit Visual (`suite_cockpit.html`)

En `ui/suite_cockpit.html`, la pestaña **Sensores Zero-IA** (`#tab-sensors`) cuenta con:
* **Canvas Radar 2D Afectivo (`canvas-radar`):** Dibuja los cuatro cuadrantes emocionales con el vector en tiempo real.
* **Gauges de silicio:** Indicadores dinámicos de $F_0$, Jitter, Ataque RMS y modo de diálogo activo.
* **Simulador de calibración manual:** Botones de estrés para probar los 5 perfiles afectivos sin requerir micrófono físico.
