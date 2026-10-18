import urllib.request
import urllib.error
import json

def test():
    keys = []
    with open("E:/Antigravity_multyMCP_Rust/.env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("NVIDIA_API_KEY_"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    keys.append(parts[1].strip().strip('"').strip("'"))

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    for i, key in enumerate(keys[:5]):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        payload = {
            "model": "meta/llama-3.3-70b-instruct",
            "messages": [{"role": "user", "content": "Respond: OK"}],
            "max_tokens": 5
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"Key #{i+1} SUCCESS:", data["choices"][0]["message"]["content"])
                return
        except urllib.error.HTTPError as e:
            print(f"Key #{i+1} FAIL: {e.code} - {e.read().decode('utf-8')[:80]}")
        except Exception as e:
            print(f"Key #{i+1} ERROR: {e}")

if __name__ == "__main__":
    test()
