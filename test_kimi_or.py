import psycopg, httpx

with psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1 port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM active_vault WHERE key_name = 'OpenRouter'")
        or_key = cur.fetchone()[0]

for m in ["moonshotai/kimi-k3", "moonshotai/kimi-k2.7-code", "moonshotai/kimi-k2-thinking"]:
    r = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {or_key}", "HTTP-Referer": "https://polydim.org", "X-Title": "POLYDIM"},
        json={"model": m, "messages": [{"role": "user", "content": "Responde solo: OK"}], "max_tokens": 10},
        timeout=20.0
    )
    print(m, "-> status:", r.status_code, "response:", r.text[:80])
