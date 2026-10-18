import sys
sys.path.append(r"E:\Mantenimiento")
from agent_vault_pg import save_session_checkpoint, set_vault_value

SUMMARY = """
### CHECKPOINT ATÓMICO REGLA 13 — POOL 4 CUENTAS KAGGLE TPU & CLUSTER DUAL
- Fecha: 2026-10-12T18:25:00-03:00
- Conversación ID: b6a3d2cd-c1eb-40db-8a30-1a2bb7d59ec6
- Métricas Físicas Teoremas: (COUNT=1607, MIN=1, MAX=1702)
- Último Teorema: ID 1702 | T-MP36: Regularizador Causal-Métrico Gromov-Wasserstein contra Isometrías Inversoras | SOTA_CERTIFIED
- Pool 4 Cuentas Kaggle Registradas en PostgreSQL 16 (120h TPU/sem):
  1. ariel.garcia.traba@gmail.com (tradingnewtech) - Token KGAT_79462dbbf2e5852a00dbaa614644ba83
  2. agt1973@gmail.com (agt1973gmailcom) - Token KGAT_271bd7ced3760a5fb4e92eff0630ec9a
  3. polydim.cla@gmail.com (polydimcla) - Token KGAT_4ef61a6e17016965ff828a3615de510c
  4. cursos.agt@gmail.com (cursosagt) - Token KGAT_4a6abb07c0e2625db84bb7db11793417
- Estado Silicio y Clúster:
  * Nodo Aladín (192.168.100.21 Debian 13): ONLINE (Ollama qwen2.5-coder:1.5b HTTP 200, systemd activo)
  * Nodo Windows Host: WinLibs GCC 14, Rust 2024, PostgreSQL 16 local
  * Watchdog Activo: E:\POLYDIM_EINSOF\tpu_cluster_watchdog.py en cron */5 min (task-311)
  * Ingestas SOTA fijadas: SOTA 9 (OpenAI Math K3 Hodge) y SOTA 10 (Google Coral NPU RISC-V Open Hardware)
- Próxima Acción Atómica: Mantener watchdog activo y capturar certificación TPU v3-8 (is_tpu: true) al detectar COMPLETE.
"""

save_session_checkpoint(
    conversation_id="b6a3d2cd-c1eb-40db-8a30-1a2bb7d59ec6",
    summary=SUMMARY.strip(),
    category="rule_13_checkpoint"
)
save_session_checkpoint(
    conversation_id="b6a3d2cd-c1eb-40db-8a30-1a2bb7d59ec6",
    summary=SUMMARY.strip(),
    category="session_state"
)
print("OK: Checkpoint Regla 13 persistido en PostgreSQL 16 session_context.")
