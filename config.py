"""
Configuración centralizada del Agente PDF Classifier
"""
import os

# 📂 Rutas del proyecto
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_pdfs" 
DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "documentos.db")

# 🔍 Configuración de clasificación
DOCUMENT_TYPES = {
    "facturas": ["factura", "invoice", "fact", "fac"],
    "remitos": ["remito", "delivery note", "rem"],
    "notas_credito": ["nota de crédito", "nota de credito", "credit note", "nc"],
    "notas_debito": ["nota de débito", "nota de debito", "debit note", "nd"],
    "cartas_porte": ["carta de porte", "waybill", "cp"],
    "recibos": ["recibo", "receipt", "rec"],
    "ordenes_compra": ["orden de compra", "purchase order", "oc"],
    "contratos": ["contrato", "contract", "convenio"]
}

# 📋 Patrones de extracción
CUIT_PATTERN = r"\d{2}-\d{8}-\d"
DATE_PATTERNS = [
    r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}",
    r"\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}",
    r"\d{1,2}\s+de\s+\w+\s+de\s+\d{4}"
]
AMOUNT_PATTERN = r"\$\s*[\d,]+\.?\d*"

# ⚙️ Configuración de procesamiento
MAX_FILE_SIZE_MB = 50
SUPPORTED_EXTENSIONS = [".pdf"]
CONFIDENCE_THRESHOLD = 0.7

# 📊 Configuración de base de datos
DB_SCHEMA = {
    "documentos": """
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            tipo TEXT NOT NULL,
            cuit TEXT,
            proveedor TEXT,
            fecha_documento TEXT,
            monto TEXT,
            confidence REAL,
            fecha_procesado TEXT NOT NULL
        )
    """
}

# 🔧 Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "logs/agente_pdfs.log"
}

# 🌐 Configuración de exportación
EXPORT_FORMATS = ["csv", "json", "excel"]
