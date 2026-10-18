import psycopg
import httpx

with psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1 port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM active_vault WHERE key_name = 'OpenRouter'")
        or_key = cur.fetchone()[0]

r = httpx.get("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {or_key}"})
data = r.json().get("data", [])
models = [m["id"] for m in data if any(x in m["id"].lower() for x in ["kimi", "moonshot", "claude", "qwen", "deepseek", "gemini"])]
print("Relevant OpenRouter models count:", len(models))
for m in sorted(models):
    if any(k in m for k in ["moonshot", "kimi", "claude-3.5", "claude-3-opus", "qwen-2.5-72b", "deepseek-r1", "deepseek-v3"]):
        print(" -", m)
