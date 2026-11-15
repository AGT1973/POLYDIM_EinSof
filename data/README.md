# Capa de Datos y Persistencia de Referencia (Estándar 2030)

Esta carpeta define los esquemas y conectores de datos para estudiantes e IAs:

## 1. Conexión Soberana PostgreSQL 16 (Clúster Local)
- **Base de datos transaccional:** `polydim_active_db` (tablas `active_vault`, `v_bootstrap_summary`).
- **Base de datos vectorial:** `polydim_vec_db` (tablas `session_context`, `facts`, extensiones `pgvector`).

## 2. Fallback Autosuficiente SQLite
Si el alumno no cuenta con PostgreSQL 16 instalado, la suite opera de forma transparente en memoria local o mediante un archivo SQLite transaccional ligero en `data/suite_local.sqlite`.
