import os
import subprocess

# Probe the username for the 3rd Kaggle account
env = os.environ.copy()
env["KAGGLE_USERNAME"] = "polydimcla"
env["KAGGLE_KEY"] = "KGAT_4ef61a6e17016965ff828a3615de510c"

# Try listing kernels to discover the actual username
res = subprocess.run(["python", "-m", "kaggle", "kernels", "list", "--mine"], env=env, capture_output=True, text=True)
print("STDOUT:", res.stdout.strip()[:500])
if res.stderr.strip():
    print("STDERR:", res.stderr.strip()[:500])
