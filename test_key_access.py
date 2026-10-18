import psycopg2
import json
import urllib.request
import urllib.error

conn = psycopg2.connect(
    dbname='polydim_active_db',
    host='localhost',
    port=5432,
    user='postgres',
    password='postgres'
)
cur = conn.cursor()

def get_key(name):
    cur.execute("SELECT value FROM active_vault WHERE key_name=%s AND category='api_key'", (name,))
    row = cur.fetchone()
    return row[0] if row else None

deepseek_key = get_key('DeepSeek')
openrouter_key = get_key('OpenRouter')
kimi_key = get_key('Kimi_Moonshot_Paga') or get_key('Kimi_Moonshot_Pool1')
conn.close()

print("KEYS_PRESENT:", {
    "DeepSeek": bool(deepseek_key),
    "OpenRouter": bool(openrouter_key),
    "Kimi": bool(kimi_key)
})
