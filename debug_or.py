import psycopg, httpx

with psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1 port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT key_name, value FROM active_vault WHERE key_name = 'OpenRouter'")
        name, val = cur.fetchone()
        print(f"Key name: {name}, Length: {len(val)}, Prefix: {val[:12]}...")

headers = {
    "Authorization": f"Bearer {val.strip()}",
    "HTTP-Referer": "https://polydim.org",
    "X-Title": "POLYDIM SOTA",
    "Content-Type": "application/json"
}

r = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json={
        "model": "moonshotai/kimi-k3",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 10
    },
    timeout=20.0
)
print("Status:", r.status_code)
print("Response:", r.text[:200])
