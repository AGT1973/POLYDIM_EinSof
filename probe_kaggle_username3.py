import os
import subprocess
import json

# Try multiple candidate usernames for polydim.cla@gmail.com
candidates = ["polydimcla", "polydimclagmailcom", "polydimc", "polydim-cla"]

for uname in candidates:
    env = os.environ.copy()
    env["KAGGLE_USERNAME"] = uname
    env["KAGGLE_KEY"] = "KGAT_4ef61a6e17016965ff828a3615de510c"
    
    # Use datasets list as a lightweight auth check
    res = subprocess.run(["python", "-m", "kaggle", "kernels", "list", "--mine", "--page-size", "1"],
                         env=env, capture_output=True, text=True, timeout=15)
    out = (res.stdout + res.stderr).strip()
    print(f"Username '{uname}': {out[:200]}")
    print("---")
