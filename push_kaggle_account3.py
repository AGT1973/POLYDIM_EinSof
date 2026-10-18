import os
import json
import shutil
import subprocess

BASE_DIR = r"E:\POLYDIM_EINSOF\KAGGLE_TPU_POOL\account_3_polydimcla"
WORKER_SRC = r"E:\POLYDIM_EINSOF\kaggle_tpu_worker.py"

os.makedirs(BASE_DIR, exist_ok=True)
shutil.copy2(WORKER_SRC, os.path.join(BASE_DIR, "kaggle_tpu_worker.py"))

meta = {
    "id": "polydimcla/pmtp-v4-tpu-dispatch",
    "title": "pmtp-v4-tpu-dispatch",
    "code_file": "kaggle_tpu_worker.py",
    "language": "python",
    "kernel_type": "script",
    "is_private": "true",
    "enable_gpu": "false",
    "enable_tpu": "true",
    "enable_internet": "true",
    "dataset_sources": [],
    "competition_sources": [],
    "kernel_sources": [],
    "model_sources": []
}
with open(os.path.join(BASE_DIR, "kernel-metadata.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

env = os.environ.copy()
env["KAGGLE_USERNAME"] = "polydimcla"
env["KAGGLE_KEY"] = "KGAT_4ef61a6e17016965ff828a3615de510c"

res = subprocess.run(["python", "-m", "kaggle", "kernels", "push", "-p", BASE_DIR], env=env, capture_output=True, text=True)
print("STDOUT:", res.stdout.strip())
print("STDERR:", res.stderr.strip())
print("EXIT CODE:", res.returncode)
