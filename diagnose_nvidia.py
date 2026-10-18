import urllib.request
import urllib.error
import json

def diagnose():
    keys = []
    with open("E:/Antigravity_multyMCP_Rust/.env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("NVIDIA_API_KEY_"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    keys.append((parts[0].strip(), parts[1].strip().strip('"').strip("'")))

    for name, key in keys[:3]:
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        payload = {
            "model": "nvidia/llama-3.1-nemotron-70b-instruct",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"[{name}] SUCCESS:", resp.read().decode("utf-8")[:100])
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            print(f"[{name}] HTTP ERROR {e.code}: {err_body}")
        except Exception as e:
            print(f"[{name}] OTHER ERROR: {e}")

if __name__ == "__main__":
    diagnose()
