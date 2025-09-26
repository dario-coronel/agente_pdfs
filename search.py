import psycopg2
import sys

DB_PATH = "db/documentos.db"


def search_documents(cuit=None, proveedor=None, tipo=None):
    from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB
    )
    cur = conn.cursor()

    query = "SELECT id, filename, tipo, cuit, proveedor, fecha_procesado FROM documentos WHERE 1=1"
    params = []

    if cuit:
        query += " AND cuit = ?"
    from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB

    if proveedor:
        query += " AND proveedor LIKE ?"
        params.append(f"%{proveedor}%")

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    if rows:
        print("📑 Resultados encontrados:")
        for r in rows:
            print(f"ID: {r[0]} | Archivo: {r[1]} | Tipo: {r[2]} | CUIT: {r[3]} | Proveedor: {r[4]} | Fecha: {r[5]}")
    else:
        print("⚠️ No se encontraron documentos con los criterios dados.")


if __name__ == "__main__":
    # Ejemplo de uso en CLI:
    # python search.py cuit 20-12345678-9
    # python search.py proveedor "Acme S.A."
    # python search.py tipo facturas

    if len(sys.argv) < 3:
        print("Uso:")
        print("  python search.py cuit <CUIT>")
        print("  python search.py proveedor <nombre>")
        print("  python search.py tipo <tipo_documento>")
    else:
        field = sys.argv[1].lower()
        value = sys.argv[2]

        if field == "cuit":
            search_documents(cuit=value)
        elif field == "proveedor":
            search_documents(proveedor=value)
        elif field == "tipo":
            search_documents(tipo=value)
        else:
            print(f"⚠️ Parámetro desconocido: {field}")
