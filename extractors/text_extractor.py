"""
Extractor de texto de documentos PDF
"""
import fitz  # PyMuPDF
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extrae texto de documentos PDF usando PyMuPDF"""
    
    def extract_from_pdf(self, file_path: str) -> Optional[str]:
        """
        Extrae texto completo de un archivo PDF
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Texto extraído o None si hay error
        """
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page_num, page in enumerate(doc):
                    page_text = page.get_text()
                    text += f"\n--- Página {page_num + 1} ---\n{page_text}"
                    
            logger.info(f"Texto extraído exitosamente de {file_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extrayendo texto de {file_path}: {e}")
            return None
    
    def extract_page_text(self, file_path: str, page_num: int) -> Optional[str]:
        """
        Extrae texto de una página específica
        
        Args:
            file_path: Ruta al archivo PDF
            page_num: Número de página (0-indexado)
            
        Returns:
            Texto de la página o None si hay error
        """
        try:
            with fitz.open(file_path) as doc:
                if page_num < len(doc):
                    page = doc[page_num]
                    text = page.get_text()
                    logger.debug(f"Texto extraído de página {page_num + 1} de {file_path}")
                    return text.strip()
                else:
                    logger.warning(f"Página {page_num + 1} no existe en {file_path}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error extrayendo página {page_num + 1} de {file_path}: {e}")
            return None
    
    def get_document_info(self, file_path: str) -> Dict:
        """
        Obtiene información básica del documento PDF
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con información del documento
        """
        try:
            with fitz.open(file_path) as doc:
                info = {
                    "page_count": len(doc),
                    "title": doc.metadata.get("title", ""),
                    "author": doc.metadata.get("author", ""),
                    "subject": doc.metadata.get("subject", ""),
                    "creator": doc.metadata.get("creator", ""),
                    "producer": doc.metadata.get("producer", ""),
                    "creation_date": doc.metadata.get("creationDate", ""),
                    "modification_date": doc.metadata.get("modDate", "")
                }
                
            logger.debug(f"Información extraída de {file_path}: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error obteniendo información de {file_path}: {e}")
            return {}