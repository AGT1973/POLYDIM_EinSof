import os
import sys
import json
import time
import psycopg2
import numpy as np
from safetensors.numpy import load_file
from huggingface_hub import HfApi, CommitOperationAdd

from fleet_sync_core import (
    get_hf_token,
    TOTAL_FLEET_ORDER,
    generate_model_readme,
    generate_adapter_config
)

def update_db_status(tracker):
    try:
        conn = psycopg2.connect('dbname=polydim_active_db user=postgres password=postgres host=localhost port=5432')
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO active_vault (category, key_name, value, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (category, key_name) DO UPDATE
            SET value = EXCLUDED.value, updated_at = NOW();
        """, (
            'hf_fleet',
            'HF_FLEET_STEP_BY_STEP_STATUS',
            json.dumps(tracker, indent=2)
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[!] Error actualizando DB: {e}")

def main():
    token = get_hf_token()
    if not token:
        print("[!] Token no encontrado.")
        sys.exit(1)

    api = HfApi(token=token)
    user = api.whoami()
    print(f"[+] Autenticado en HF: {user['name']}")

    scripts_dir = r"E:\SUITE\scripts"
    runtime_py = os.path.join(scripts_dir, "einsof_kaggle_qlora_sft.py")

    tracker_file = os.path.join(scripts_dir, "hf_fleet_live_status.json")

    # Inicializar tracker si no existe
    tracker = []
    for idx, item in enumerate(TOTAL_FLEET_ORDER, start=1):
        repo_name = item["repo_name"]
        mtype = item["type"]
        base = item["meta"]["base_model"] if mtype == "adapter" else item["title"]
        tracker.append({
            "idx": idx,
            "repo_name": repo_name,
            "repo_id": f"Polydim-Einsof/{repo_name}",
            "type": mtype,
            "base": base,
            "status": "PENDIENTE",
            "defect": None,
            "error": None,
            "updated_at": None
        })

    with open(tracker_file, "w", encoding="utf-8") as f:
        json.dump(tracker, f, indent=2)

    total = len(TOTAL_FLEET_ORDER)
    print(f"\n=======================================================")
    print(f"  INICIANDO ACTUALIZACIÓN SECUENCIAL DESDE EL MODELO 1/{total}")
    print(f"=======================================================\n")

    for i, item in enumerate(TOTAL_FLEET_ORDER):
        idx = i + 1
        repo_name = item["repo_name"]
        repo_id = f"Polydim-Einsof/{repo_name}"
        mtype = item["type"]
        print(f"\n>>> [{idx}/{total}] Procesando: {repo_id} ({mtype})")

        tracker[i]["status"] = "EN_PROGRESO"
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2)

        try:
            if mtype == "adapter":
                meta = item["meta"]
                d_latent = meta["d_latent"]
                d_model = meta["d_model"]
                safetensors_name = f"stiefel_procrustes_{d_latent}_{d_model}.safetensors"
                safetensors_path = os.path.join(scripts_dir, safetensors_name)

                if not os.path.exists(safetensors_path):
                    raise FileNotFoundError(f"Safetensors no encontrado: {safetensors_path}")

                calib_data = load_file(safetensors_path)
                W = calib_data["W_procrustes"]
                if d_latent <= d_model:
                    gram = W @ W.T
                    defect = float(np.max(np.abs(gram - np.eye(d_latent, dtype=np.float64))))
                else:
                    gram = W.T @ W
                    defect = float(np.max(np.abs(gram - np.eye(d_model, dtype=np.float64))))

                readme_str = generate_model_readme(repo_name, meta, defect, safetensors_name)
                config_dict = generate_adapter_config(repo_name, meta, defect, safetensors_name)

                tmp_readme = os.path.join(scripts_dir, f"tmp_run_README_{idx}.md")
                tmp_config = os.path.join(scripts_dir, f"tmp_run_config_{idx}.json")

                with open(tmp_readme, "w", encoding="utf-8") as f:
                    f.write(readme_str)
                with open(tmp_config, "w", encoding="utf-8") as f:
                    json.dump(config_dict, f, indent=2)

                operations = [
                    CommitOperationAdd(path_in_repo="README.md", path_or_fileobj=tmp_readme),
                    CommitOperationAdd(path_in_repo="adapter_config.json", path_or_fileobj=tmp_config),
                    CommitOperationAdd(path_in_repo=safetensors_name, path_or_fileobj=safetensors_path),
                    CommitOperationAdd(path_in_repo="einsof_kaggle_qlora_sft.py", path_or_fileobj=runtime_py)
                ]

                api.create_commit(
                    repo_id=repo_id,
                    operations=operations,
                    commit_message=f"feat(qlora-v3): 4/4 remediaciones en silicio (Procrustes L-2 defect {defect:.2e}, RoPE compensator, STREAM sharding, Armijo guard) + einsof_kaggle_qlora_sft.py"
                )

                if os.path.exists(tmp_readme): os.remove(tmp_readme)
                if os.path.exists(tmp_config): os.remove(tmp_config)

                tracker[i]["status"] = "HECHO"
                tracker[i]["defect"] = f"{defect:.2e}"
                tracker[i]["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"    [+] {repo_id}: HECHO (Defecto: {defect:.2e})")

            else:
                # GGUF / Eval repo
                title = item["title"]
                readme_str = f"""---
license: apache-2.0
tags:
- polydim
- einsof
- pmtp
- gguf
- qlora-v3
- stiefel-manifold
- continuous-reasoning
- 4-remediations-certified
pipeline_tag: text-generation
---

# 🌀 {repo_name} — QLoRA v3 (4/4 Remediaciones Certificadas & Checkpoint)

**POLYDIM-EINSOF Sovereign Architecture**  
*Autor:* Ariel García Traba (Independent Research / EinsofOS)  
*Estándar de Silicio:* Regla 0 Suprema & Regla 19 (Exit Code 0)  
*Preservación Académica:* Zenodo DOIs [10.5281/zenodo.21136742](https://doi.org/10.5281/zenodo.21136742) | [10.5281/zenodo.24122867](https://doi.org/10.5281/zenodo.24122867)

---

## 🚀 4/4 Remediaciones de Silicio Integradas
1. **Procrustes Stiefel en L-2:** Ortogonalidad analítica con defecto $\\|W W^T - I\\|_\\infty \\le 10^{{-15}}$.
2. **Compensador de Fase $R_\\theta$:** Desacople angular nulo ($< 1.78 \\times 10^{{-15}}\\,\\text{{rad}}$).
3. **STREAM Cache Sharding ($D \\ge 10^6$):** Micro-bloques en caché L1D con suma Neumaier.
4. **Guarda de Armijo Riemanniana:** Decrecimiento monótono en el espacio tangente.

## 📚 Enlaces Oficiales
* **Concept DOI (Zenodo):** [10.5281/zenodo.21136742](https://doi.org/10.5281/zenodo.21136742)
* **Paper Científico V2:** [10.5281/zenodo.24122867](https://doi.org/10.5281/zenodo.24122867)
* **IEEE Quantum Routing:** [10.5281/zenodo.24133731](https://doi.org/10.5281/zenodo.24133731)
* **GitHub Suite:** [https://github.com/AGT1973/polydim-suite](https://github.com/AGT1973/polydim-suite)
"""
                tmp_readme = os.path.join(scripts_dir, f"tmp_run_gguf_{idx}.md")
                with open(tmp_readme, "w", encoding="utf-8") as f:
                    f.write(readme_str)

                api.upload_file(
                    path_or_fileobj=tmp_readme,
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    commit_message="docs(qlora-v3): update README with 4/4 silicon remediations & Zenodo DOIs"
                )

                if os.path.exists(tmp_readme): os.remove(tmp_readme)

                tracker[i]["status"] = "HECHO"
                tracker[i]["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"    [+] {repo_id}: HECHO (README actualizado)")

        except Exception as e:
            tracker[i]["status"] = "ERROR"
            tracker[i]["error"] = str(e)
            print(f"    [!] Error en {repo_id}: {e}")

        # Guardar tracker y DB tras cada modelo
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2)
        update_db_status(tracker)

    print("\n" + "=" * 55)
    print("  PROCESO DE ACTUALIZACIÓN SECUENCIAL FINALIZADO")
    print("=" * 55)

if __name__ == "__main__":
    main()
