import os
import json

from fleet_sync_core import TOTAL_FLEET_ORDER

scripts_dir = r"E:\SUITE\scripts"
hf_export = r"E:\POLYDIM_EINSOF\hf_export"

# Fuentes especiales conocidas de adaptadores cosechados
SPECIAL_SOURCES = {
    "einsof2-deepseek-v4-stiefel-adapter": r"E:\POLYDIM_EINSOF\harvest_deepseek_complete\einsof2_deepseek_v4_stiefel_adapter",
    "einsof2-glm4-9b-stiefel-adapter": r"E:\POLYDIM_EINSOF\harvest_glm4_complete\einsof2_glm4_stiefel_adapter",
    "einsof2-kimi-16b-stiefel-adapter": r"E:\POLYDIM_EINSOF\harvest_kimi_complete\einsof2_kimi_stiefel_adapter",
    "einsof2-gemma4-31b-stiefel-adapter": r"E:\POLYDIM_EINSOF\downloaded_gemma4_adapter\einsof2-gemma4-31b-stiefel_adapter",
    "einsof2-deepseek-prover-v2-stiefel-adapter": r"E:\POLYDIM_EINSOF\kaggle_output_deepseek_prover\einsof2-deepseek-prover-v2-stiefel_adapter",
}

print(f"{'#':<3} | {'Repo Name':<42} | {'Tipo':<8} | {'Adapter Source Path':<55} | {'Size MB':<8}")
print("-" * 125)

mapping = []

for idx, item in enumerate(TOTAL_FLEET_ORDER, start=1):
    repo_name = item["repo_name"]
    mtype = item["type"]
    
    adapter_path = None
    adapter_size_mb = 0
    
    if mtype == "adapter":
        # 1. Verificar si tiene fuente especial de harvest
        if repo_name in SPECIAL_SOURCES and os.path.exists(SPECIAL_SOURCES[repo_name]):
            candidate = os.path.join(SPECIAL_SOURCES[repo_name], "adapter_model.safetensors")
            if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
                adapter_path = candidate
        
        # 2. Si no, verificar en hf_export directo
        if not adapter_path:
            candidate = os.path.join(hf_export, repo_name, "adapter_model.safetensors")
            if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
                adapter_path = candidate
                
        # 3. Variantes de nombres comunes en hf_export
        if not adapter_path:
            clean_name = repo_name.replace("-pmtp", "").replace("-adapter", "").replace(".", "_").replace("-", "_")
            for sub in os.listdir(hf_export):
                sub_path = os.path.join(hf_export, sub)
                if os.path.isdir(sub_path) and (clean_name in sub.lower() or sub.lower() in clean_name):
                    cand = os.path.join(sub_path, "adapter_model.safetensors")
                    if os.path.exists(cand) and os.path.getsize(cand) > 0:
                        adapter_path = cand
                        break
                        
        if adapter_path:
            adapter_size_mb = round(os.path.getsize(adapter_path) / (1024 * 1024), 2)
            
    mapping.append({
        "idx": idx,
        "repo_name": repo_name,
        "type": mtype,
        "adapter_path": adapter_path,
        "size_mb": adapter_size_mb
    })
    
    status_str = f"{adapter_size_mb} MB" if adapter_path else ("(N/A - GGUF/Eval)" if mtype == "gguf_eval" else "NO LOCALIZADO")
    disp_path = os.path.basename(os.path.dirname(adapter_path)) if adapter_path else "—"
    print(f"{idx:<3} | {repo_name:<42} | {mtype:<8} | {disp_path:<55} | {status_str:<8}")

with open(r"E:\SUITE\scripts\fleet_adapter_mapping.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, indent=2)

print("\nMapeo guardado en E:\\SUITE\\scripts\\fleet_adapter_mapping.json")
