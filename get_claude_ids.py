import psycopg, httpx

with psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1 port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM active_vault WHERE key_name = 'OpenRouter' AND category = 'api_key'")
        or_key = cur.fetchone()[0]

r = httpx.get("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {or_key}"})
data = r.json().get("data", [])
cl_models = [m["id"] for m in data if "claude" in m["id"].lower()]
print("Claude exact IDs:", cl_models[:8])
