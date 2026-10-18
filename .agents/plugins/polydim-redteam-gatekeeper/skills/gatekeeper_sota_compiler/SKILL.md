---
name: gatekeeper_sota_compiler
description: Valida mecanicamente los 7 axiomas SOTA de POLYDIM_VECDB.sqlite antes de permitir cualquier generacion o compilacion. Si no coinciden los hashes y teoremas analiticos, aborta el build con Exit Code 1.
---

# Gatekeeper SOTA Compiler

Esta skill ejecuta la validacion obligatoria de silicio:
1. Lee los IDs 683 a 689 de E:\\POLYDIM-THEORICAL\\POLYDIM_VECDB.sqlite.
2. Verifica que las correcciones matematicas provengan de Perplexity Sonar-Pro.
3. Aplica Fuzzing Asintotico con =10^7$ y subnormales ^{-315}$.
