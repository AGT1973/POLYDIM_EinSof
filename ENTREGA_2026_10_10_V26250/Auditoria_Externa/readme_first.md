# 📦 PAQUETE DE AUDITORÍA EXTERNA — POLYDIM EINSOF V26250
**Fecha:** 2026-10-10  
**Autor:** Ariel García Traba  

Bienvenido al paquete de auditoría adversarial externa de POLYDIM EINSOF V26250.

---

## 🗺️ MAPA DE CONTENIDOS DEL PAQUETE

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| **`00_INSTRUCCIONES_AUDITORIA_EXTERNA.md`** | Guía metodológica completa para alumnos y colegas investigadores. |
| **`01_PROMPT_RED_TEAM_MAESTRO_V26250.txt`** | Prompt hostil para suministrar a modelos frontera sin sesgo de complacencia. |
| **`02_CODIGO_FUENTE_CONSOLIDADO_UNIVERSAL_V26250.txt`** | Conjunto 1: Archivo único unificado con todos los kernels (100 KB) para modelos de contexto masivo. |
| **`archivos_modulares/`** | Conjunto 2: Los 5 kernels actualizados como archivos independientes (C++, Rust, CUDA, Triton, Python). |
| **`TABLA_MAESTRA_TEOREMAS_V26250.md`** | Tabla con el catálogo de los 1.571 teoremas SOTA certificados. |
| **`TABLA_MAESTRA_TEOREMAS_V26250.csv`** | Versión tabular CSV de los 1.571 teoremas para análisis y filtrado automático. |
| **`suite_consolidada_1571_teoremas.py`** | Script Python maestro con las 1.571 funciones de prueba individuales y sus docstrings formales. |
| **`scripts_teoremas/`** | Carpeta con los 1.571 scripts individuales de verificación (`verify_th_*.py`). |
| **`logs_teoremas/`** | Carpeta con los 1.559 logs crudos de ejecución física en silicio con Exit Code 0. |
| **`06_PLANTILLA_REPORTE_AUDITORIA.md`** | Plantilla estandarizada para reportar hallazgos y dictámenes. |

---

## 🚀 EJECUCIÓN RÁPIDA DE PRUEBAS
```bash
# Probar muestra rápida de 20 teoremas
python suite_consolidada_1571_teoremas.py --smoke

# Probar un teorema específico (ej: Teorema 1)
python suite_consolidada_1571_teoremas.py --id 1

# Probar la totalidad de los 1.571 teoremas
python suite_consolidada_1571_teoremas.py --all
```
