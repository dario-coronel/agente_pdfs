"""
Validador robusto de archivos PDF con validaciones exhaustivas
"""
import os
import hashlib
import mimetypes
from pathlib import Path
import fitz  # PyMuPDF
import logging
from datetime import datetime
from typing import Tuple, Dict, List, Optional
from config import PDF_VALIDATION_CONFIG
from utils import get_logger

logger = get_logger(__name__)


class ValidationResult:
    """Clase para encapsular resultados de validación detallados"""
    
    def __init__(self):
        self.is_valid = False
        self.errors = []
        self.warnings = []
        self.file_info = {}
        self.pdf_metadata = {}
        self.security_info = {}
        self.content_analysis = {}
    
    def add_error(self, message: str):
        """Agrega un error de validación"""
        self.errors.append(message)
        logger.error(f"Validación PDF - Error: {message}")
    
    def add_warning(self, message: str):
        """Agrega una advertencia de validación"""
        self.warnings.append(message)
        logger.warning(f"Validación PDF - Advertencia: {message}")
    
    def to_dict(self) -> Dict:
        """Convierte el resultado a diccionario"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "file_info": self.file_info,
            "pdf_metadata": self.pdf_metadata,
            "security_info": self.security_info,
            "content_analysis": self.content_analysis
        }


class AdvancedPDFValidator:
    """Validador avanzado de archivos PDF con múltiples verificaciones"""
    
    def __init__(self):
        self.config = PDF_VALIDATION_CONFIG
        self.quarantine_dir = Path("quarantine")
        self.quarantine_dir.mkdir(exist_ok=True)
    
    def validate_pdf_comprehensive(self, file_path: str) -> ValidationResult:
        """
        Realiza validación exhaustiva de un archivo PDF
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            ValidationResult con detalles completos de la validación
        """
        result = ValidationResult()
        
        try:
            logger.info(f"Iniciando validación exhaustiva de: {file_path}")
            
            # 1. Validaciones básicas de archivo
            self._validate_file_basics(file_path, result)
            if result.errors:
                return result
            
            # 2. Validación de estructura PDF
            self._validate_pdf_structure(file_path, result)
            if result.errors:
                return result
            
            # 3. Validación de seguridad y encriptación
            self._validate_security(file_path, result)
            
            # 4. Validación de contenido
            self._validate_content_extractability(file_path, result)
            
            # 5. Análisis de metadatos
            self._analyze_metadata(file_path, result)
            
            # 6. Verificación de integridad
            self._verify_integrity(file_path, result)
            
            # 7. Análisis de páginas
            self._analyze_pages(file_path, result)
            
            # Determinar si es válido
            result.is_valid = len(result.errors) == 0
            
            if result.is_valid:
                logger.info(f"✅ Archivo válido: {file_path}")
            else:
                logger.error(f"❌ Archivo inválido: {file_path} - Errores: {len(result.errors)}")
                
                # Mover a cuarentena si está configurado
                if self.config.get("quarantine_invalid_files", False):
                    self._quarantine_file(file_path, result)
        
        except Exception as e:
            result.add_error(f"Error durante validación: {str(e)}")
            logger.exception(f"Excepción durante validación de {file_path}")
        
        return result
    
    def _validate_file_basics(self, file_path: str, result: ValidationResult):
        """Validaciones básicas del archivo"""
        file_path = Path(file_path)
        
        # Verificar existencia
        if not file_path.exists():
            result.add_error(f"Archivo no encontrado: {file_path}")
            return
        
        # Información básica del archivo
        stat = file_path.stat()
        result.file_info = {
            "path": str(file_path.absolute()),
            "name": file_path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
        
        # Validar extensión
        allowed_extensions = self.config.get("allowed_extensions", [".pdf"])
        if file_path.suffix.lower() not in allowed_extensions:
            result.add_error(f"Extensión no permitida: {file_path.suffix}")
        
        # Validar tamaño
        min_size = self.config.get("min_file_size", 1024)
        max_size = self.config.get("max_file_size", 50 * 1024 * 1024)
        
        if stat.st_size < min_size:
            result.add_error(f"Archivo muy pequeño: {stat.st_size} bytes (mínimo: {min_size})")
        
        if stat.st_size > max_size:
            result.add_error(f"Archivo muy grande: {stat.st_size} bytes (máximo: {max_size})")
        
        # Verificar tipo MIME
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type != "application/pdf":
            result.add_warning(f"Tipo MIME inesperado: {mime_type}")
    
    def _validate_pdf_structure(self, file_path: str, result: ValidationResult):
        """Valida la estructura interna del PDF"""
        try:
            doc = fitz.open(file_path)
            
            # Información básica del documento
            result.pdf_metadata = {
                "page_count": len(doc),
                "is_pdf": doc.is_pdf,
                "needs_pass": doc.needs_pass,
                "is_encrypted": doc.is_encrypted,
                "permissions": doc.permissions if hasattr(doc, 'permissions') else None
            }
            
            # Validar número de páginas
            min_pages = self.config.get("min_pages", 1)
            max_pages = self.config.get("max_pages", 500)
            
            if len(doc) < min_pages:
                result.add_error(f"Muy pocas páginas: {len(doc)} (mínimo: {min_pages})")
            
            if len(doc) > max_pages:
                result.add_error(f"Demasiadas páginas: {len(doc)} (máximo: {max_pages})")
            
            # Verificar si está dañado
            if doc.is_closed:
                result.add_error("El documento PDF está dañado o corrupto")
            
            doc.close()
            
        except Exception as e:
            result.add_error(f"Error abriendo PDF: {str(e)}")
    
    def _validate_security(self, file_path: str, result: ValidationResult):
        """Valida aspectos de seguridad del PDF"""
        try:
            doc = fitz.open(file_path)
            
            security_info = {
                "is_encrypted": doc.is_encrypted,
                "needs_password": doc.needs_pass,
                "permissions": {}
            }
            
            # Verificar protección por contraseña si está configurado
            if self.config.get("check_password_protection", True):
                if doc.needs_pass:
                    result.add_error("Documento protegido por contraseña")
                    security_info["password_protected"] = True
                else:
                    security_info["password_protected"] = False
            
            # Analizar permisos si están disponibles
            if hasattr(doc, 'permissions') and doc.permissions:
                perms = doc.permissions
                security_info["permissions"] = {
                    "print": bool(perms & fitz.PDF_PERM_PRINT),
                    "modify": bool(perms & fitz.PDF_PERM_MODIFY),
                    "copy": bool(perms & fitz.PDF_PERM_COPY),
                    "annotate": bool(perms & fitz.PDF_PERM_ANNOTATE)
                }
            
            result.security_info = security_info
            doc.close()
            
        except Exception as e:
            result.add_warning(f"Error verificando seguridad: {str(e)}")
    
    def _validate_content_extractability(self, file_path: str, result: ValidationResult):
        """Valida si se puede extraer contenido del PDF"""
        try:
            doc = fitz.open(file_path)
            
            total_text = ""
            extractable_pages = 0
            pages_with_images = 0
            
            # Analizar cada página
            for page_num in range(min(len(doc), 5)):  # Solo las primeras 5 páginas para eficiencia
                page = doc[page_num]
                
                # Intentar extraer texto
                page_text = page.get_text()
                if page_text.strip():
                    total_text += page_text
                    extractable_pages += 1
                
                # Verificar si tiene imágenes
                if page.get_images():
                    pages_with_images += 1
            
            content_analysis = {
                "total_characters": len(total_text),
                "extractable_pages": extractable_pages,
                "pages_with_images": pages_with_images,
                "has_extractable_text": len(total_text.strip()) > 0,
                "text_density": len(total_text) / len(doc) if len(doc) > 0 else 0
            }
            
            # Validación de contenido extraíble
            if self.config.get("check_text_extractability", True):
                if content_analysis["total_characters"] < 10:
                    if pages_with_images == 0:
                        result.add_error("No se puede extraer texto y no contiene imágenes")
                    else:
                        result.add_warning("Texto mínimo pero contiene imágenes (posible OCR necesario)")
            
            result.content_analysis = content_analysis
            doc.close()
            
        except Exception as e:
            result.add_error(f"Error validando contenido: {str(e)}")
    
    def _analyze_metadata(self, file_path: str, result: ValidationResult):
        """Analiza los metadatos del PDF"""
        try:
            doc = fitz.open(file_path)
            
            metadata = doc.metadata
            if metadata:
                result.pdf_metadata.update({
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                    "subject": metadata.get("subject", ""),
                    "keywords": metadata.get("keywords", ""),
                    "creation_date": metadata.get("creationDate", ""),
                    "modification_date": metadata.get("modDate", "")
                })
            
            doc.close()
            
        except Exception as e:
            result.add_warning(f"Error analizando metadatos: {str(e)}")
    
    def _verify_integrity(self, file_path: str, result: ValidationResult):
        """Verifica la integridad del archivo"""
        if not self.config.get("check_file_integrity", True):
            return
        
        try:
            # Calcular hash del archivo
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            result.file_info["sha256"] = sha256_hash.hexdigest()
            
            # Verificar que el archivo se puede leer completamente
            with open(file_path, "rb") as f:
                file_size = 0
                while chunk := f.read(8192):
                    file_size += len(chunk)
                
                if file_size != result.file_info["size"]:
                    result.add_error("Inconsistencia en el tamaño del archivo durante lectura")
        
        except Exception as e:
            result.add_warning(f"Error verificando integridad: {str(e)}")
    
    def _analyze_pages(self, file_path: str, result: ValidationResult):
        """Analiza las páginas del documento"""
        try:
            doc = fitz.open(file_path)
            
            page_analysis = {
                "total_pages": len(doc),
                "pages_with_text": 0,
                "pages_with_images": 0,
                "pages_with_links": 0,
                "average_text_length": 0,
                "page_sizes": []
            }
            
            total_text_length = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Texto en la página
                page_text = page.get_text()
                if page_text.strip():
                    page_analysis["pages_with_text"] += 1
                    total_text_length += len(page_text)
                
                # Imágenes en la página
                if page.get_images():
                    page_analysis["pages_with_images"] += 1
                
                # Enlaces en la página
                if page.get_links():
                    page_analysis["pages_with_links"] += 1
                
                # Tamaño de página
                rect = page.rect
                page_analysis["page_sizes"].append({
                    "width": rect.width,
                    "height": rect.height
                })
            
            if page_analysis["pages_with_text"] > 0:
                page_analysis["average_text_length"] = total_text_length / page_analysis["pages_with_text"]
            
            result.content_analysis.update(page_analysis)
            doc.close()
            
        except Exception as e:
            result.add_warning(f"Error analizando páginas: {str(e)}")
    
    def _quarantine_file(self, file_path: str, result: ValidationResult):
        """Mueve archivo inválido a cuarentena"""
        try:
            source_path = Path(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_file = self.quarantine_dir / f"{timestamp}_{source_path.name}"
            
            # Crear archivo de informe junto al archivo en cuarentena
            report_file = quarantine_file.with_suffix(".json")
            
            import shutil
            shutil.move(str(source_path), str(quarantine_file))
            
            # Guardar informe de validación
            with open(report_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.warning(f"Archivo movido a cuarentena: {quarantine_file}")
            
        except Exception as e:
            logger.error(f"Error moviendo archivo a cuarentena: {e}")
    
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
            report["checks"]["structure"] = self._validate_structure_simple(file_path)
            if report["checks"]["structure"]:
                with fitz.open(file_path) as doc:
                    report["details"]["pages"] = len(doc)
                    report["details"]["title"] = doc.metadata.get("title", "")
            
            # Verificar contenido
            report["checks"]["content"] = self._validate_content_simple(file_path)
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
    
    def validate_pdf(self, file_path: str) -> bool:
        """
        Método de compatibilidad para validación simple
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            True si el archivo es válido
        """
        result = self.validate_pdf_comprehensive(file_path)
        return result.is_valid
    
    def get_validation_summary(self) -> Dict:
        """
        Obtiene resumen de validaciones realizadas
        
        Returns:
            Diccionario con estadísticas de validación
        """
        quarantine_files = list(self.quarantine_dir.glob("*.pdf"))
        
        return {
            "quarantine_directory": str(self.quarantine_dir.absolute()),
            "files_in_quarantine": len(quarantine_files),
            "quarantine_files": [f.name for f in quarantine_files],
            "validation_config": self.config
        }
    
    def _validate_structure_simple(self, file_path: str) -> bool:
        """
        Método de compatibilidad para validación simple de estructura
        """
        try:
            with fitz.open(file_path) as doc:
                return not doc.is_closed and len(doc) > 0
        except:
            return False
    
    def _validate_content_simple(self, file_path: str) -> bool:
        """
        Método de compatibilidad para validación simple de contenido
        """
        try:
            with fitz.open(file_path) as doc:
                for page_num in range(min(len(doc), 3)):  # Verificar primeras 3 páginas
                    page = doc[page_num]
                    if page.get_text().strip():
                        return True
                return False
        except:
            return False


# Clase de compatibilidad con el nombre original
PDFValidator = AdvancedPDFValidator