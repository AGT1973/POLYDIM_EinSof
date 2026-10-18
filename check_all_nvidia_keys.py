import urllib.request
import urllib.error
import json

def check_all():
    keys = []
    with open("E:/Antigravity_multyMCP_Rust/.env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("NVIDIA_API_KEY_"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    keys.append((parts[0].strip(), parts[1].strip().strip('"').strip("'")))

    print(f"Probando las {len(keys)} claves de NVIDIA...")
    active_keys = []
    for name, key in keys:
        url = "https://integrate.api.nvidia.com/v1/models"
        headers = {"Authorization": f"Bearer {key}"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                print(f"[{name}] ACTIVA Y VALIDA (HTTP 200)")
                active_keys.append(name)
        except urllib.error.HTTPError as e:
            # print(f"[{name}] HTTP {e.code}")
            pass
        except Exception as e:
            pass
            
    print(f"\nResultado: {len(active_keys)} claves activas de {len(keys)} probadas.")

if __name__ == "__main__":
    check_all()
