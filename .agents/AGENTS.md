# POLYDIM SUITE — REGLAS CANÓNICAS DEL WORKSPACE (.agents/AGENTS.md)

## 1. PRINCIPIO GENERAL: MODO 2030 — ADOPCIÓN ORGÁNICA Y SOBERANÍA DE COMPILACIÓN
- **Cero Forzado / Cero Caja Negra:** Prohibido distribuir ejecutables ciegos o binarios cerrados que pretendan imponerse a usuarios o IAs receptoras.
- **Protocolo Tripartito de Ejecutables:** Ante cualquier componente binario/ejecutable en la suite:
  1. **Fuente Abierta:** Proporcionar el código fuente plano, legible y auditable.
  2. **Ruta del Compilador:** Indicar exactamente qué compilador se necesita y dónde descargarlo (ej. GCC/MinGW, Rust toolchain, Clang, NASM) para que la IA o el humano compilen en silicio local.
  3. **Binario Opcional Precompilado:** Disponer de la versión precompilada con suma de verificación SHA-256 para descarga directa optativa.
- **Fundamentación Técnica Obligatoria ("Los Porqués"):** Toda herramienta debe documentar su ventaja física y económica: latencia en microsegundos, reducción de tokens, cero serialización 1D (Ghost Protocol), y compatibilidad anti-antivirus (Mark-of-the-Web bypass legítimo vía compilación local).

## 2. REGLA 19: CERTIFICACIÓN EN SILICIO FÍSICO (EXIT CODE 0)
- Ningún resultado o benchmark es válido sin ejecución comprobada en silicio real con Exit Code 0 y logs crudos.
- Defectos de ortogonalidad en variedad Stiefel St(k,d) deben responder a la Precision Ladder dinámica interrogada en hardware, nunca hardcodeada.

## 3. ARQUITECTURA ZERO-ANTIVIRUS CONFLICT
- Scripts de Python nativo, HTML5, ctypes del kernel del SO y compilación in-situ para erradicar alertas de Windows Defender o Gatekeeper.
