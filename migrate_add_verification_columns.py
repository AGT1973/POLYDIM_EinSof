import sys
sys.path.append(r'E:\Mantenimiento')
import db_manager

alter_sql = """
ALTER TABLE polydim_theorems 
ADD COLUMN IF NOT EXISTS script_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS script_exit_code INTEGER,
ADD COLUMN IF NOT EXISTS script_path TEXT,
ADD COLUMN IF NOT EXISTS script_log_ref TEXT,
ADD COLUMN IF NOT EXISTS perplexity_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS perplexity_theory_eval TEXT,
ADD COLUMN IF NOT EXISTS perplexity_model TEXT,
ADD COLUMN IF NOT EXISTS verification_timestamp TIMESTAMP WITH TIME ZONE;
"""

db_manager.execute_statement('polydim_vec_db', alter_sql)
print("ALTER TABLE executed successfully.")

cols = db_manager.execute_query('polydim_vec_db', """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'polydim_theorems'
    ORDER BY ordinal_position;
""")
print("=== COLUMNS IN polydim_theorems ===")
for c in cols:
    print(f"  {c['column_name']:25s} {c['data_type']}")
