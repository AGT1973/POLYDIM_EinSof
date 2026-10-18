import psycopg

conn = psycopg.connect('dbname=polydim_vec_db user=postgres host=localhost port=5432')
with conn.cursor() as cur:
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'session_context';")
    for r in cur.fetchall():
        print(r)
conn.close()
