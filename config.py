"""
Configuración centralizada del Agente PDF Classifier
"""
import os

# 📂 Rutas del proyecto
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_pdfs" 
DB_DIR = "db"

# Configuración para PostgreSQL
PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASSWORD = "Suecia2372"
PG_DB = "postgres"

# 🔍 Configuración de clasificación
DOCUMENT_TYPES = {
    "facturas": ["factura", "invoice", "fact", "fac", "bill"],
    "remitos": ["remito", "delivery note", "rem", "guía", "guia"],
    "notas_credito": ["nota de crédito", "nota de credito", "credit note"],  # Removido "nc" genérico
    "notas_debito": ["nota de débito", "nota de debito", "debit note"],     # Removido "nd" genérico
    "cartas_porte": ["carta de porte", "waybill", "cp", "porte", "transporte", "flete"],
    "liquidaciones_granos": ["liquidación primaria", "liquidación de granos", "liquidacion", "granos", "cereales", "soja", "trigo", "maíz", "maiz", "girasol", "sorgo", "settlement", "grain settlement"],
    "cot": ["cot", "certificado de transferencia", "certificado", "transferencia", "certificate of transfer", "transferencia de granos", "transfer certificate"],
    "ctg": ["ctg", "carta de crédito", "carta de credito", "certificado de depósito", "certificado de deposito", "warrant", "storage certificate"],
    "pesajes": ["pesaje", "peso", "báscula", "bascula", "balanza", "weigh", "weight", "scale", "kg", "toneladas"],
    "contratos_granos": ["contrato", "contract", "convenio", "acuerdo", "compraventa", "granos", "cereales"],
    "transferencias": ["transferencia bancaria", "transferencia", "transfer", "wire transfer", "giro", "envío de dinero", "remesa"],
    "ordenes_pago": ["orden de pago", "payment order", "op", "orden pago", "autorización de pago", "payment authorization"],
    "recibos": ["recibo", "receipt", "rec", "comprobante"],
    "ordenes_compra": ["orden de compra", "purchase order", "oc"],
    "contratos": ["contrato", "contract", "convenio", "acuerdo"]
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
            proveedor_id TEXT,
            fecha_documento TEXT,
            monto TEXT,
            confidence REAL,
            fecha_procesado TEXT NOT NULL,
            detalles_clasificacion TEXT,
            metodos_usados TEXT
        )
    """
}

# 🔧 Configuración de logging avanzada
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "logs/agente_pdfs.log",
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
    "console_level": "INFO",
    "file_level": "DEBUG",
    "enable_structured_logging": True,
    "log_performance": True,
    "log_classification_details": True
}

# 🧠 Configuración de clasificación inteligente
INTELLIGENT_CLASSIFICATION_CONFIG = {
    "enable_ml": True,
    "enable_layout_analysis": True,
    "enable_supplier_detection": True,
    "classification_weights": {
        "keyword": 0.25,
        "regex": 0.30,
        "ml": 0.20,
        "layout": 0.15,
        "supplier": 0.10
    },
    "confidence_thresholds": {
        "min_confidence": 0.4,
        "high_confidence": 0.8,
        "consensus_threshold": 0.6
    },
    "consensus_requirements": {
        "high_confidence_methods": 2,
        "medium_confidence_methods": 1,
        "supplier_boost": 0.15
    }
}

# 📊 Configuración de Machine Learning
ML_CONFIG = {
    "training_data_size": 1000,
    "test_size": 0.2,
    "random_state": 42,
    "vectorizer_params": {
        "max_features": 5000,
        "stop_words": "english",
        "ngram_range": (1, 2)
    },
    "classifier_params": {
        "alpha": 1.0,
        "fit_prior": True
    },
    "retrain_threshold": 100  # Reentrenar cada N documentos nuevos
}

# 🔍 Configuración de validación PDF
PDF_VALIDATION_CONFIG = {
    "max_file_size": 50 * 1024 * 1024,  # 50 MB
    "min_file_size": 1024,  # 1 KB
    "allowed_extensions": [".pdf"],
    "check_password_protection": True,
    "check_text_extractability": True,
    "check_page_count": True,
    "max_pages": 500,
    "min_pages": 1,
    "check_file_integrity": True,
    "quarantine_invalid_files": True
}

# 📋 Configuración de layout analysis
LAYOUT_CONFIG = {
    "min_table_rows": 3,
    "min_table_cols": 2,
    "font_size_threshold": 12,
    "line_spacing_threshold": 1.2,
    "margin_threshold": 0.1,
    "header_detection": True,
    "footer_detection": True,
    "signature_detection": True
}

# 📤 Configuración de exportación
EXPORT_CONFIG = {
    "formats": ["csv", "json", "excel", "xml"],
    "default_format": "csv",
    "include_classification_details": True,
    "include_method_results": True,
    "include_confidence_scores": True,
    "excel_sheets": {
        "summary": "Resumen",
        "detailed": "Detallado", 
        "methods": "Métodos",
        "suppliers": "Proveedores"
    },
    "csv_separator": ",",
    "csv_encoding": "utf-8-sig"
}

# ⚡ Configuración de rendimiento
PERFORMANCE_CONFIG = {
    "batch_size": 10,
    "max_workers": 4,
    "enable_parallel_processing": True,
    "memory_limit": 1024 * 1024 * 1024,  # 1 GB
    "timeout_per_document": 300,  # 5 minutos
    "cache_extracted_text": True,
    "cache_classification_results": False
}

# 🌐 Configuración de la interfaz CLI
CLI_CONFIG = {
    "show_progress_bar": True,
    "colorful_output": True,
    "interactive_mode": True,
    "confirm_actions": True,
    "detailed_help": True,
    "auto_suggest": True
}

# 📈 Configuración de métricas y estadísticas
METRICS_CONFIG = {
    "enable_performance_tracking": True,
    "track_processing_time": True,
    "track_accuracy": True,
    "generate_reports": True,
    "report_frequency": "daily",
    "keep_history_days": 30
}

# 🛠️ Funciones de configuración
import os
import json
from typing import Dict, Any


def load_custom_config(config_file: str = "config/custom_config.json") -> Dict[str, Any]:
    """
    Carga configuración personalizada desde archivo JSON
    
    Args:
        config_file: Ruta al archivo de configuración
        
    Returns:
        Diccionario con configuración personalizada
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando configuración personalizada: {e}")
    return {}


