import urllib.request
import urllib.error
import json

def find_working_pair():
    keys = []
    with open("E:/Antigravity_multyMCP_Rust/.env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("NVIDIA_API_KEY_"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    keys.append((parts[0].strip(), parts[1].strip().strip('"').strip("'")))

    models = [
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "nv-mistralai/mistral-nemo-12b-instruct",
        "deepseek-ai/deepseek-v4.1-flash",
        "meta/llama-guard-4-12b"
    ]
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    for model in models:
        for name, key in keys:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    print(f"FOUND WORKING: {name} with model {model} -> {data['choices'][0]['message']['content']}")
                    return name, key, model
            except urllib.error.HTTPError as e:
                # print(f"{name} with {model}: {e.code}")
                pass
            except Exception as e:
                pass
    print("Ninguna clave de NVIDIA tiene créditos de inferencia activos.")
    return None

if __name__ == "__main__":
    find_working_pair()
