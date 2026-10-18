import psycopg, httpx

with psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1 port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM active_vault WHERE key_name = 'OpenRouter' AND category = 'api_key'")
        or_key = cur.fetchone()[0]

print(f"OpenRouter actual key prefix: {or_key[:15]}...")

headers = {
    "Authorization": f"Bearer {or_key.strip()}",
    "HTTP-Referer": "https://polydim.org",
    "X-Title": "POLYDIM SOTA",
    "Content-Type": "application/json"
}

for m in ["moonshotai/kimi-k3", "anthropic/claude-3.5-sonnet", "qwen/qwen-2.5-72b-instruct"]:
    r = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={"model": m, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 5},
        timeout=25.0
    )
    print(f"{m} -> Status: {r.status_code}, Response: {r.text[:120]}")
