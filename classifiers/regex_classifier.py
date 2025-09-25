"""
Clasificador basado en patrones regex avanzados
"""
import re
import logging
from typing import Dict, Tuple, List
from config import DOCUMENT_TYPES

logger = logging.getLogger(__name__)


class RegexClassifier:
    """Clasificador que usa patrones regex específicos para identificar tipos de documentos"""
    
    def __init__(self):
        # Patrones regex específicos por tipo de documento
        self.regex_patterns = {
            "facturas": [
                r"FACTURA\s+[A-Z]?\s*N[°º]?\s*\d+",
                r"ORIGINAL\s+DUPLICADO",
                r"CÓDIGO\s+DESCRIPCIÓN\s+CANTIDAD",
                r"SUBTOTAL.*TOTAL",
                r"IVA\s+(21|10\.5|27)%",
                r"PUNTO\s+DE\s+VENTA\s*:\s*\d+",
                r"CAE\s*N[°º]?\s*:\s*\d+",
                r"VENCIMIENTO\s+DEL\s+CAE"
            ],
            "remitos": [
                r"REMITO\s*N[°º]?\s*\d+",
                r"ORDEN\s+DE\s+ENTREGA",
                r"DESTINATARIO",
                r"BULTOS\s+PESO",
                r"MERCADERÍA\s+ENTREGADA",
                r"CÓDIGO\s+ARTÍCULO\s+CANTIDAD",
                r"SIN\s+CARGO\s+FISCAL",
                r"DOCUMENTO\s+NO\s+VÁLIDO"
            ],
            "notas_credito": [
                r"NOTA\s+DE\s+CR[EÉ]DITO\s*N[°º]?\s*\d+",
                r"ANULACIÓN\s+PARCIAL",
                r"DEVOLUCIÓN",
                r"DESCUENTO\s+OTORGADO",
                r"IMPORTE\s+A\s+FAVOR",
                r"CRÉDITO\s+FISCAL"
            ],
            "notas_debito": [
                r"NOTA\s+DE\s+D[EÉ]BITO\s*N[°º]?\s*\d+",
                r"CARGO\s+ADICIONAL",
                r"INTERESES\s+MORATORIOS",
                r"GASTOS\s+ADMINISTRATIVOS",
                r"AJUSTE\s+DE\s+PRECIO",
                r"DÉBITO\s+FISCAL"
            ],
            "cartas_porte": [
                r"CARTA\s+DE\s+PORTE\s*N[°º]?\s*\d+",
                r"TRANSPORTISTA",
                r"ORIGEN.*DESTINO",
                r"CONDUCTOR.*DNI",
                r"PATENTE.*ACOPLADO",
                r"MERCADERÍA\s+A\s+TRANSPORTAR",
                r"KM\s+RECORRIDOS"
            ],
            "recibos": [
                r"RECIBO\s*N[°º]?\s*\d+",
                r"RECIBÍ\s+DE",
                r"LA\s+SUMA\s+DE",
                r"PESOS\s+CON\s+\d+/100",
                r"EN\s+CONCEPTO\s+DE",
                r"FIRMA\s+Y\s+ACLARACIÓN"
            ],
            "ordenes_compra": [
                r"ORDEN\s+DE\s+COMPRA\s*N[°º]?\s*\d+",
                r"PROVEEDOR\s*:",
                r"FECHA\s+DE\s+ENTREGA",
                r"CONDICIONES\s+DE\s+PAGO",
                r"LUGAR\s+DE\s+ENTREGA",
                r"AUTORIZADO\s+POR"
            ],
            "contratos": [
                r"CONTRATO\s+(DE\s+)?(LOCACIÓN|TRABAJO|SERVICIOS)",
                r"PARTES\s+CONTRATANTES",
                r"CLÁUSULAS\s+PARTICULARES",
                r"VIGENCIA\s+DEL\s+CONTRATO",
                r"EN\s+PRUEBA\s+DE\s+CONFORMIDAD",
                r"FIRMA.*FECHA"
            ]
        }
        
        # Patrones para estructura de documentos
        self.structure_patterns = {
            "header_patterns": [
                r"^[A-Z\s]{10,50}$",  # Títulos en mayúsculas
                r"^\s*ORIGINAL\s*$",
                r"^\s*DUPLICADO\s*$"
            ],
            "table_patterns": [
                r"CÓDIGO\s+DESCRIPCIÓN\s+CANTIDAD\s+PRECIO",
                r"ITEM\s+DETALLE\s+CANT\s+P\.UNIT",
                r"\|\s*\w+\s*\|\s*\w+\s*\|\s*\d+\s*\|"
            ],
            "total_patterns": [
                r"SUBTOTAL\s*:?\s*\$?\s*[\d,]+\.?\d*",
                r"TOTAL\s*:?\s*\$?\s*[\d,]+\.?\d*",
                r"NETO\s*:?\s*\$?\s*[\d,]+\.?\d*"
            ]
        }
        
        # Patrones específicos de formato AFIP/Argentina
        self.afip_patterns = {
            "cae_pattern": r"CAE\s*N[°º]?\s*:\s*\d{14}",
            "cuit_pattern": r"CUIT\s*:?\s*\d{2}-\d{8}-\d",
            "fecha_vto_cae": r"VENCIMIENTO\s+DEL\s+CAE\s*:\s*\d{2}/\d{2}/\d{4}",
            "punto_venta": r"PUNTO\s+DE\s+VENTA\s*:\s*\d{5}",
            "responsabilidad_iva": r"RESPONSABLE\s+INSCRIPTO|MONOTRIBUTISTA|EXENTO"
        }
    
    def classify_by_regex(self, text: str) -> Tuple[str, float]:
        """
        Clasifica documento usando patrones regex
        
        Args:
            text: Texto del documento
            
        Returns:
            Tuple con (tipo_documento, confidence_score)
        """
        scores = {}
        
        for doc_type, patterns in self.regex_patterns.items():
            score = self._calculate_regex_score(text, patterns)
            scores[doc_type] = score
        
        # Encontrar el tipo con mayor puntuación
        if not scores or max(scores.values()) == 0:
            return "desconocido", 0.0
        
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        logger.debug(f"Clasificación regex: {best_type} (confianza: {best_score:.3f})")
        return best_type, best_score
    
    def _calculate_regex_score(self, text: str, patterns: List[str]) -> float:
        """
        Calcula puntuación basada en patrones regex
        
        Args:
            text: Texto del documento
            patterns: Lista de patrones regex
            
        Returns:
            Puntuación normalizada
        """
        total_matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            try:
                matches = len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))
                if matches > 0:
                    total_matches += min(matches, 3)  # Máximo 3 puntos por patrón
            except re.error as e:
                logger.warning(f"Error en patrón regex '{pattern}': {e}")
        
        # Normalizar puntuación (máximo 3 puntos por patrón)
        max_possible_score = total_patterns * 3
        normalized_score = min(total_matches / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
        
        return normalized_score
    
    def analyze_document_structure(self, text: str) -> Dict:
        """
        Analiza la estructura del documento usando regex
        
        Args:
            text: Texto del documento
            
        Returns:
            Diccionario con análisis de estructura
        """
        analysis = {
            "has_header": False,
            "has_table_structure": False,
            "has_totals": False,
            "is_afip_compliant": False,
            "structure_score": 0.0
        }
        
        # Verificar patrones de encabezado
        for pattern in self.structure_patterns["header_patterns"]:
            if re.search(pattern, text, re.MULTILINE):
                analysis["has_header"] = True
                break
        
        # Verificar estructura de tabla
        for pattern in self.structure_patterns["table_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                analysis["has_table_structure"] = True
                break
        
        # Verificar totales
        for pattern in self.structure_patterns["total_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                analysis["has_totals"] = True
                break
        
        # Verificar cumplimiento AFIP
        afip_matches = 0
        for pattern in self.afip_patterns.values():
            if re.search(pattern, text, re.IGNORECASE):
                afip_matches += 1
        
        analysis["is_afip_compliant"] = afip_matches >= 2  # Al menos 2 elementos AFIP
        
        # Calcular puntuación de estructura
        structure_elements = [
            analysis["has_header"],
            analysis["has_table_structure"], 
            analysis["has_totals"],
            analysis["is_afip_compliant"]
        ]
        
        analysis["structure_score"] = sum(structure_elements) / len(structure_elements)
        
        return analysis
    
    def get_regex_details(self, text: str, doc_type: str = None) -> Dict:
        """
        Obtiene detalles de coincidencias de regex para un tipo específico
        
        Args:
            text: Texto del documento
            doc_type: Tipo de documento a analizar (opcional)
            
        Returns:
            Diccionario con detalles de coincidencias
        """
        details = {}
        
        types_to_check = [doc_type] if doc_type else self.regex_patterns.keys()
        
        for doc_type_key in types_to_check:
            if doc_type_key not in self.regex_patterns:
                continue
                
            matches = {}
            for i, pattern in enumerate(self.regex_patterns[doc_type_key]):
                try:
                    found_matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if found_matches:
                        matches[f"pattern_{i+1}"] = {
                            "pattern": pattern,
                            "matches": found_matches,
                            "count": len(found_matches)
                        }
                except re.error as e:
                    matches[f"pattern_{i+1}"] = {
                        "pattern": pattern,
                        "error": str(e)
                    }
            
            if matches:
                details[doc_type_key] = matches
        
        return details
    
    def add_custom_pattern(self, doc_type: str, pattern: str):
        """
        Agrega un patrón regex personalizado para un tipo de documento
        
        Args:
            doc_type: Tipo de documento
            pattern: Patrón regex a agregar
        """
        if doc_type not in self.regex_patterns:
            self.regex_patterns[doc_type] = []
        
        try:
            # Validar que el patrón sea válido
            re.compile(pattern)
            self.regex_patterns[doc_type].append(pattern)
            logger.info(f"Patrón agregado para {doc_type}: {pattern}")
        except re.error as e:
            logger.error(f"Patrón regex inválido: {e}")
            raise ValueError(f"Patrón regex inválido: {e}")
    
    def get_supported_patterns(self) -> Dict:
        """
        Retorna todos los patrones soportados por tipo de documento
        
        Returns:
            Diccionario con patrones por tipo
        """
        return self.regex_patterns.copy()