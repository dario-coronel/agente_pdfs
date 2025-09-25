"""
Extractor de metadatos específicos de documentos
"""
import re
import logging
from typing import Optional, List, Dict
from datetime import datetime
from config import CUIT_PATTERN, DATE_PATTERNS, AMOUNT_PATTERN

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extrae metadatos específicos como CUIT, fechas, montos, etc."""
    
    def extract_cuit(self, text: str) -> Optional[str]:
        """
        Extrae CUIT del texto (formato 00-00000000-0)
        
        Args:
            text: Texto donde buscar el CUIT
            
        Returns:
            CUIT encontrado o None
        """
        try:
            match = re.search(CUIT_PATTERN, text)
            if match:
                cuit = match.group(0)
                logger.debug(f"CUIT encontrado: {cuit}")
                return cuit
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo CUIT: {e}")
            return None
    
    def extract_dates(self, text: str) -> List[str]:
        """
        Extrae fechas del texto usando múltiples patrones
        
        Args:
            text: Texto donde buscar fechas
            
        Returns:
            Lista de fechas encontradas
        """
        dates = []
        try:
            for pattern in DATE_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                dates.extend(matches)
                
            # Remover duplicados manteniendo el orden
            unique_dates = list(dict.fromkeys(dates))
            
            if unique_dates:
                logger.debug(f"Fechas encontradas: {unique_dates}")
                
            return unique_dates
            
        except Exception as e:
            logger.error(f"Error extrayendo fechas: {e}")
            return []
    
    def extract_amounts(self, text: str) -> List[str]:
        """
        Extrae montos del texto
        
        Args:
            text: Texto donde buscar montos
            
        Returns:
            Lista de montos encontrados
        """
        try:
            amounts = re.findall(AMOUNT_PATTERN, text)
            
            if amounts:
                logger.debug(f"Montos encontrados: {amounts}")
                
            return amounts
            
        except Exception as e:
            logger.error(f"Error extrayendo montos: {e}")
            return []
    
    def extract_supplier_name(self, text: str) -> Optional[str]:
        """
        Intenta extraer el nombre del proveedor del documento
        
        Args:
            text: Texto del documento
            
        Returns:
            Nombre del proveedor o None
        """
        try:
            lines = text.split('\n')[:10]  # Buscar en las primeras 10 líneas
            
            # Patrones comunes para identificar proveedores
            supplier_patterns = [
                r"Razón Social:?\s*([A-Z][A-Za-z\s&\.]{3,50})",
                r"Proveedor:?\s*([A-Z][A-Za-z\s&\.]{3,50})",
                r"Empresa:?\s*([A-Z][A-Za-z\s&\.]{3,50})",
                r"^([A-Z][A-Za-z\s&\.]{10,50})\s*(S\.A\.|SRL|SA|LTDA)"
            ]
            
            for line in lines:
                line = line.strip()
                for pattern in supplier_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        supplier = match.group(1).strip()
                        logger.debug(f"Proveedor encontrado: {supplier}")
                        return supplier
                        
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo proveedor: {e}")
            return None
    
    def extract_document_number(self, text: str) -> Optional[str]:
        """
        Extrae el número de documento (factura, remito, etc.)
        
        Args:
            text: Texto del documento
            
        Returns:
            Número de documento o None
        """
        try:
            # Patrones para números de documento
            doc_patterns = [
                r"N[úu]mero:?\s*(\d+[-/]?\d*)",
                r"N[°º]:?\s*(\d+[-/]?\d*)",
                r"Factura N[°º]:?\s*(\d+[-/]?\d*)",
                r"Remito N[°º]:?\s*(\d+[-/]?\d*)",
                r"Documento N[°º]:?\s*(\d+[-/]?\d*)"
            ]
            
            for pattern in doc_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    doc_number = match.group(1)
                    logger.debug(f"Número de documento encontrado: {doc_number}")
                    return doc_number
                    
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo número de documento: {e}")
            return None
    
    def extract_all_metadata(self, text: str) -> Dict:
        """
        Extrae todos los metadatos del texto
        
        Args:
            text: Texto del documento
            
        Returns:
            Diccionario con todos los metadatos encontrados
        """
        metadata = {
            "cuit": self.extract_cuit(text),
            "dates": self.extract_dates(text),
            "amounts": self.extract_amounts(text),
            "supplier": self.extract_supplier_name(text),
            "document_number": self.extract_document_number(text),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Metadatos extraídos: {metadata}")
        return metadata