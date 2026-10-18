import os
import sys
import subprocess
import json
import datetime
import urllib.request

sys.path.append(r"E:\Mantenimiento")
try:
    from agent_vault_pg import set_vault_value
    PG_AVAILABLE = True
except Exception:
    PG_AVAILABLE = False

WORKSPACE = r"E:\POLYDIM_EINSOF"
OUTPUT_BASE = os.path.join(WORKSPACE, "TPU_DISPATCH_OUTPUT")
LOG_FILE = os.path.join(WORKSPACE, "kaggle_tpu_poller.log")

KAGGLE_ACCOUNTS = [
    {
        "id": "account_1_ariel",
        "username": "tradingnewtech",
        "email": "ariel.garcia.traba@gmail.com",
        "token": "KGAT_79462dbbf2e5852a00dbaa614644ba83",
        "kernels": ["tradingnewtech/pmtp-v4-tpu-dispatch"]
    },
    {
        "id": "account_2_agt",
        "username": "agt1973gmailcom",
        "email": "agt1973@gmail.com",
        "token": "KGAT_271bd7ced3760a5fb4e92eff0630ec9a",
        "kernels": ["agt1973gmailcom/pmtp-v4-tpu-dispatch", "agt1973gmailcom/polydim-tpu-v3-8-bench"]
    },
    {
        "id": "account_3_polydimcla",
        "username": "polydimcla",
        "email": "polydim.cla@gmail.com",
        "token": "KGAT_4ef61a6e17016965ff828a3615de510c",
        "kernels": ["polydimcla/pmtp-v4-tpu-dispatch"]
    },
    {
        "id": "account_4_cursos",
        "username": "cursosagt",
        "email": "cursos.agt@gmail.com",
        "token": "KGAT_4a6abb07c0e2625db84bb7db11793417",
        "kernels": ["cursosagt/pmtp-v4-tpu-dispatch"]
    }
]

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def make_env(acc):
    env = os.environ.copy()
    env["KAGGLE_USERNAME"] = acc["username"]
    env["KAGGLE_KEY"] = acc["token"]
    env["KAGGLE_API_TOKEN"] = acc["token"]
    return env

def check_status(acc, kernel_slug):
    cmd = ["python", "-m", "kaggle", "kernels", "status", kernel_slug]
    res = subprocess.run(cmd, cwd=WORKSPACE, env=make_env(acc), capture_output=True, text=True)
    out = (res.stdout + " " + res.stderr).strip()
    return out

def fetch_output(acc, kernel_slug):
    safe_slug = kernel_slug.replace("/", "_")
    out_dir = os.path.join(OUTPUT_BASE, safe_slug)
    os.makedirs(out_dir, exist_ok=True)
    cmd = ["python", "-m", "kaggle", "kernels", "output", kernel_slug, "-p", out_dir]
    res = subprocess.run(cmd, cwd=WORKSPACE, env=make_env(acc), capture_output=True, text=True)
    log(f"Fetch Output [{kernel_slug}]: {res.stdout.strip()} {res.stderr.strip()}")
    
    for fname in os.listdir(out_dir):
        fpath = os.path.join(out_dir, fname)
        if fname.endswith(".json") or fname.endswith(".log"):
            log(f"  -> File [{kernel_slug}]: {fname} ({os.path.getsize(fpath)} bytes)")
            if fname.endswith(".json"):
                with open(fpath, "r", encoding="utf-8") as jf:
                    try:
                        data = json.load(jf)
                        log(f"  -> JSON [{kernel_slug}]: {json.dumps(data)}")
                        if data.get("is_tpu") is True and data.get("exit_code") == 0:
                            log(f">>> SUCCESS: PHYSICAL TPU CERTIFICATION ACHIEVED IN {kernel_slug}! <<<")
                            if PG_AVAILABLE:
                                set_vault_value(
                                    category="tpu_certification",
                                    key_name=kernel_slug,
                                    value=json.dumps(data),
                                    notes=f"Certified TPU v3-8 on account {acc['email']}",
                                    use_vec_db=False
                                )
                                set_vault_value(
                                    category="tpu_certification",
                                    key_name=kernel_slug,
                                    value=json.dumps(data),
                                    notes=f"Certified TPU v3-8 on account {acc['email']}",
                                    use_vec_db=True
                                )
                            return True, data
                    except Exception as err:
                        log(f"  -> JSON error in {fname}: {err}")
    return False, None

def ping_aladin():
    try:
        req = urllib.request.urlopen("http://192.168.100.21:11434/api/tags", timeout=2)
        if req.status == 200:
            return "ALADIN_ONLINE"
    except Exception:
        return "ALADIN_UNREACHABLE"
    return "ALADIN_UNKNOWN"

def main():
    log("=== WATCHDOG 4-CUENTAS KAGGLE TPU & CLUSTER DUAL ===")
    aladin_st = ping_aladin()
    log(f"Nodo Aladin (192.168.100.21): {aladin_st}")
    
    for acc in KAGGLE_ACCOUNTS:
        for kslug in acc["kernels"]:
            st = check_status(acc, kslug)
            log(f"[{acc['username']}] {kslug} -> {st}")
            if "COMPLETE" in st:
                ok, data = fetch_output(acc, kslug)
                if ok:
                    log(f"VALOR EXACTO CAPTURADO DE {kslug}: {json.dumps(data)}")

if __name__ == "__main__":
    main()
