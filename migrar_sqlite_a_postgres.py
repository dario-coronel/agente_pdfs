import sqlite3
import psycopg2

# Configuración de conexión
SQLITE_DB = 'db/documentos.db'
PG_HOST = 'localhost'
PG_PORT = 5432
PG_USER = 'postgres'
PG_PASSWORD = 'Suecia2372'
PG_DB = 'postgres'

# Conexión a SQLite
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_cur = sqlite_conn.cursor()
sqlite_cur.execute('SELECT * FROM documentos')
rows = sqlite_cur.fetchall()
columns = [desc[0] for desc in sqlite_cur.description]

# Conexión a PostgreSQL
pg_conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    user=PG_USER,
    password=PG_PASSWORD,
    dbname=PG_DB
)
pg_cur = pg_conn.cursor()

# Insertar datos en PostgreSQL
for row in rows:
    placeholders = ','.join(['%s'] * len(row))
    sql = f"INSERT INTO documentos ({','.join(columns)}) VALUES ({placeholders})"
    pg_cur.execute(sql, row)

pg_conn.commit()

print(f"Migrados {len(rows)} registros de documentos.")

# Cerrar conexiones
sqlite_conn.close()
pg_cur.close()
pg_conn.close()
