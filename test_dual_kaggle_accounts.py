import os
import subprocess

ACCOUNTS = [
    {
        "name": "Account_1_Ariel (tradingnewtech)",
        "email": "ariel.garcia.traba@gmail.com",
        "username": "tradingnewtech",
        "token": "KGAT_79462dbbf2e5852a00dbaa614644ba83"
    },
    {
        "name": "Account_2_AGT (agt1973gmailcom)",
        "email": "agt1973@gmail.com",
        "username": "agt1973gmailcom",
        "token": "KGAT_271bd7ced3760a5fb4e92eff0630ec9a"
    }
]

for acc in ACCOUNTS:
    print("=" * 60)
    print(f"PROBANDO CUENTA: {acc['name']} ({acc['email']})")
    env = os.environ.copy()
    env["KAGGLE_USERNAME"] = acc["username"]
    env["KAGGLE_KEY"] = acc["token"]
    env["KAGGLE_API_TOKEN"] = acc["token"]
    
    # List owned kernels
    res = subprocess.run(["python", "-m", "kaggle", "kernels", "list", "--mine"], env=env, capture_output=True, text=True)
    print("STDOUT:")
    print(res.stdout.strip())
    if res.stderr.strip():
        print("STDERR:", res.stderr.strip())
