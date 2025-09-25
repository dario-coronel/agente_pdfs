"""
Sistema de logging avanzado para el agente PDF
"""
import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from config import LOGGING_CONFIG


class StructuredFormatter(logging.Formatter):
    """
    Formateador que genera logs estructurados en formato JSON
    """
    
    def format(self, record):
        """Formatea el registro como JSON estructurado"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregar información adicional si está disponible
        if hasattr(record, 'document_id'):
            log_entry["document_id"] = record.document_id
        
        if hasattr(record, 'document_type'):
            log_entry["document_type"] = record.document_type
        
        if hasattr(record, 'confidence'):
            log_entry["confidence"] = record.confidence
        
        if hasattr(record, 'processing_time'):
            log_entry["processing_time"] = record.processing_time
        
        if hasattr(record, 'method_results'):
            log_entry["method_results"] = record.method_results
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Formateador con colores para la consola
    """
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cian
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Formatea el registro con colores"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formatear el mensaje básico
        formatted = super().format(record)
        
        # Agregar información adicional si está disponible
        extras = []
        
        if hasattr(record, 'document_type'):
            extras.append(f"tipo={record.document_type}")
        
        if hasattr(record, 'confidence'):
            extras.append(f"conf={record.confidence:.3f}")
        
        if hasattr(record, 'processing_time'):
            extras.append(f"tiempo={record.processing_time:.2f}s")
        
        if extras:
            formatted += f" [{', '.join(extras)}]"
        
        return f"{color}{formatted}{reset}"


class PerformanceLogger:
    """
    Logger especializado para métricas de rendimiento
    """
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
        self.start_times = {}
    
    def start_timer(self, operation_id: str):
        """Inicia un cronómetro para una operación"""
        self.start_times[operation_id] = datetime.now()
    
    def end_timer(self, operation_id: str, **extra_info):
        """Termina un cronómetro y registra el tiempo transcurrido"""
        if operation_id in self.start_times:
            start_time = self.start_times[operation_id]
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            log_data = {
                "operation": operation_id,
                "duration": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                **extra_info
            }
            
            self.logger.info(f"Operación completada: {operation_id}", extra=log_data)
            del self.start_times[operation_id]
            return duration
        else:
            self.logger.warning(f"No se encontró cronómetro para: {operation_id}")
            return 0


class ClassificationLogger:
    """
    Logger especializado para resultados de clasificación
    """
    
    def __init__(self, logger_name: str = "classification"):
        self.logger = logging.getLogger(logger_name)
    
    def log_classification_result(self, document_path: str, classification_result: Dict):
        """
        Registra el resultado completo de una clasificación
        
        Args:
            document_path: Ruta del documento clasificado
            classification_result: Resultado completo de la clasificación inteligente
        """
        log_data = {
            "document_path": document_path,
            "final_classification": classification_result.get("final_classification"),
            "final_confidence": classification_result.get("final_confidence"),
            "method_results": classification_result.get("method_results", {}),
            "consensus_analysis": classification_result.get("consensus_analysis", {}),
            "supplier_info": classification_result.get("supplier_info", {}),
            "decision_reasoning": classification_result.get("decision_details", {}).get("final_reasoning", "")
        }
        
        self.logger.info(
            f"Clasificación: {os.path.basename(document_path)} -> "
            f"{classification_result.get('final_classification')} "
            f"(confianza: {classification_result.get('final_confidence', 0):.3f})",
            extra=log_data
        )
    
    def log_method_performance(self, method_name: str, processing_time: float, 
                             success: bool, error_msg: str = None):
        """
        Registra el rendimiento de un método específico de clasificación
        
        Args:
            method_name: Nombre del método (keyword, regex, ml, etc.)
            processing_time: Tiempo de procesamiento en segundos
            success: Si el método se ejecutó exitosamente
            error_msg: Mensaje de error si hubo falla
        """
        log_data = {
            "method": method_name,
            "processing_time": processing_time,
            "success": success,
            "error": error_msg
        }
        
        level = logging.INFO if success else logging.ERROR
        message = f"Método {method_name}: {'exitoso' if success else 'fallido'} ({processing_time:.3f}s)"
        
        self.logger.log(level, message, extra=log_data)


