import os
import re
import fitz  # PyMuPDF
import sqlite3
from datetime import datetime

# 📂 Rutas
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_pdfs"
DB_PATH = "db/documentos.db"


# ------------------- DB -------------------
def init_db():
    """Inicializa la base de datos SQLite."""
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            tipo TEXT,
            cuit TEXT,
            proveedor TEXT,
            fecha_procesado TEXT
        )
    """)
    conn.commit()
    conn.close()


# ------------------- PDF -------------------
def extract_text_from_pdf(path):
    """Extrae texto de un PDF usando PyMuPDF."""
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def classify_document(text):
    """Clasifica el documento según palabras clave."""
    t = text.lower()
    if "factura" in t:
        return "facturas"
    elif "remito" in t:
        return "remitos"
    elif "nota de crédito" in t or "nota de credito" in t:
        return "notas_credito"
    elif "nota de débito" in t or "nota de debito" in t:
        return "notas_debito"
    elif "carta de porte" in t:
        return "cartas_porte"
    else:
        return "desconocido"


def extract_cuit(text):
    """Busca un CUIT en el texto (formato 00-00000000-0)."""
    match = re.search(r"\d{2}-\d{8}-\d", text)
    return match.group(0) if match else None


# ------------------- DB Save -------------------
def save_to_db(filename, tipo, cuit, proveedor=""):
    """Guarda metadatos en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documentos (filename, tipo, cuit, proveedor, fecha_procesado)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, tipo, cuit, proveedor, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ------------------- Procesamiento -------------------
def process_pdf(file_path):
    """Procesa un archivo PDF completo."""
    try:
        text = extract_text_from_pdf(file_path)
        tipo = classify_document(text)
        cuit = extract_cuit(text)

        # Crear carpeta destino
        dest_dir = os.path.join(OUTPUT_DIR, tipo)
        os.makedirs(dest_dir, exist_ok=True)

        # Mover archivo
        filename = os.path.basename(file_path)
        dest_path = os.path.join(dest_dir, filename)
        os.rename(file_path, dest_path)

        # Guardar metadatos
        save_to_db(filename, tipo, cuit)

        print(f"✅ {filename} → {tipo} | CUIT: {cuit if cuit else 'N/D'}")

    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")


# ------------------- Main -------------------
if __name__ == "__main__":
    print("🚀 Iniciando agente de PDFs...")
    init_db()

    if not os.path.exists(INPUT_DIR):
        print(f"⚠️ La carpeta {INPUT_DIR} no existe. Crea la carpeta y coloca PDFs.")
    else:
        files = os.listdir(INPUT_DIR)
        if not files:
            print(f"📂 No se encontraron archivos en {INPUT_DIR}")
        else:
            for file in files:
                path = os.path.join(INPUT_DIR, file)
                if file.lower().endswith(".pdf"):
                    process_pdf(path)
                else:
                    print(f"⚠️ {file} no es un PDF válido")

    print("🏁 Proceso finalizado.")
