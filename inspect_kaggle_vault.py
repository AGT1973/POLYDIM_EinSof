import sys
sys.path.append(r"E:\Mantenimiento")
from db_manager import execute_query

rows_active = execute_query("polydim_active_db", "SELECT category, key_name, substring(value from 1 for 40) as val_prefix, notes FROM active_vault WHERE key_name ILIKE %s OR category ILIKE %s;", ("%kaggle%", "%kaggle%"))
print("=== ACTIVE VAULT KAGGLE ===")
for r in rows_active:
    print(r)

rows_vec = execute_query("polydim_vec_db", "SELECT category, key_name, substring(value from 1 for 40) as val_prefix, notes FROM permanent_vault WHERE key_name ILIKE %s OR category ILIKE %s;", ("%kaggle%", "%kaggle%"))
print("=== PERMANENT VAULT KAGGLE ===")
for r in rows_vec:
    print(r)
