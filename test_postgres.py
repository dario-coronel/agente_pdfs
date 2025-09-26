import psycopg2
from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB

try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM documentos;")
    count = cur.fetchone()[0]
    print(f"La tabla 'documentos' tiene {count} registros.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error al conectar o consultar la base de datos: {e}")
