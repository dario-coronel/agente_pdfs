"""
Clasificador especializado para documentos comerciales y financieros
"""
import re
import logging
from typing import Dict, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CommercialDocumentClassifier:
    """Clasificador especializado para documentos comerciales y financieros"""
    
    def __init__(self):
        # Patrones específicos para documentos comerciales
        self.commercial_patterns = {
            "transferencias": {
                "keywords": ["transferencia bancaria", "transferencia", "transfer", "wire transfer", "giro", "envío de dinero", "remesa"],
                "patterns": [
                    r"transferencia\s+(?:bancaria|electr[óo]nica)",
                    r"wire\s+transfer",
                    r"swift\s+(?:code|mt)",
                    r"n[úu]mero\s+de\s+(?:transferencia|operaci[óo]n)",
                    r"c[óo]digo\s+de\s+transferencia",
                    r"banco\s+(?:origen|destino)",
                    r"cbu\s+(?:origen|destino)",
                    r"alias\s+(?:cbu|bancario)"
                ],
                "required_elements": ["transferencia", "banco", "importe"]
            },
            "ordenes_pago": {
                "keywords": ["orden de pago", "payment order", "op", "orden pago", "autorización de pago", "payment authorization"],
                "patterns": [
                    r"orden\s+de\s+pago",
                    r"payment\s+order",
                    r"autorizaci[óo]n\s+(?:de\s+)?pago",
                    r"solicitud\s+(?:de\s+)?pago",
                    r"n[úu]mero\s+(?:de\s+)?(?:orden|op)",
                    r"beneficiario",
                    r"concepto\s+(?:del\s+)?pago",
                    r"fecha\s+(?:de\s+)?vencimiento"
                ],
                "required_elements": ["orden", "pago", "beneficiario"]
            },
            "cheques": {
                "keywords": ["cheque", "check", "ch", "orden de pago al portador"],
                "patterns": [
                    r"cheque\s+(?:n[úu]mero|nro|no|#)",
                    r"p[áa]guese\s+(?:a|al)",
                    r"banco\s+(?:emisor|girado)",
                    r"fecha\s+(?:de\s+)?emisi[óo]n",
                    r"importe\s+en\s+(?:letras|palabras)",
                    r"cuenta\s+corriente",
                    r"cuit\s+(?:del\s+)?(?:emisor|girador)"
                ],
                "required_elements": ["cheque", "banco", "importe"]
            },
            "recibos_pago": {
                "keywords": ["recibo de pago", "recibo", "receipt", "comprobante de pago"],
                "patterns": [
                    r"recibo\s+(?:de\s+)?pago",
                    r"comprobante\s+(?:de\s+)?pago",
                    r"recib[íi]\s+(?:de|del)",
                    r"cancelaci[óo]n\s+(?:de|del)",
                    r"pago\s+(?:de|por)",
                    r"concepto\s+(?:del\s+)?pago",
                    r"forma\s+(?:de\s+)?pago",
                    r"m[ée]todo\s+(?:de\s+)?pago"
                ],
                "required_elements": ["recibo", "pago"]
            },
            "estados_cuenta": {
                "keywords": ["estado de cuenta", "extracto", "resumen de cuenta", "statement"],
                "patterns": [
                    r"estado\s+(?:de\s+)?cuenta",
                    r"extracto\s+(?:bancario|de\s+cuenta)",
                    r"resumen\s+(?:de\s+)?cuenta",
                    r"account\s+statement",
                    r"saldo\s+(?:anterior|actual|final)",
                    r"movimientos\s+(?:del\s+)?per[íi]odo",
                    r"fecha\s+(?:de\s+)?(?:inicio|fin)",
                    r"n[úu]mero\s+(?:de\s+)?cuenta"
                ],
                "required_elements": ["cuenta", "saldo"]
            }
        }
        
        # Términos específicos del sector comercial y financiero
        self.commercial_terms = {
            "bancos": ["banco", "bank", "financial", "financiero", "entidad", "sucursal"],
            "pagos": ["pago", "payment", "abono", "cancelación", "liquidación", "settlement"],
            "monedas": ["pesos", "dollars", "usd", "ars", "eur", "euros", "uyu"],
            "cuentas": ["cuenta", "account", "cbu", "alias", "iban", "swift", "routing"],
            "conceptos": ["concepto", "motivo", "razón", "descripción", "detalle", "observaciones"]
        }
    
    def classify_commercial_document(self, text: str) -> Tuple[str, float, Dict]:
        """
        Clasifica un documento comercial
        
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
            "commercial_terms_found": [],
            "specific_indicators": {}
        }
        
        # Evaluar cada tipo de documento comercial
        for doc_type, config in self.commercial_patterns.items():
            score = self._calculate_commercial_score(text_lower, config, details, doc_type)
            scores[doc_type] = score
        
        # Encontrar el mejor candidato
        if not scores or max(scores.values()) == 0:
            return "desconocido", 0.0, details
        
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Aplicar bonificaciones por términos comerciales
        commercial_bonus = self._calculate_commercial_bonus(text_lower, details)
        final_score = min(best_score + commercial_bonus, 1.0)
        
        logger.info(f"Documento comercial clasificado como '{best_type}' con confianza {final_score:.2f}")
        
        return best_type, final_score, details
    
    def _calculate_commercial_score(self, text: str, config: Dict, details: Dict, doc_type: str) -> float:
        """
        Calcula la puntuación para un tipo específico de documento comercial
        """
        score = 0.0
        patterns_found = []
        
        # Puntuación por palabras clave
        keyword_score = 0
        for keyword in config["keywords"]:
            if keyword in text:
                keyword_score += 0.15
                if keyword not in details["commercial_terms_found"]:
                    details["commercial_terms_found"].append(keyword)
        
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
                required_score += 0.3
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
            "transferencia": [r"transferencia", r"transfer", r"giro", r"envío"],
            "banco": [r"banco", r"bank", r"entidad\s+financiera", r"cbu", r"swift"],
            "importe": [r"importe", r"monto", r"cantidad", r"\$\s*[\d,]+", r"amount"],
            "orden": [r"orden", r"order", r"solicitud", r"autorizaci[óo]n"],
            "pago": [r"pago", r"payment", r"abono", r"cancelaci[óo]n"],
            "beneficiario": [r"beneficiario", r"beneficiary", r"destinatario", r"p[áa]guese\s+a"],
            "cheque": [r"cheque", r"check", r"ch\s+n", r"n[úu]mero.*cheque"],
            "recibo": [r"recibo", r"receipt", r"comprobante", r"recib[íi]"],
            "cuenta": [r"cuenta", r"account", r"cta", r"n[úu]mero.*cuenta"],
            "saldo": [r"saldo", r"balance", r"disponible", r"movimiento"]
        }
        
        if element in element_patterns:
            for pattern in element_patterns[element]:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        
        return False
    
    def _calculate_commercial_bonus(self, text: str, details: Dict) -> float:
        """
        Calcula bonificación por términos específicos del sector comercial
        """
        bonus = 0.0
        
        # Bonificación por términos bancarios
        for bank_term in self.commercial_terms["bancos"]:
            if bank_term in text:
                bonus += 0.04
        
        # Bonificación por términos de pago
        for payment_term in self.commercial_terms["pagos"]:
            if payment_term in text:
                bonus += 0.05
        
        # Bonificación por monedas mencionadas
        for currency in self.commercial_terms["monedas"]:
            if re.search(rf"\b{currency}\b", text):
                bonus += 0.03
        
        # Bonificación por términos de cuentas
        for account_term in self.commercial_terms["cuentas"]:
            if account_term in text:
                bonus += 0.04
        
        # Bonificación por conceptos específicos
        for concept in self.commercial_terms["conceptos"]:
            if concept in text:
                bonus += 0.02
        
        return min(bonus, 0.25)  # Máximo 25% de bonificación
    
    def get_commercial_classification_details(self, text: str) -> Dict:
        """
        Obtiene detalles completos de clasificación comercial
        """
        doc_type, confidence, details = self.classify_commercial_document(text)
        
        # Agregar información adicional
        details.update({
            "classification": doc_type,
            "confidence": confidence,
            "is_commercial_document": confidence > 0.3,
            "commercial_indicators": self._extract_commercial_indicators(text),
            "processing_timestamp": datetime.now().isoformat()
        })
        
        return details
    
    def _extract_commercial_indicators(self, text: str) -> Dict:
        """
        Extrae indicadores específicos del sector comercial
        """
        indicators = {
            "amounts_found": [],
            "account_numbers": [],
            "banks_mentioned": [],
            "payment_methods": [],
            "dates_found": []
        }
        
        text_lower = text.lower()
        
        # Extraer importes
        amount_patterns = [r"\$\s*([\d,]+(?:\.\d+)?)", r"(?:usd|ars|eur)\s*([\d,]+(?:\.\d+)?)"]
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators["amounts_found"].extend([f"${match}" for match in matches])
        
        # Extraer números de cuenta
        account_patterns = [r"(?:cuenta|cbu|cta).*?(\d{10,})", r"alias.*?([a-zA-Z0-9.]+)"]
        for pattern in account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators["account_numbers"].extend(matches)
        
        # Extraer bancos mencionados
        bank_patterns = [r"banco\s+([a-záéíóúñ\s]+)", r"(bbva|santander|galicia|nación|macro|icbc)"]
        for pattern in bank_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators["banks_mentioned"].extend(matches)
        
        # Extraer métodos de pago
        payment_patterns = [r"(transferencia|cheque|efectivo|débito|crédito)"]
        matches = re.findall(payment_patterns[0], text, re.IGNORECASE)
        indicators["payment_methods"].extend(matches)
        
        # Extraer fechas
        date_patterns = [r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})"]
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            indicators["dates_found"].extend(matches)
        
        return indicators
    
    def is_commercial_document(self, text: str, threshold: float = 0.3) -> bool:
        """
        Determina si un documento pertenece al sector comercial
        
        Args:
            text: Texto del documento
            threshold: Umbral mínimo de confianza
            
        Returns:
            True si es un documento comercial
        """
        _, confidence, _ = self.classify_commercial_document(text)
        return confidence > threshold


def get_commercial_classifier() -> CommercialDocumentClassifier:
    """Factory function para obtener una instancia del clasificador comercial"""
    return CommercialDocumentClassifier()