"""
Clasificador basado en el layout y estructura visual del documento
"""
import fitz  # PyMuPDF
import logging
from typing import Dict, Tuple, List, Optional
import re
from collections import Counter

logger = logging.getLogger(__name__)


class LayoutClassifier:
    """Clasificador que analiza la estructura visual y layout del documento PDF"""
    
    def __init__(self):
        # Definición de zonas típicas del documento (porcentajes de la página)
        self.layout_zones = {
            "header": {"y_min": 0.0, "y_max": 0.15},      # 15% superior
            "title": {"y_min": 0.1, "y_max": 0.25},       # Zona de título
            "content": {"y_min": 0.2, "y_max": 0.8},      # Contenido principal
            "footer": {"y_min": 0.85, "y_max": 1.0},      # 15% inferior
            "left_margin": {"x_min": 0.0, "x_max": 0.15}, # Margen izquierdo
            "right_margin": {"x_min": 0.85, "x_max": 1.0} # Margen derecho
        }
        
        # Patrones de layout específicos por tipo de documento
        self.layout_patterns = {
            "facturas": {
                "title_keywords": ["factura", "invoice", "bill"],
                "required_sections": ["header_info", "item_table", "totals"],
                "table_indicators": ["código", "descripción", "cantidad", "precio"],
                "total_position": "bottom_right",
                "has_tax_section": True,
                "typical_font_sizes": [8, 10, 12, 14]
            },
            "remitos": {
                "title_keywords": ["remito", "delivery", "entrega"],
                "required_sections": ["header_info", "item_list"],
                "table_indicators": ["código", "artículo", "cantidad"],
                "total_position": "bottom_center",
                "has_tax_section": False,
                "typical_font_sizes": [8, 10, 12]
            },
            "notas_credito": {
                "title_keywords": ["nota de crédito", "credit note"],
                "required_sections": ["reference_doc", "credit_amount"],
                "table_indicators": ["concepto", "importe"],
                "total_position": "bottom_right",
                "has_tax_section": True,
                "typical_font_sizes": [8, 10, 12, 14]
            },
            "contratos": {
                "title_keywords": ["contrato", "contract", "acuerdo"],
                "required_sections": ["parties", "clauses", "signatures"],
                "table_indicators": [],  # Generalmente sin tablas
                "total_position": None,
                "has_tax_section": False,
                "typical_font_sizes": [10, 11, 12]
            }
        }
    
    def classify_by_layout(self, file_path: str) -> Tuple[str, float]:
        """
        Clasifica documento basado en su layout y estructura visual
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Tuple con (tipo_documento, confidence_score)
        """
        try:
            layout_analysis = self.analyze_document_layout(file_path)
            
            if not layout_analysis:
                return "desconocido", 0.0
            
            scores = {}
            
            for doc_type, pattern in self.layout_patterns.items():
                score = self._calculate_layout_score(layout_analysis, pattern)
                scores[doc_type] = score
            
            if not scores or max(scores.values()) == 0:
                return "desconocido", 0.0
            
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            
            logger.debug(f"Clasificación por layout: {best_type} (confianza: {best_score:.3f})")
            return best_type, best_score
            
        except Exception as e:
            logger.error(f"Error en clasificación por layout: {e}")
            return "desconocido", 0.0
    
    def analyze_document_layout(self, file_path: str) -> Optional[Dict]:
        """
        Analiza la estructura y layout del documento PDF
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con análisis de layout
        """
        try:
            with fitz.open(file_path) as doc:
                if len(doc) == 0:
                    return None
                
                # Analizar primera página (más representativa)
                page = doc[0]
                page_rect = page.rect
                
                # Obtener bloques de texto con posiciones
                blocks = page.get_text("dict")["blocks"]
                
                analysis = {
                    "page_dimensions": {
                        "width": page_rect.width,
                        "height": page_rect.height,
                        "aspect_ratio": page_rect.width / page_rect.height
                    },
                    "text_blocks": self._analyze_text_blocks(blocks, page_rect),
                    "font_analysis": self._analyze_fonts(blocks),
                    "spatial_distribution": self._analyze_spatial_distribution(blocks, page_rect),
                    "table_detection": self._detect_tables(blocks, page_rect),
                    "title_detection": self._detect_titles(blocks, page_rect)
                }
                
                return analysis
                
        except Exception as e:
            logger.error(f"Error analizando layout del documento {file_path}: {e}")
            return None
    
    def _analyze_text_blocks(self, blocks: List, page_rect) -> Dict:
        """Analiza los bloques de texto y su distribución"""
        text_blocks = []
        
        for block in blocks:
            if "lines" in block:  # Es un bloque de texto
                block_rect = fitz.Rect(block["bbox"])
                
                # Calcular posición normalizada (0-1)
                normalized_pos = {
                    "x_min": block_rect.x0 / page_rect.width,
                    "y_min": block_rect.y0 / page_rect.height,
                    "x_max": block_rect.x1 / page_rect.width,
                    "y_max": block_rect.y1 / page_rect.height,
                    "width": block_rect.width / page_rect.width,
                    "height": block_rect.height / page_rect.height
                }
                
                # Extraer texto del bloque
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"] + " "
                
                text_blocks.append({
                    "text": block_text.strip(),
                    "position": normalized_pos,
                    "zone": self._classify_zone(normalized_pos)
                })
        
        return {
            "total_blocks": len(text_blocks),
            "blocks": text_blocks,
            "zone_distribution": self._calculate_zone_distribution(text_blocks)
        }
    
    def _analyze_fonts(self, blocks: List) -> Dict:
        """Analiza los fonts utilizados en el documento"""
        font_sizes = []
        font_names = []
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(span["size"])
                        font_names.append(span["font"])
        
        font_size_counter = Counter(font_sizes)
        font_name_counter = Counter(font_names)
        
        return {
            "font_sizes": dict(font_size_counter),
            "font_names": dict(font_name_counter),
            "most_common_size": font_size_counter.most_common(1)[0] if font_size_counter else None,
            "size_variety": len(set(font_sizes)),
            "average_size": sum(font_sizes) / len(font_sizes) if font_sizes else 0
        }
    
    def _analyze_spatial_distribution(self, blocks: List, page_rect) -> Dict:
        """Analiza la distribución espacial del contenido"""
        x_positions = []
        y_positions = []
        
        for block in blocks:
            if "lines" in block:
                bbox = block["bbox"]
                x_positions.extend([bbox[0], bbox[2]])  # x_min, x_max
                y_positions.extend([bbox[1], bbox[3]])  # y_min, y_max
        
        if not x_positions or not y_positions:
            return {}
        
        return {
            "content_bounds": {
                "x_min": min(x_positions) / page_rect.width,
                "x_max": max(x_positions) / page_rect.width,
                "y_min": min(y_positions) / page_rect.height,
                "y_max": max(y_positions) / page_rect.height
            },
            "margin_analysis": {
                "left_margin": min(x_positions) / page_rect.width,
                "right_margin": 1.0 - (max(x_positions) / page_rect.width),
                "top_margin": min(y_positions) / page_rect.height,
                "bottom_margin": 1.0 - (max(y_positions) / page_rect.height)
            }
        }
    
    def _detect_tables(self, blocks: List, page_rect) -> Dict:
        """Detecta la presencia de tablas en el documento"""
        table_indicators = 0
        aligned_blocks = 0
        
        # Buscar patrones que indican tablas
        table_keywords = ["código", "descripción", "cantidad", "precio", "importe", "total"]
        
        for block in blocks:
            if "lines" in block:
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"].lower() + " "
                
                # Contar palabras clave de tabla
                for keyword in table_keywords:
                    if keyword in block_text:
                        table_indicators += 1
                
                # Detectar alineación (indicativo de tablas)
                lines = block["lines"]
                if len(lines) > 3:  # Múltiples líneas
                    x_positions = [line["bbox"][0] for line in lines]
                    if len(set(x_positions)) <= 2:  # Alineación consistente
                        aligned_blocks += 1
        
        return {
            "table_indicators": table_indicators,
            "aligned_blocks": aligned_blocks,
            "has_table_structure": table_indicators >= 3 or aligned_blocks >= 2
        }
    
    def _detect_titles(self, blocks: List, page_rect) -> Dict:
        """Detecta títulos y encabezados en el documento"""
        titles = []
        
        for block in blocks:
            if "lines" in block:
                block_rect = fitz.Rect(block["bbox"])
                
                # Verificar si está en la zona de título
                y_normalized = block_rect.y0 / page_rect.height
                if y_normalized > 0.25:  # No está en zona de título
                    continue
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        font_size = span["size"]
                        
                        # Criterios para considerar como título
                        if (len(text) > 5 and 
                            (font_size > 12 or text.isupper()) and
                            any(keyword in text.lower() for keyword in 
                                ["factura", "remito", "nota", "contrato", "recibo", "carta"])):
                            
                            titles.append({
                                "text": text,
                                "font_size": font_size,
                                "position": y_normalized
                            })
        
        return {
            "detected_titles": titles,
            "has_clear_title": len(titles) > 0,
            "title_count": len(titles)
        }
    
    def _classify_zone(self, position: Dict) -> str:
        """Clasifica en qué zona del documento está un bloque de texto"""
        y_center = (position["y_min"] + position["y_max"]) / 2
        x_center = (position["x_min"] + position["x_max"]) / 2
        
        if y_center <= self.layout_zones["header"]["y_max"]:
            return "header"
        elif y_center >= self.layout_zones["footer"]["y_min"]:
            return "footer"
        elif y_center <= self.layout_zones["title"]["y_max"]:
            return "title"
        else:
            return "content"
    
    def _calculate_zone_distribution(self, text_blocks: List) -> Dict:
        """Calcula la distribución de contenido por zonas"""
        zone_counts = Counter(block["zone"] for block in text_blocks)
        total_blocks = len(text_blocks)
        
        return {
            zone: count / total_blocks 
            for zone, count in zone_counts.items()
        } if total_blocks > 0 else {}
    
    def _calculate_layout_score(self, layout_analysis: Dict, pattern: Dict) -> float:
        """Calcula puntuación de coincidencia con patrón de layout"""
        score = 0.0
        max_score = 5.0  # Puntuación máxima
        
        try:
            # 1. Verificar palabras clave de título (peso: 1.0)
            titles = layout_analysis.get("title_detection", {}).get("detected_titles", [])
            title_score = 0.0
            
            for title in titles:
                title_text = title["text"].lower()
                for keyword in pattern["title_keywords"]:
                    if keyword in title_text:
                        title_score = 1.0
                        break
                if title_score > 0:
                    break
            
            score += title_score
            
            # 2. Verificar estructura de tabla (peso: 1.0)
            table_detection = layout_analysis.get("table_detection", {})
            if pattern["table_indicators"]:
                if table_detection.get("has_table_structure", False):
                    score += 1.0
            else:
                # Para documentos sin tabla (como contratos)
                if not table_detection.get("has_table_structure", True):
                    score += 0.5
            
            # 3. Verificar análisis de fonts (peso: 1.0)
            font_analysis = layout_analysis.get("font_analysis", {})
            typical_sizes = pattern.get("typical_font_sizes", [])
            
            if typical_sizes and font_analysis.get("most_common_size"):
                most_common = font_analysis["most_common_size"][0]
                if most_common in typical_sizes:
                    score += 1.0
                elif any(abs(most_common - size) <= 2 for size in typical_sizes):
                    score += 0.5
            
            # 4. Verificar distribución espacial (peso: 1.0)
            spatial = layout_analysis.get("spatial_distribution", {})
            if spatial:
                margins = spatial.get("margin_analysis", {})
                # Documentos comerciales típicamente tienen márgenes consistentes
                if (margins.get("left_margin", 0) > 0.05 and 
                    margins.get("right_margin", 0) > 0.05):
                    score += 0.5
                
                if (margins.get("top_margin", 0) > 0.05 and 
                    margins.get("bottom_margin", 0) > 0.05):
                    score += 0.5
            
            # 5. Verificar aspectos específicos del tipo (peso: 1.0)
            text_blocks = layout_analysis.get("text_blocks", {}).get("blocks", [])
            
            # Buscar indicadores específicos en el texto
            full_text = " ".join(block["text"].lower() for block in text_blocks)
            
            type_specific_score = 0.0
            if pattern.get("has_tax_section"):
                if any(tax_term in full_text for tax_term in ["iva", "impuesto", "tax"]):
                    type_specific_score += 0.5
            
            # Buscar indicadores de tabla específicos
            table_terms_found = sum(
                1 for term in pattern["table_indicators"] 
                if term in full_text
            )
            
            if pattern["table_indicators"]:
                type_specific_score += min(table_terms_found / len(pattern["table_indicators"]), 0.5)
            
            score += type_specific_score
            
            # Normalizar puntuación
            normalized_score = min(score / max_score, 1.0)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error calculando puntuación de layout: {e}")
            return 0.0
    
    def get_layout_report(self, file_path: str) -> Dict:
        """
        Genera un reporte completo del análisis de layout
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con reporte completo
        """
        layout_analysis = self.analyze_document_layout(file_path)
        
        if not layout_analysis:
            return {"error": "No se pudo analizar el layout del documento"}
        
        # Calcular puntuaciones para todos los tipos
        type_scores = {}
        for doc_type, pattern in self.layout_patterns.items():
            score = self._calculate_layout_score(layout_analysis, pattern)
            type_scores[doc_type] = score
        
        best_match = max(type_scores, key=type_scores.get) if type_scores else "desconocido"
        
        return {
            "layout_analysis": layout_analysis,
            "type_scores": type_scores,
            "best_match": best_match,
            "confidence": type_scores.get(best_match, 0.0)
        }