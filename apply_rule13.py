import sys
sys.path.append(r"E:\Mantenimiento")
import db_manager

summary_r13 = """# REGLA 13 — REGISTRO DE ESTADO ATÓMICO Y CIERRE DE SESIÓN SOTA
1. METRICAS FISICAS DE TEOREMAS (POSTGRESQL 16 - polydim_vec_db):
   - polydim_theorems: COUNT=1571, DUAL_CERTIFIED=1571 (100%), MIN_ID=1, MAX_ID=1666, MIN_CYCLE=1, MAX_CYCLE=26872.
   - pmtp_v4_theorems: COUNT=46, MIN_ID=27001, MAX_ID=27601, MIN_CYCLE=27001, MAX_CYCLE=27601 (SOTA_CERTIFIED).

2. ULTIMO PROCESO Y TEOREMA CONSIGNADO:
   - polydim_theorems: ID 1666 (Ciclo 26872, V26200) | Enmienda E24-1: Invarianza Criptográfica del Descriptor Wire 120B con ExtFields Integrado | SOTA_CERTIFIED | Staging: enmienda_e24_wire_descriptor_120b.md | Script EC=0 | Perplexity Sonar-Pro OK.
   - pmtp_v4_theorems: ID 27601 (Ciclo 27601, V26250) | Teorema PMTP-v4-046: Cierre de Protocolo y Blindaje FFI Final | SOTA_CERTIFIED.

3. CICLO DE HARDENING Y SUBAGENTES:
   - Ciclo Actual Consolidado: 27601.
   - Subagentes activos: 0. Daemons en background: 0. Tareas activas: 0. Silicio en reposo absoluto.

4. PROXIMA ACCION ATOMICA UNIVOCA:
   - Sincronizacion de teoria en manuscritos formales (Paper V1550+ y Whitebook V1550+) integrando el catalogo de 1571 teoremas y la especificacion PMTP-v4.

5. ARCHIVOS Y RESPALDOS FISICOS VERIFICADOS:
   - Respaldo D: D:\\POLYDIM_BACKUPS\\BACKUP_2026_10_09_DUAL_CERTIFIED\\ (7 archivos: SQL, DUMP y MD)
   - Respaldo I: I:\\Mi unidad\\POLYDIM_BACKUPS\\BACKUP_2026_10_09_DUAL_CERTIFIED\\ (7 archivos: SQL, DUMP y MD)
   - Catalogo Maestro MD: POLYDIM_THEOREMS_CATALOG_SOTA_V26200.md (1.64 MB, 1571 teoremas dual-certificados tabulados)
   - Scripts nucleares: certify_theorems_dual_engine.py, continuous_dual_certifier_daemon.py, generate_full_backup.py"""

# Registrar en session_context bajo rule_13_checkpoint y session_state
db_manager.execute_statement("polydim_vec_db", """
    INSERT INTO session_context (conversation_id, summary, category, created_at)
    VALUES (%s, %s, 'rule_13_checkpoint', CURRENT_TIMESTAMP);
""", ("fb3e85b7-3de8-42d4-92e7-35a634bba5ee", summary_r13))

db_manager.execute_statement("polydim_vec_db", """
    INSERT INTO session_context (conversation_id, summary, category, created_at)
    VALUES (%s, %s, 'session_state', CURRENT_TIMESTAMP);
""", ("fb3e85b7-3de8-42d4-92e7-35a634bba5ee", summary_r13))

print("Regla 13 consignada en PostgreSQL 16 (session_context).")