def save_config_template(config_file: str = "config/config_template.json"):
    """
    Guarda plantilla de configuración para personalización
    
    Args:
        config_file: Ruta donde guardar la plantilla
    """
    template = {
        "logging": LOGGING_CONFIG,
        "classification": INTELLIGENT_CLASSIFICATION_CONFIG,
        "ml": ML_CONFIG,
        "validation": PDF_VALIDATION_CONFIG,
        "layout": LAYOUT_CONFIG,
        "export": EXPORT_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "cli": CLI_CONFIG,
        "metrics": METRICS_CONFIG
    }
    
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"Plantilla de configuración guardada en: {config_file}")


def get_config_value(section: str, key: str, default_value: Any = None) -> Any:
    """
    Obtiene un valor de configuración con fallback a valor por defecto
    
    Args:
        section: Sección de configuración
        key: Clave específica
        default_value: Valor por defecto
        
    Returns:
        Valor de configuración o valor por defecto
    """
    config_map = {
        "logging": LOGGING_CONFIG,
        "classification": INTELLIGENT_CLASSIFICATION_CONFIG,
        "ml": ML_CONFIG,
        "validation": PDF_VALIDATION_CONFIG,
        "layout": LAYOUT_CONFIG,
        "export": EXPORT_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "cli": CLI_CONFIG,
        "metrics": METRICS_CONFIG
    }
    
    section_config = config_map.get(section, {})
    return section_config.get(key, default_value)


def update_config_value(section: str, key: str, value: Any):
    """
    Actualiza un valor de configuración en tiempo de ejecución
    
    Args:
        section: Sección de configuración
        key: Clave específica
        value: Nuevo valor
    """
    config_map = {
        "logging": LOGGING_CONFIG,
        "classification": INTELLIGENT_CLASSIFICATION_CONFIG,
        "ml": ML_CONFIG,
        "validation": PDF_VALIDATION_CONFIG,
        "layout": LAYOUT_CONFIG,
        "export": EXPORT_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "cli": CLI_CONFIG,
        "metrics": METRICS_CONFIG
    }
    
    if section in config_map:
        config_map[section][key] = value
        print(f"Configuración actualizada: {section}.{key} = {value}")
    else:
        print(f"Sección de configuración no encontrada: {section}")


def validate_config() -> bool:
    """
    Valida la configuración actual
    
    Returns:
        True si la configuración es válida
    """
    errors = []
    
    # Validar directorios
    required_dirs = [INPUT_DIR, OUTPUT_DIR, os.path.dirname(DB_PATH)]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                errors.append(f"No se puede crear directorio: {dir_path} - {e}")
    
    # Validar configuración de pesos
    weights = INTELLIGENT_CLASSIFICATION_CONFIG["classification_weights"]
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 0.1:
        errors.append(f"Los pesos de clasificación deben sumar 1.0 (actual: {total_weight})")
    
    # Validar umbrales de confianza
    thresholds = INTELLIGENT_CLASSIFICATION_CONFIG["confidence_thresholds"]
    if thresholds["min_confidence"] >= thresholds["high_confidence"]:
        errors.append("min_confidence debe ser menor que high_confidence")
    
    # Validar configuración de archivos
    max_size = PDF_VALIDATION_CONFIG["max_file_size"]
    min_size = PDF_VALIDATION_CONFIG["min_file_size"]
    if min_size >= max_size:
        errors.append("min_file_size debe ser menor que max_file_size")
    
    if errors:
        print("Errores de configuración encontrados:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


# Validar configuración al importar el módulo
if __name__ == "__main__":
    if validate_config():
        print("✅ Configuración validada correctamente")
        save_config_template()
    else:
        print("❌ Errores en la configuración")
