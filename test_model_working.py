import urllib.request
import urllib.error
import json

def test_models():
    key = None
    with open("E:/Antigravity_multyMCP_Rust/.env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("NVIDIA_API_KEY_1="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

    candidates = [
        "meta/llama-3.2-11b-vision-instruct",
        "deepseek-ai/deepseek-coder-6.7b-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "mistralai/mixtral-8x22b-v0.1"
    ]
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }

    for model in candidates:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["choices"][0]["message"]["content"].strip()
                print(f"[MODEL OK] {model}: '{reply}'")
                return model
        except urllib.error.HTTPError as e:
            print(f"[MODEL FAIL] {model}: HTTP {e.code}")
        except Exception as e:
            print(f"[MODEL FAIL] {model}: {e}")
    return None

if __name__ == "__main__":
    test_models()
