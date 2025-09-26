import sqlite3

conn = sqlite3.connect('db/documentos.db')
cursor = conn.cursor()

print('BUSCANDO DOCUMENTOS CON NOTAS DE CRÉDITO/DÉBITO...')
print('=' * 60)
cursor.execute('''SELECT filename, tipo, proveedor, detalles_clasificacion FROM documentos WHERE LOWER(filename) LIKE '%nota%' OR LOWER(filename) LIKE '%credit%' OR LOWER(filename) LIKE '%debit%' OR LOWER(detalles_clasificacion) LIKE '%nota de crédito%' OR LOWER(detalles_clasificacion) LIKE '%nota de débito%' LIMIT 15''')
results = cursor.fetchall()
if results:
    for i, (filename, tipo, proveedor, detalles) in enumerate(results, 1):
        print(f'{i}. {filename}')
        print(f'   Tipo clasificado: {tipo}')
        print(f'   Proveedor: {proveedor if proveedor else "N/A"}')
        if detalles:
            print(f'   Detalles: {detalles[:100]}...')
        print()
else:
    print('No se encontraron documentos con notas específicas')

print('\nDOCUMENTOS CLASIFICADOS COMO DESCONOCIDO...')
print('=' * 50)
cursor.execute('''SELECT filename, tipo, proveedor, detalles_clasificacion FROM documentos WHERE tipo = 'desconocido' LIMIT 10''')
unknown_docs = cursor.fetchall()
for i, (filename, tipo, proveedor, detalles) in enumerate(unknown_docs, 1):
    print(f'{i}. {filename}')
    print(f'   Tipo: {tipo}')
    print(f'   Proveedor: {proveedor if proveedor else "N/A"}')
    if detalles:
        print(f'   Detalles: {detalles[:100]}...')
    print()

conn.close()
