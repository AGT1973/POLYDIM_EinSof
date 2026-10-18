import os

bundle_dir = r"E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26250\brecha1\cuda_silicon_validation_bundle\cuda_silicon_bundle"

with open(os.path.join(bundle_dir, "kernel_cuda_v26250.cu.txt"), "r", encoding="utf-8") as f:
    cuda_code = f.read()

with open(os.path.join(bundle_dir, "polydim_triton_kernel_v26250.py"), "r", encoding="utf-8") as f:
    triton_code = f.read()

with open(os.path.join(bundle_dir, "test_adapter.py"), "r", encoding="utf-8") as f:
    adapter_code = f.read()

with open(os.path.join(bundle_dir, "harness_cuda_silicon_test.py"), "r", encoding="utf-8") as f:
    harness_code = f.read()

worker_script = f'''# ==============================================================================
# POLYDIM EINSOF — KAGGLE DUAL-GPU TESLA T4 SILICON WORKER (BRECHA 1)
# ==============================================================================
import os
import sys
import subprocess
import shutil
import glob
from pathlib import Path

WORKDIR = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path(".").resolve()
os.chdir(WORKDIR)

print("=" * 80)
print("POLYDIM EINSOF — KAGGLE SILICON DISPATCH WORKER V26250")
print("=" * 80)

# 1. Materializar archivos en el contenedor de silicio
print("[*] Desplegando artefactos de silicio en:", WORKDIR)

with open(WORKDIR / "kernel_cuda_v26250.cu.txt", "w", encoding="utf-8") as f:
    f.write({repr(cuda_code)})

with open(WORKDIR / "polydim_triton_kernel_v26250.py", "w", encoding="utf-8") as f:
    f.write({repr(triton_code)})

with open(WORKDIR / "test_adapter.py", "w", encoding="utf-8") as f:
    f.write({repr(adapter_code)})

with open(WORKDIR / "harness_cuda_silicon_test.py", "w", encoding="utf-8") as f:
    f.write({repr(harness_code)})

print("[*] Archivos desplegados con éxito.")

# 2. Ejecutar el arnés de certificación en silicio
cmd = [
    sys.executable, "harness_cuda_silicon_test.py",
    "--cuda-source", "kernel_cuda_v26250.cu.txt",
    "--triton-source", "polydim_triton_kernel_v26250.py",
    "--adapter", "test_adapter.py",
    "--arch", "auto",
    "--work-dir", str(WORKDIR),
    "--log-dir", str(WORKDIR / "_HISTORICO/silicio_logs")
]

print("\\n[+] Ejecutando arnés de validación en silicio:")
print("$", " ".join(cmd))
res = subprocess.run(cmd, text=True)
print(f"[*] Arnés finalizado con Exit Code: {{res.returncode}}")

# 3. Copiar logs generados al directorio raíz de salida para descarga inmediata por Kaggle CLI
log_files = glob.glob(str(WORKDIR / "_HISTORICO/silicio_logs/*.log"))
for lf in log_files:
    dest = WORKDIR / Path(lf).name
    shutil.copy2(lf, dest)
    print(f"[*] Log copiado a salida pública de Kaggle: {{dest.name}}")

sys.exit(res.returncode)
'''

with open(r"E:\POLYDIM_EINSOF\kaggle_cuda_worker.py", "w", encoding="utf-8") as f:
    f.write(worker_script)

print("GENERATED kaggle_cuda_worker.py, SIZE:", os.path.getsize(r"E:\POLYDIM_EINSOF\kaggle_cuda_worker.py"))
