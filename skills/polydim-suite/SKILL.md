---
name: polydim-suite
description: Inspección de telemetría, benchmarks, variedad Stiefel y control de la suite soberana POLYDIM SUITE.
---

# Skill: POLYDIM SUITE (Estándar 2030)

Esta habilidad permite a cualquier agente interactuar con el ecosistema de **POLYDIM SUITE** en su máquina local o en el clúster ALADIN.

## Capacidades Principales:
1. **Comprobación Rápida de Silicio:** Ejecutar `python tests/test_en_vivo.py` para verificar memoria compartida y defecto Stiefel en <1 segundo.
2. **Ejecución de Benchmarks:** Correr `python benchmarks/humaneval_plus_ablation_164_real.py` para reproducir la matriz comparativa de 164 tareas.
3. **Telemetría Cockpit:** Consultar el estado del clúster dual y abrir la interfaz gráfica local en `ui/suite_cockpit.html`.
4. **Soberanía de Compilación:** Si se requiere compilar DLLs o binarios C++/Rust, verificar la existencia de `g++` o `rustc` en el sistema y compilar in-situ sin descargar `.exe` externos.