def setup_advanced_logging():
    """
    Configura el sistema de logging avanzado con múltiples handlers
    """
    # Crear directorio de logs
    log_dir = Path(LOGGING_CONFIG["log_file"]).parent
    log_dir.mkdir(exist_ok=True)
    
    # Configuración base
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # 1. Handler para archivo principal con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        LOGGING_CONFIG["log_file"],
        maxBytes=LOGGING_CONFIG["max_file_size"],
        backupCount=LOGGING_CONFIG["backup_count"],
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, LOGGING_CONFIG["file_level"]))
    
    if LOGGING_CONFIG.get("enable_structured_logging", False):
        file_handler.setFormatter(StructuredFormatter())
    else:
        file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG["format"]))
    
    root_logger.addHandler(file_handler)
    
    # 2. Handler para consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOGGING_CONFIG["console_level"]))
    console_handler.setFormatter(ColoredConsoleFormatter(LOGGING_CONFIG["format"]))
    
    root_logger.addHandler(console_handler)
    
    # 3. Handler separado para errores
    error_file = log_dir / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=LOGGING_CONFIG["max_file_size"],
        backupCount=2,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOGGING_CONFIG["format"]))
    
    root_logger.addHandler(error_handler)
    
    # 4. Handler para rendimiento (si está habilitado)
    if LOGGING_CONFIG.get("log_performance", False):
        performance_file = log_dir / "performance.log"
        performance_handler = logging.handlers.RotatingFileHandler(
            performance_file,
            maxBytes=LOGGING_CONFIG["max_file_size"],
            backupCount=3,
            encoding='utf-8'
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(StructuredFormatter())
        
        # Aplicar solo al logger de performance
        perf_logger = logging.getLogger("performance")
        perf_logger.addHandler(performance_handler)
        perf_logger.setLevel(logging.INFO)
    
    # 5. Handler para clasificación detallada (si está habilitado)
    if LOGGING_CONFIG.get("log_classification_details", False):
        classification_file = log_dir / "classification.log"
        classification_handler = logging.handlers.RotatingFileHandler(
            classification_file,
            maxBytes=LOGGING_CONFIG["max_file_size"],
            backupCount=5,
            encoding='utf-8'
        )
        classification_handler.setLevel(logging.INFO)
        classification_handler.setFormatter(StructuredFormatter())
        
        # Aplicar solo al logger de clasificación
        class_logger = logging.getLogger("classification")
        class_logger.addHandler(classification_handler)
        class_logger.setLevel(logging.INFO)
    
    # Log de inicio del sistema
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging avanzado configurado correctamente")
    logger.info(f"Logs principales: {LOGGING_CONFIG['log_file']}")
    logger.info(f"Logs de errores: {error_file}")
    
    if LOGGING_CONFIG.get("log_performance", False):
        logger.info(f"Logs de rendimiento: {performance_file}")
    
    if LOGGING_CONFIG.get("log_classification_details", False):
        logger.info(f"Logs de clasificación: {classification_file}")


def get_logger(name: str, logger_type: str = "standard") -> logging.Logger:
    """
    Obtiene un logger configurado según el tipo especificado
    
    Args:
        name: Nombre del logger
        logger_type: Tipo de logger ("standard", "performance", "classification")
        
    Returns:
        Logger configurado
    """
    if logger_type == "performance":
        return PerformanceLogger(f"performance.{name}")
    elif logger_type == "classification":
        return ClassificationLogger(f"classification.{name}")
    else:
        return logging.getLogger(name)


def log_system_info():
    """Registra información del sistema al inicio"""
    logger = logging.getLogger("system")
    
    import platform
    import psutil
    
    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "disk_free": psutil.disk_usage('.').free
    }
    
    logger.info("Información del sistema", extra={"system_info": system_info})


if __name__ == "__main__":
    # Prueba del sistema de logging
    setup_advanced_logging()
    log_system_info()
    
    # Crear loggers de prueba
    std_logger = get_logger("test_standard")
    perf_logger = get_logger("test_performance", "performance")
    class_logger = get_logger("test_classification", "classification")
    
    # Pruebas
    std_logger.info("Prueba de logger estándar")
    std_logger.warning("Prueba de warning")
    std_logger.error("Prueba de error")
    
    # Prueba de rendimiento
    perf_logger.start_timer("test_operation")
    import time
    time.sleep(0.1)
    perf_logger.end_timer("test_operation", document_count=5)
    
    # Prueba de clasificación
    mock_result = {
        "final_classification": "factura",
        "final_confidence": 0.85,
        "method_results": {"keyword": {"type": "factura", "confidence": 0.8}},
        "consensus_analysis": {},
        "supplier_info": {},
        "decision_details": {"final_reasoning": "Alta confianza por palabras clave"}
    }
    class_logger.log_classification_result("test_document.pdf", mock_result)
    
    print("✅ Sistema de logging avanzado probado correctamente")