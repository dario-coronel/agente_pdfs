"""
Detectector específico de proveedores y sus patrones de documentos
"""
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SupplierDetector:
    """Detecta proveedores específicos y sus patrones de documentos característicos"""
    
    def __init__(self, suppliers_db_path: str = "config/suppliers_db.json"):
        self.suppliers_db_path = suppliers_db_path
        self.suppliers_db = {}
        self._load_suppliers_db()
        
        # Patrones generales para detectar información de proveedores
        self.general_patterns = {
            "razón_social": [
                r"RAZÓN\s+SOCIAL\s*:?\s*([A-Z\s&\.]{5,50})",
                r"EMPRESA\s*:?\s*([A-Z\s&\.]{5,50})",
                r"PROVEEDOR\s*:?\s*([A-Z\s&\.]{5,50})"
            ],
            "nombre_comercial": [
                r"NOMBRE\s+COMERCIAL\s*:?\s*([A-Z\s&\.]{3,30})",
                r"DENOMINACIÓN\s*:?\s*([A-Z\s&\.]{3,30})"
            ],
            "cuit_empresa": [
                r"CUIT\s*:?\s*(\d{2}-\d{8}-\d)",
                r"C\.U\.I\.T\.?\s*:?\s*(\d{2}-\d{8}-\d)"
            ],
            "domicilio": [
                r"DOMICILIO\s*:?\s*([A-Za-z\s\d\.]{10,80})",
                r"DIRECCIÓN\s*:?\s*([A-Za-z\s\d\.]{10,80})"
            ],
            "teléfono": [
                r"TEL[ÉE]FONO\s*:?\s*([\d\s\-\(\)]{8,20})",
                r"TEL\s*:?\s*([\d\s\-\(\)]{8,20})"
            ]
        }
    
    def _load_suppliers_db(self):
        """Carga la base de datos de proveedores conocidos"""
        try:
            suppliers_file = Path(self.suppliers_db_path)
            
            if suppliers_file.exists():
                with open(suppliers_file, 'r', encoding='utf-8') as f:
                    self.suppliers_db = json.load(f)
                logger.info(f"Base de datos de proveedores cargada: {len(self.suppliers_db)} proveedores")
            else:
                # Crear base de datos inicial con ejemplos
                self._create_default_suppliers_db()
                
        except Exception as e:
            logger.error(f"Error cargando base de datos de proveedores: {e}")
            self._create_default_suppliers_db()
    
    def _create_default_suppliers_db(self):
        """Crea una base de datos inicial con proveedores de ejemplo"""
        default_suppliers = {
            "telecom_argentina": {
                "names": ["TELECOM ARGENTINA", "TELECOM", "PERSONAL"],
                "cuit": "30-50000109-4",
                "document_patterns": {
                    "facturas": {
                        "specific_terms": ["SERVICIOS DE TELECOMUNICACIONES", "PLAN PERSONAL"],
                        "layout_indicators": ["CONSUMO DEL PERÍODO", "PRÓXIMO VENCIMIENTO"],
                        "confidence_boost": 0.3
                    }
                },
                "contact_info": {
                    "website": "www.telecom.com.ar",
                    "phone": "0800-555-0000"
                }
            },
            "edesur": {
                "names": ["EDESUR S.A.", "EMPRESA DISTRIBUIDORA SUR"],
                "cuit": "30-65511620-2",
                "document_patterns": {
                    "facturas": {
                        "specific_terms": ["DISTRIBUCIÓN ELÉCTRICA", "ENERGÍA CONSUMIDA", "CARGO FIJO"],
                        "layout_indicators": ["KWH CONSUMIDOS", "PRÓXIMO VENCIMIENTO"],
                        "confidence_boost": 0.3
                    }
                }
            },
            "metrogas": {
                "names": ["METROGAS S.A.", "DISTRIBUIDORA DE GAS"],
                "cuit": "30-61469304-9",
                "document_patterns": {
                    "facturas": {
                        "specific_terms": ["DISTRIBUCIÓN DE GAS", "M3 CONSUMIDOS", "GAS NATURAL"],
                        "layout_indicators": ["MEDICIÓN ANTERIOR", "MEDICIÓN ACTUAL"],
                        "confidence_boost": 0.3
                    }
                }
            },
            "mercadolibre": {
                "names": ["MERCADOLIBRE S.R.L.", "MELI", "MERCADO LIBRE"],
                "cuit": "30-70308853-4",
                "document_patterns": {
                    "facturas": {
                        "specific_terms": ["COMISIÓN POR VENTA", "MARKETPLACE", "PUBLICACIÓN"],
                        "layout_indicators": ["DETALLE DE VENTAS", "COMISIONES"],
                        "confidence_boost": 0.2
                    },
                    "recibos": {
                        "specific_terms": ["COBRO AUTOMÁTICO", "DÉBITO AUTOMÁTICO"],
                        "layout_indicators": ["MEDIO DE PAGO"],
                        "confidence_boost": 0.2
                    }
                }
            },
            "andreani": {
                "names": ["ANDREANI LOGÍSTICA S.A.", "ANDREANI", "GRUPO ANDREANI"],
                "cuit": "30-50010085-2",
                "document_patterns": {
                    "cartas_porte": {
                        "specific_terms": ["TRANSPORTE DE CORRESPONDENCIA", "COURIER", "ENVÍO"],
                        "layout_indicators": ["DESTINATARIO", "REMITENTE", "CÓDIGO DE SEGUIMIENTO"],
                        "confidence_boost": 0.4
                    },
                    "remitos": {
                        "specific_terms": ["ENTREGA A DOMICILIO", "SERVICIO PUERTA A PUERTA"],
                        "layout_indicators": ["TRACKING", "CÓDIGO POSTAL"],
                        "confidence_boost": 0.3
                    }
                }
            }
        }
        
        self.suppliers_db = default_suppliers
        self._save_suppliers_db()
    
    def _save_suppliers_db(self):
        """Guarda la base de datos de proveedores"""
        try:
            suppliers_file = Path(self.suppliers_db_path)
            suppliers_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(suppliers_file, 'w', encoding='utf-8') as f:
                json.dump(self.suppliers_db, f, indent=2, ensure_ascii=False)
                
            logger.info("Base de datos de proveedores guardada")
            
        except Exception as e:
            logger.error(f"Error guardando base de datos de proveedores: {e}")
    
    def detect_supplier(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detecta el proveedor específico del documento
        
        Args:
            text: Texto del documento
            
        Returns:
            Tuple con (id_proveedor, confidence_score)
        """
        best_supplier = None
        best_score = 0.0
        
        text_upper = text.upper()
        
        for supplier_id, supplier_data in self.suppliers_db.items():
            score = self._calculate_supplier_score(text_upper, supplier_data)
            
            if score > best_score:
                best_score = score
                best_supplier = supplier_id
        
        # Solo retornar si la confianza es suficiente
        if best_score >= 0.3:  # Umbral mínimo de confianza
            logger.debug(f"Proveedor detectado: {best_supplier} (confianza: {best_score:.3f})")
            return best_supplier, best_score
        
        return None, 0.0
    
    def _calculate_supplier_score(self, text: str, supplier_data: Dict) -> float:
        """Calcula la puntuación de coincidencia con un proveedor específico"""
        score = 0.0
        
        # 1. Verificar nombres del proveedor (peso: 0.4)
        name_score = 0.0
        for name in supplier_data.get("names", []):
            if name.upper() in text:
                name_score = 0.4
                break
            # Búsqueda parcial para nombres largos
            elif len(name) > 10:
                name_words = name.upper().split()
                if len(name_words) >= 2:
                    found_words = sum(1 for word in name_words if word in text)
                    if found_words >= 2:
                        name_score = 0.3
        
        score += name_score
        
        # 2. Verificar CUIT (peso: 0.3)
        cuit = supplier_data.get("cuit", "")
        if cuit and cuit in text:
            score += 0.3
        
        # 3. Verificar patrones específicos del documento (peso: 0.3)
        pattern_score = 0.0
        document_patterns = supplier_data.get("document_patterns", {})
        
        for doc_type, patterns in document_patterns.items():
            type_score = 0.0
            
            # Términos específicos
            specific_terms = patterns.get("specific_terms", [])
            terms_found = sum(1 for term in specific_terms if term.upper() in text)
            if specific_terms:
                type_score += (terms_found / len(specific_terms)) * 0.2
            
            # Indicadores de layout
            layout_indicators = patterns.get("layout_indicators", [])
            indicators_found = sum(1 for indicator in layout_indicators if indicator.upper() in text)
            if layout_indicators:
                type_score += (indicators_found / len(layout_indicators)) * 0.1
            
            pattern_score = max(pattern_score, type_score)
        
        score += pattern_score
        
        return min(score, 1.0)  # Normalizar a máximo 1.0
    
    def get_supplier_info(self, supplier_id: str) -> Optional[Dict]:
        """
        Obtiene información completa de un proveedor
        
        Args:
            supplier_id: ID del proveedor
            
        Returns:
            Diccionario con información del proveedor o None
        """
        return self.suppliers_db.get(supplier_id)
    
    def extract_supplier_data(self, text: str) -> Dict:
        """
        Extrae información general del proveedor del texto
        
        Args:
            text: Texto del documento
            
        Returns:
            Diccionario con datos extraídos del proveedor
        """
        extracted_data = {}
        
        for field, patterns in self.general_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted_data[field] = match.group(1).strip()
                    break
        
        return extracted_data
    
    def get_supplier_classification_boost(self, supplier_id: str, doc_type: str) -> float:
        """
        Obtiene el boost de confianza para una clasificación específica
        
        Args:
            supplier_id: ID del proveedor detectado
            doc_type: Tipo de documento clasificado
            
        Returns:
            Valor de boost para la confianza (0.0 a 0.5)
        """
        supplier_data = self.suppliers_db.get(supplier_id)
        if not supplier_data:
            return 0.0
        
        document_patterns = supplier_data.get("document_patterns", {})
        doc_patterns = document_patterns.get(doc_type, {})
        
        return doc_patterns.get("confidence_boost", 0.0)
    
    def add_supplier(self, supplier_id: str, supplier_data: Dict):
        """
        Agrega un nuevo proveedor a la base de datos
        
        Args:
            supplier_id: ID único del proveedor
            supplier_data: Datos del proveedor
        """
        self.suppliers_db[supplier_id] = supplier_data
        self._save_suppliers_db()
        logger.info(f"Proveedor agregado: {supplier_id}")
    
    def update_supplier_patterns(self, supplier_id: str, doc_type: str, 
                                new_terms: List[str] = None, new_indicators: List[str] = None):
        """
        Actualiza los patrones de un proveedor basado en nuevos documentos
        
        Args:
            supplier_id: ID del proveedor
            doc_type: Tipo de documento
            new_terms: Nuevos términos específicos encontrados
            new_indicators: Nuevos indicadores de layout encontrados
        """
        if supplier_id not in self.suppliers_db:
            logger.warning(f"Proveedor {supplier_id} no encontrado")
            return
        
        supplier_data = self.suppliers_db[supplier_id]
        
        # Inicializar estructura si no existe
        if "document_patterns" not in supplier_data:
            supplier_data["document_patterns"] = {}
        
        if doc_type not in supplier_data["document_patterns"]:
            supplier_data["document_patterns"][doc_type] = {
                "specific_terms": [],
                "layout_indicators": [],
                "confidence_boost": 0.1
            }
        
        patterns = supplier_data["document_patterns"][doc_type]
        
        # Agregar nuevos términos únicos
        if new_terms:
            existing_terms = set(term.upper() for term in patterns["specific_terms"])
            for term in new_terms:
                if term.upper() not in existing_terms:
                    patterns["specific_terms"].append(term)
        
        # Agregar nuevos indicadores únicos
        if new_indicators:
            existing_indicators = set(ind.upper() for ind in patterns["layout_indicators"])
            for indicator in new_indicators:
                if indicator.upper() not in existing_indicators:
                    patterns["layout_indicators"].append(indicator)
        
        self._save_suppliers_db()
        logger.info(f"Patrones actualizados para {supplier_id} - {doc_type}")
    
    def get_all_suppliers(self) -> Dict:
        """Retorna todos los proveedores en la base de datos"""
        return self.suppliers_db.copy()
    
    def search_suppliers(self, query: str) -> List[Dict]:
        """
        Busca proveedores por nombre, CUIT o términos
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de proveedores coincidentes
        """
        results = []
        query_upper = query.upper()
        
        for supplier_id, supplier_data in self.suppliers_db.items():
            # Buscar en nombres
            names_match = any(query_upper in name.upper() for name in supplier_data.get("names", []))
            
            # Buscar en CUIT
            cuit_match = query_upper in supplier_data.get("cuit", "")
            
            if names_match or cuit_match:
                results.append({
                    "id": supplier_id,
                    "data": supplier_data,
                    "match_score": 1.0 if cuit_match else 0.8
                })
        
        # Ordenar por score de coincidencia
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results