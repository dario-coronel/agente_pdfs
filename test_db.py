import psycopg2
import os
''

print("🔍 Diagnóstico de la base de datos")

    try:
        from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DB
        )
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Tablas encontradas: {tables}")
        
        # Verificar estructura de la tabla documentos
        if ('documentos',) in tables:
            cursor.execute("PRAGMA table_info(documentos);")
            columns = cursor.fetchall()
            print(f"🏗️ Columnas de documentos: {columns}")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM documentos;")
            count = cursor.fetchone()[0]
            print(f"📈 Registros en documentos: {count}")
        
        conn.close()
        print("✅ Conexión exitosa")
        
    except Exception as e:
        print(f"❌ Error: {e}")
