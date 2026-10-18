import urllib.request
import json

def get_models():
    key = None
    with open("E:/Antigravity_multyMCP_Rust/.env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("NVIDIA_API_KEY_1="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

    url = "https://integrate.api.nvidia.com/v1/models"
    headers = {"Authorization": f"Bearer {key}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m["id"] for m in data.get("data", [])]
            print(f"Total available models: {len(models)}")
            for m in models:
                if any(x in m.lower() for x in ["llama", "deepseek", "qwen", "mistral"]):
                    print(" -", m)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    get_models()
