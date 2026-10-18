import psycopg
import httpx

with psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1 port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT key_name, value FROM active_vault WHERE key_name LIKE 'Kimi%'")
        keys = dict(cur.fetchall())

client = httpx.Client(timeout=10.0)
for k, v in keys.items():
    r = client.get("https://api.moonshot.cn/v1/models", headers={"Authorization": f"Bearer {v}"})
    print(k, "models status:", r.status_code, r.text[:120])
    if r.status_code == 200:
        chat_r = client.post("https://api.moonshot.cn/v1/chat/completions",
                             headers={"Authorization": f"Bearer {v}"},
                             json={"model": "moonshot-v1-8k", "messages": [{"role": "user", "content": "ping"}], "max_tokens": 5})
        print(" -> Chat test:", chat_r.status_code, chat_r.text[:100])
