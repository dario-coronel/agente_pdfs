"""
Clasificador de documentos basado en reglas y palabras clave
"""
import logging
from typing import Dict, Tuple
from config import DOCUMENT_TYPES, CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)


class DocumentClassifier:
    """Clasificador principal de documentos PDF"""
    
    def __init__(self):
        self.document_types = DOCUMENT_TYPES
        self.confidence_threshold = CONFIDENCE_THRESHOLD
    
    def classify_document(self, text: str) -> Tuple[str, float]:
        """
        Clasifica un documento basado en su contenido
        
        Args:
            text: Texto del documento a clasificar
            
        Returns:
            Tuple con (tipo_documento, confidence_score)
        """
        if not text:
            logger.warning("Texto vacío para clasificación")
            return "desconocido", 0.0
        
        text_lower = text.lower()
        scores = {}
        
        # Calcular puntuación para cada tipo de documento
        for doc_type, keywords in self.document_types.items():
            score = self._calculate_keyword_score(text_lower, keywords)
            scores[doc_type] = score
            
        # Encontrar el tipo con mayor puntuación
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Si la puntuación es muy baja, clasificar como desconocido
        if best_score < self.confidence_threshold:
            logger.info(f"Puntuación baja ({best_score:.2f}), clasificando como desconocido")
            return "desconocido", best_score
            
        logger.info(f"Documento clasificado como '{best_type}' con confianza {best_score:.2f}")
        return best_type, best_score
    
    def _calculate_keyword_score(self, text: str, keywords: list) -> float:
        """
        Calcula puntuación basada en presencia de palabras clave
        
        Args:
            text: Texto en minúsculas
            keywords: Lista de palabras clave
            
        Returns:
            Puntuación normalizada entre 0 y 1
        """
        total_score = 0
        text_words = text.split()
        text_length = len(text_words)
        
        for keyword in keywords:
            # Contar ocurrencias de la palabra clave
            occurrences = text.count(keyword.lower())
            
            # Puntuación base por ocurrencia
            keyword_score = occurrences * 0.1
            
            # Bonus si aparece en las primeras líneas (más relevante)
            first_lines = ' '.join(text_words[:100])  # Primeras ~100 palabras
            if keyword.lower() in first_lines:
                keyword_score += 0.3
            
            total_score += keyword_score
        
        # Normalizar puntuación
        normalized_score = min(total_score, 1.0)
        
        return normalized_score
    
    def get_classification_details(self, text: str) -> Dict:
        """
        Obtiene detalles completos de la clasificación
        
        Args:
            text: Texto del documento
            
        Returns:
            Diccionario con detalles de la clasificación
        """
        text_lower = text.lower()
        details = {
            "scores": {},
            "keywords_found": {},
            "classification": None,
            "confidence": 0.0
        }
        
        # Calcular puntuaciones para todos los tipos
        for doc_type, keywords in self.document_types.items():
            score = self._calculate_keyword_score(text_lower, keywords)
            details["scores"][doc_type] = score
            
            # Encontrar palabras clave presentes
            found_keywords = [kw for kw in keywords if kw.lower() in text_lower]
            if found_keywords:
                details["keywords_found"][doc_type] = found_keywords
        
        # Clasificación final
        classification, confidence = self.classify_document(text)
        details["classification"] = classification
        details["confidence"] = confidence
        
        return details
    
    def add_document_type(self, doc_type: str, keywords: list):
        """
        Agrega un nuevo tipo de documento
        
        Args:
            doc_type: Nombre del tipo de documento
            keywords: Lista de palabras clave asociadas
        """
        self.document_types[doc_type] = keywords
        logger.info(f"Nuevo tipo de documento agregado: {doc_type}")
    
    def update_keywords(self, doc_type: str, keywords: list):
        """
        Actualiza las palabras clave de un tipo de documento existente
        
        Args:
            doc_type: Tipo de documento a actualizar
            keywords: Nueva lista de palabras clave
        """
        if doc_type in self.document_types:
            self.document_types[doc_type] = keywords
            logger.info(f"Palabras clave actualizadas para {doc_type}")
        else:
            logger.warning(f"Tipo de documento '{doc_type}' no existe")
    
    def get_supported_types(self) -> list:
        """
        Obtiene la lista de tipos de documentos soportados
        
        Returns:
            Lista de tipos de documentos
        """
        return list(self.document_types.keys())