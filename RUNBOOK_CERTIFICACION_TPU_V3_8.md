<!-- RUNBOOK & GUIÓN DE CERTIFICACIÓN FÍSICA TPU V3-8 (SESSIÓN LOCK KAGGLE WEB UI) -->
<!-- PROTOCOLO: Regla 10 (Cero Simulación) y Dictamen Doctoral Perplexity Sonar-Pro -->

# PROTOCOLO DE CIERRE 100% SUBFASE 4.3: CERTIFICACIÓN FÍSICA EN TPU V3-8

## 1. HALLAZGO TÉCNICO EMPÍRICO IRREFUTABLE
Al despachar el kernel vía Kaggle CLI con el bootstrapper forzado a backend TPU, el sistema operativo del contenedor devolvió el error físico de hardware:
```text
jax.errors.JaxRuntimeError: NOT_FOUND: TPU initialization failed: No jellyfish device found.
RuntimeError: Unable to initialize backend 'tpu': NOT_FOUND: TPU initialization failed: No jellyfish device found.
```
* **"Jellyfish"** es el codename interno del ASIC de Google Cloud TPU (v2/v3).
* **Causa Raíz Dictaminada por Perplexity Sonar-Pro:** El endpoint de la CLI de Kaggle (`kaggle kernels push`) ignora la asignación dinámica de hardware TPU VM y provisiona un pod estándar CPU/Worker. La única vía soportada por Kaggle para provisionar físicamente el pod con los 8 chips TPU v3-8 (Jellyfish) es a través del **Session Lock en la Web UI**.

---

## 2. GUÍA DE DISPARO DE 2 MINUTOS (SESIÓN WEB UI DE KAGGLE)

Para obtener el log certificado con `[TpuDevice(id=0..7)]` y cerrar la Subfase 4.3 al 100%:

1. **Abrir en el Navegador:**
   Ingresar a Kaggle con la cuenta `agt1973@gmail.com` (o `tradingnewtech`):
   🔗 `https://www.kaggle.com/code/agt1973gmailcom/pmtp-v4-tpu-dispatch`

2. **Fijar el Silicio (Session Lock):**
   * En el panel lateral derecho (`Settings` / `Notebook options`):
   * En el desplegable **Accelerator**, seleccionar: **`TPU v3-8`**.
   * Verificar que **Internet** esté en: `Always on`.

3. **Pegar el Kernel de Certificación (`kaggle_tpu_worker.py`):**
   * Copiar el contenido exacto de `E:\POLYDIM_EINSOF\kaggle_tpu_worker.py`.
   * Hacer clic en **"Save Version" -> "Quick Save"** (o **"Run All"**).

4. **Verificación Automática:**
   El worker ejecutará:
   * Inicialización de los 8 dispositivos: `[TpuDevice(id=0), ..., TpuDevice(id=7)]`.
   * Retracción Cayley-SMW en $D=1.000.000, K=16$.
   * Rotación de Clifford en $D=10^7$ FP64.
   * Generación en `/kaggle/working/` del archivo:
     `pmtp_v4_tpu_results_certified.json` con `is_tpu: true` y Exit Code 0.

---

## 3. INGESTIÓN AUTOMÁTICA EN LOCAL
Apenas termine la ejecución en la Web UI, correr desde esta terminal:
```powershell
python -m kaggle kernels output agt1973gmailcom/pmtp-v4-tpu-dispatch -p E:\POLYDIM_EINSOF\TPU_DISPATCH_OUTPUT
```
El script local detectará el JSON con `is_tpu: true`, actualizará PostgreSQL 16 automáticamente y marcará la **Fase 4 al 100.0%**.
