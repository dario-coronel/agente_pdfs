"""
Validador de archivos PDF
"""
import os
import fitz  # PyMuPDF
import logging
from typing import Tuple, Dict
from config import MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class PDFValidator:
    """Validador de archivos PDF y su contenido"""
    
    def __init__(self):
        self.max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        self.supported_extensions = SUPPORTED_EXTENSIONS
    
    def validate_pdf(self, file_path: str) -> bool:
        """
        Valida si un archivo PDF es procesable
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            True si el archivo es válido, False en caso contrario
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                logger.error(f"Archivo no encontrado: {file_path}")
                return False
            
            # Verificar extensión
            if not self._validate_extension(file_path):
                return False
            
            # Verificar tamaño
            if not self._validate_size(file_path):
                return False
            
            # Verificar que se puede abrir como PDF
            if not self._validate_pdf_structure(file_path):
                return False
            
            # Verificar que tiene contenido extraíble
            if not self._validate_content(file_path):
                return False
            
            logger.debug(f"PDF válido: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validando PDF {file_path}: {e}")
            return False
    
    def _validate_extension(self, file_path: str) -> bool:
        """Valida la extensión del archivo"""
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension not in self.supported_extensions:
            logger.error(f"Extensión no soportada: {extension}")
            return False
            
        return True
    
    def _validate_size(self, file_path: str) -> bool:
        """Valida el tamaño del archivo"""
        try:
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            
            if file_size == 0:
                logger.error(f"Archivo vacío: {file_path}")
                return False
            
            if file_size > self.max_size_bytes:
                logger.error(f"Archivo muy grande ({size_mb:.1f}MB): {file_path}")
                return False
            
            logger.debug(f"Tamaño válido ({size_mb:.1f}MB): {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error verificando tamaño de {file_path}: {e}")
            return False
    
    def _validate_pdf_structure(self, file_path: str) -> bool:
        """Valida que el archivo se puede abrir como PDF"""
        try:
            with fitz.open(file_path) as doc:
                # Verificar que tiene al menos una página
                if len(doc) == 0:
                    logger.error(f"PDF sin páginas: {file_path}")
                    return False
                
                # Intentar acceder a la primera página
                page = doc[0]
                if page is None:
                    logger.error(f"No se puede acceder a la primera página: {file_path}")
                    return False
                
            logger.debug(f"Estructura PDF válida: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF corrupto o inválido {file_path}: {e}")
            return False
    
    def _validate_content(self, file_path: str) -> bool:
        """Valida que el PDF tiene contenido extraíble"""
        try:
            with fitz.open(file_path) as doc:
                total_text = ""
                
                # Intentar extraer texto de las primeras páginas
                max_pages_to_check = min(3, len(doc))
                
                for i in range(max_pages_to_check):
                    page = doc[i]
                    page_text = page.get_text().strip()
                    total_text += page_text
                
                # Verificar que hay texto extraíble
                if len(total_text.strip()) < 10:
                    logger.warning(f"PDF con poco o sin texto extraíble: {file_path}")
                    # No retornamos False aquí porque podría ser un PDF de imágenes válido
                    # que necesite OCR en el futuro
                
            logger.debug(f"Contenido extraíble disponible: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error extrayendo contenido de {file_path}: {e}")
            return False
    
    def get_validation_report(self, file_path: str) -> Dict:
        """
        Obtiene un reporte detallado de validación
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con detalles de la validación
        """
        report = {
            "file_path": file_path,
            "is_valid": False,
            "checks": {
                "exists": False,
                "extension": False,
                "size": False,
                "structure": False,
                "content": False
            },
            "details": {},
            "warnings": []
        }
        
        try:
            # Verificar existencia
            report["checks"]["exists"] = os.path.exists(file_path)
            if not report["checks"]["exists"]:
                report["details"]["error"] = "Archivo no encontrado"
                return report
            
            # Verificar extensión
            report["checks"]["extension"] = self._validate_extension(file_path)
            
            # Verificar tamaño
            report["checks"]["size"] = self._validate_size(file_path)
            if report["checks"]["size"]:
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                report["details"]["size_mb"] = round(size_mb, 2)
            
            # Verificar estructura
            report["checks"]["structure"] = self._validate_pdf_structure(file_path)
            if report["checks"]["structure"]:
                with fitz.open(file_path) as doc:
                    report["details"]["pages"] = len(doc)
                    report["details"]["title"] = doc.metadata.get("title", "")
            
            # Verificar contenido
            report["checks"]["content"] = self._validate_content(file_path)
            if report["checks"]["content"]:
                with fitz.open(file_path) as doc:
                    # Contar caracteres de texto extraíble
                    total_chars = 0
                    for page in doc:
                        total_chars += len(page.get_text().strip())
                    
                    report["details"]["extractable_chars"] = total_chars
                    
                    if total_chars < 50:
                        report["warnings"].append("Poco texto extraíble, podría necesitar OCR")
            
            # Determinación final
            report["is_valid"] = all(report["checks"].values())
            
        except Exception as e:
            report["details"]["error"] = str(e)
            logger.error(f"Error generando reporte de validación para {file_path}: {e}")
        
        return report
    
    def validate_batch(self, file_paths: list) -> Dict:
        """
        Valida múltiples archivos
        
        Args:
            file_paths: Lista de rutas de archivos
            
        Returns:
            Diccionario con resultados de validación por lotes
        """
        results = {
            "total_files": len(file_paths),
            "valid_files": 0,
            "invalid_files": 0,
            "reports": []
        }
        
        for file_path in file_paths:
            report = self.get_validation_report(file_path)
            results["reports"].append(report)
            
            if report["is_valid"]:
                results["valid_files"] += 1
            else:
                results["invalid_files"] += 1
        
        return results