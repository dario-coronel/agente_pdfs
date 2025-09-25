"""
Clasificador especializado para documentos del sector agropecuario
"""
import re
import logging
from typing import Dict, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AgroDocumentClassifier:
    """Clasificador especializado para documentos agropecuarios"""
    
    def __init__(self):
        # Patrones específicos para documentos agropecuarios
        self.agro_patterns = {
            "liquidaciones_granos": {
                "keywords": ["liquidación", "liquidacion", "granos", "cereales", "soja", "trigo", "maíz", "maiz", "girasol", "sorgo"],
                "patterns": [
                    r"liquidaci[óo]n\s+(?:de\s+)?(?:granos|cereales)",
                    r"(?:soja|trigo|ma[íi]z|girasol|sorgo)",
                    r"precio\s+(?:por\s+)?(?:kg|tonelada|tn|qq)",
                    r"(?:humedad|protein[aí]|aceite).*%",
                    r"descuento.*(?:humedad|merma)",
                    r"peso\s+neto.*(?:kg|tn)"
                ],
                "required_elements": ["precio", "peso", "grano"]
            },
            "cot": {
                "keywords": ["cot", "certificado de transferencia", "transferencia", "granos"],
                "patterns": [
                    r"certificado\s+de\s+transferencia",
                    r"c\.?o\.?t\.?",
                    r"transfer[ae]ncia\s+(?:de\s+)?granos",
                    r"depósito\s+(?:de\s+)?cereales",
                    r"warrant"
                ],
                "required_elements": ["certificado", "transferencia"]
            },
            "ctg": {
                "keywords": ["ctg", "carta de crédito", "certificado de depósito", "warrant"],
                "patterns": [
                    r"carta\s+de\s+cr[ée]dito",
                    r"certificado\s+de\s+dep[óo]sito",
                    r"c\.?t\.?g\.?",
                    r"warrant",
                    r"almacenaje",
                    r"dep[óo]sito\s+(?:de\s+)?granos"
                ],
                "required_elements": ["certificado", "depósito"]
            },
            "cartas_porte": {
                "keywords": ["carta de porte", "porte", "transporte", "flete"],
                "patterns": [
                    r"carta\s+de\s+porte",
                    r"remito\s+(?:de\s+)?transporte",
                    r"gu[íi]a\s+(?:de\s+)?transporte",
                    r"flete",
                    r"transportista",
                    r"chapa\s+(?:del\s+)?cami[óo]n"
                ],
                "required_elements": ["transporte", "destino"]
            },
            "pesajes": {
                "keywords": ["pesaje", "peso", "báscula", "balanza"],
                "patterns": [
                    r"peso\s+(?:bruto|neto|tara)",
                    r"b[áa]scula",
                    r"balanza",
                    r"pesaje",
                    r"\d+\s*(?:kg|tn|toneladas?)",
                    r"ticket\s+(?:de\s+)?peso"
                ],
                "required_elements": ["peso"]
            },
            "contratos_granos": {
                "keywords": ["contrato", "compraventa", "granos", "cereales"],
                "patterns": [
                    r"contrato\s+(?:de\s+)?(?:compraventa|compra|venta)",
                    r"acuerdo\s+(?:de\s+)?(?:compraventa|comercializaci[óo]n)",
                    r"condiciones\s+(?:de\s+)?entrega",
                    r"precio\s+(?:por\s+)?(?:tonelada|kg|quintal)",
                    r"calidad\s+(?:de\s+)?grano"
                ],
                "required_elements": ["contrato", "precio", "grano"]
            }
        }
        
        # Términos específicos del sector agropecuario
        self.agro_terms = {
            "granos": ["soja", "trigo", "maíz", "maiz", "girasol", "sorgo", "avena", "cebada", "centeno"],
            "medidas": ["kg", "tn", "toneladas", "quintales", "qq", "hectolitro", "hl"],
            "calidad": ["humedad", "proteína", "aceite", "impurezas", "peso hectolitrico", "gluten"],
            "procesos": ["cosecha", "acopio", "almacenaje", "secado", "clasificación", "limpieza"],
            "actores": ["productor", "acopiador", "exportador", "cooperativa", "cerealera"]
        }
    
    def classify_agro_document(self, text: str) -> Tuple[str, float, Dict]:
        """
        Clasifica un documento agropecuario
        
        Args:
            text: Texto del documento
            
        Returns:
            Tuple con (tipo_documento, confidence_score, detalles)
        """
        if not text:
            return "desconocido", 0.0, {}
        
        text_lower = text.lower()
        scores = {}
        details = {
            "patterns_found": {},
            "agro_terms_found": [],
            "specific_indicators": {}
        }
        
        # Evaluar cada tipo de documento agropecuario
        for doc_type, config in self.agro_patterns.items():
            score = self._calculate_agro_score(text_lower, config, details, doc_type)
            scores[doc_type] = score
        
        # Encontrar el mejor candidato
        if not scores or max(scores.values()) == 0:
            return "desconocido", 0.0, details
        
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Aplicar bonificaciones por términos agropecuarios
        agro_bonus = self._calculate_agro_bonus(text_lower, details)
        final_score = min(best_score + agro_bonus, 1.0)
        
        logger.info(f"Documento agropecuario clasificado como '{best_type}' con confianza {final_score:.2f}")
        
        return best_type, final_score, details
    
    def _calculate_agro_score(self, text: str, config: Dict, details: Dict, doc_type: str) -> float:
        """
        Calcula la puntuación para un tipo específico de documento agropecuario
        """
        score = 0.0
        patterns_found = []
        
        # Puntuación por palabras clave
        keyword_score = 0
        for keyword in config["keywords"]:
            if keyword in text:
                keyword_score += 0.15
                if keyword not in details["agro_terms_found"]:
                    details["agro_terms_found"].append(keyword)
        
        # Puntuación por patrones específicos
        pattern_score = 0
        for pattern in config["patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pattern_score += 0.2 * len(matches)
                patterns_found.extend(matches)
        
        # Verificar elementos requeridos
        required_score = 0
        required_found = []
        for element in config["required_elements"]:
            if self._check_required_element(text, element):
                required_score += 0.25
                required_found.append(element)
        
        if patterns_found:
            details["patterns_found"][doc_type] = patterns_found
        
        if required_found:
            details["specific_indicators"][doc_type] = required_found
        
        # Puntuación total
        total_score = keyword_score + pattern_score + required_score
        
        # Normalizar y aplicar peso por cantidad de elementos requeridos encontrados
        if config["required_elements"]:
            required_ratio = len(required_found) / len(config["required_elements"])
            total_score *= (0.5 + 0.5 * required_ratio)  # Penalizar si faltan elementos
        
        return min(total_score, 1.0)
    
    def _check_required_element(self, text: str, element: str) -> bool:
        """
        Verifica la presencia de elementos requeridos específicos
        """
        element_patterns = {
            "precio": [r"precio", r"\$\s*[\d,]+", r"valor", r"importe"],
            "peso": [r"peso", r"\d+\s*(?:kg|tn|toneladas)", r"balanza", r"báscula"],
            "grano": [r"soja|trigo|ma[íi]z|girasol|sorgo|cereales|granos"],
            "certificado": [r"certificado", r"cert\.", r"certificación"],
            "transferencia": [r"transferencia", r"transfer", r"cesión"],
            "depósito": [r"depósito", r"almacén", r"storage", r"acopio"],
            "transporte": [r"transporte", r"flete", r"camión", r"transportista"],
            "destino": [r"destino", r"entregar", r"delivery", r"dirección"],
            "contrato": [r"contrato", r"acuerdo", r"convenio", r"términos"]
        }
        
        if element in element_patterns:
            for pattern in element_patterns[element]:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        
        return False
    
    def _calculate_agro_bonus(self, text: str, details: Dict) -> float:
        """
        Calcula bonificación por términos específicos del sector agropecuario
        """
        bonus = 0.0
        
        # Bonificación por tipos de granos
        for grain in self.agro_terms["granos"]:
            if grain in text:
                bonus += 0.05
        
        # Bonificación por unidades de medida agropecuarias
        for measure in self.agro_terms["medidas"]:
            if re.search(rf"\b{measure}\b", text):
                bonus += 0.03
        
        # Bonificación por términos de calidad
        for quality in self.agro_terms["calidad"]:
            if quality in text:
                bonus += 0.04
        
        # Bonificación por procesos agropecuarios
        for process in self.agro_terms["procesos"]:
            if process in text:
                bonus += 0.03
        
        # Bonificación por actores del sector
        for actor in self.agro_terms["actores"]:
            if actor in text:
                bonus += 0.04
        
        return min(bonus, 0.3)  # Máximo 30% de bonificación
    
    def get_agro_classification_details(self, text: str) -> Dict:
        """
        Obtiene detalles completos de clasificación agropecuaria
        """
        doc_type, confidence, details = self.classify_agro_document(text)
        
        # Agregar información adicional
        details.update({
            "classification": doc_type,
            "confidence": confidence,
            "is_agro_document": confidence > 0.3,
            "agro_indicators": self._extract_agro_indicators(text),
            "processing_timestamp": datetime.now().isoformat()
        })
        
        return details
    
    def _extract_agro_indicators(self, text: str) -> Dict:
        """
        Extrae indicadores específicos del sector agropecuario
        """
        indicators = {
            "grains_mentioned": [],
            "weights_found": [],
            "prices_found": [],
            "quality_params": [],
            "dates_found": []
        }
        
        text_lower = text.lower()
        
        # Extraer granos mencionados
        for grain in self.agro_terms["granos"]:
            if grain in text_lower:
                indicators["grains_mentioned"].append(grain)
        
        # Extraer pesos
        weight_patterns = [r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(kg|tn|toneladas?|quintales?)"]
        for pattern in weight_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators["weights_found"].extend([f"{match[0]} {match[1]}" for match in matches])
        
        # Extraer precios
        price_patterns = [r"\$\s*([\d,]+(?:\.\d+)?)", r"precio[:\s]*([\d,]+(?:\.\d+)?)"]
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators["prices_found"].extend(matches)
        
        # Extraer parámetros de calidad
        quality_patterns = [r"(humedad|proteína|aceite)[:\s]*([\d,]+(?:\.\d+)?)\s*%?"]
        for pattern in quality_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators["quality_params"].extend([f"{match[0]}: {match[1]}%" for match in matches])
        
        # Extraer fechas
        date_patterns = [r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})"]
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            indicators["dates_found"].extend(matches)
        
        return indicators
    
    def is_agro_document(self, text: str, threshold: float = 0.3) -> bool:
        """
        Determina si un documento pertenece al sector agropecuario
        
        Args:
            text: Texto del documento
            threshold: Umbral mínimo de confianza
            
        Returns:
            True si es un documento agropecuario
        """
        _, confidence, _ = self.classify_agro_document(text)
        return confidence > threshold


def get_agro_classifier() -> AgroDocumentClassifier:
    """Factory function para obtener una instancia del clasificador agropecuario"""
    return AgroDocumentClassifier()