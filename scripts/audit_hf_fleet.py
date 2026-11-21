import psycopg2, json
from huggingface_hub import HfApi

conn = psycopg2.connect('dbname=polydim_active_db user=postgres password=postgres host=localhost port=5432')
cur = conn.cursor()
cur.execute("SELECT value FROM active_vault WHERE key_name = 'HuggingFace_Polydim_Einsof' LIMIT 1;")
token = cur.fetchone()[0].strip()
cur.close()
conn.close()

api = HfApi(token=token)
models = list(api.list_models(author="Polydim-Einsof"))
print(f"Auditing {len(models)} repos on Hugging Face...\n")

fleet_summary = []
for m in models:
    repo_id = m.id
    files = api.list_repo_files(repo_id=repo_id)
    has_safetensors = any(f.endswith(".safetensors") for f in files)
    has_procrustes = any("procrustes" in f.lower() for f in files)
    has_adapter_config = "adapter_config.json" in files
    has_readme = "README.md" in files
    
    fleet_summary.append({
        "repo_id": repo_id,
        "files_count": len(files),
        "files": files,
        "has_safetensors": has_safetensors,
        "has_procrustes": has_procrustes,
        "has_adapter_config": has_adapter_config,
        "has_readme": has_readme
    })

print(f"{'Repository':<55} | {'Files':<5} | {'Safetensors':<11} | {'Procrustes':<10} | {'Config':<6}")
print("-" * 95)
for f in fleet_summary:
    print(f"{f['repo_id']:<55} | {f['files_count']:<5} | {str(f['has_safetensors']):<11} | {str(f['has_procrustes']):<10} | {str(f['has_adapter_config']):<6}")

with open("E:/SUITE/scripts/hf_fleet_current_audit.json", "w") as out:
    json.dump(fleet_summary, out, indent=2)
print("\nSaved audit to E:/SUITE/scripts/hf_fleet_current_audit.json")
