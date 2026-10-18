import os
import json
import shutil
import subprocess

BASE_DIR = r"E:\POLYDIM_EINSOF\KAGGLE_TPU_POOL"
WORKER_SRC = r"E:\POLYDIM_EINSOF\kaggle_tpu_worker.py"

ACCOUNTS = [
    {
        "id": "account_1_ariel",
        "username": "tradingnewtech",
        "email": "ariel.garcia.traba@gmail.com",
        "token": "KGAT_79462dbbf2e5852a00dbaa614644ba83",
        "kernel_slug": "tradingnewtech/pmtp-v4-tpu-dispatch"
    },
    {
        "id": "account_2_agt",
        "username": "agt1973gmailcom",
        "email": "agt1973@gmail.com",
        "token": "KGAT_271bd7ced3760a5fb4e92eff0630ec9a",
        "kernel_slug": "agt1973gmailcom/pmtp-v4-tpu-dispatch"
    }
]

for acc in ACCOUNTS:
    kdir = os.path.join(BASE_DIR, acc["id"])
    os.makedirs(kdir, exist_ok=True)
    shutil.copy2(WORKER_SRC, os.path.join(kdir, "kaggle_tpu_worker.py"))
    
    meta = {
        "id": acc["kernel_slug"],
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
    with open(os.path.join(kdir, "kernel-metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

# Push kernel to Account 1 (tradingnewtech) if not already pushed
acc1 = ACCOUNTS[0]
env1 = os.environ.copy()
env1["KAGGLE_USERNAME"] = acc1["username"]
env1["KAGGLE_KEY"] = acc1["token"]
env1["KAGGLE_API_TOKEN"] = acc1["token"]

kdir1 = os.path.join(BASE_DIR, acc1["id"])
res = subprocess.run(["python", "-m", "kaggle", "kernels", "push", "-p", kdir1], env=env1, capture_output=True, text=True)
print("Push Account 1 (tradingnewtech):", res.stdout.strip(), res.stderr.strip())
