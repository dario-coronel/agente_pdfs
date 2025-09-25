"""
Clasificador inteligente que         # Pesos para cada método de clasificación (suman 1.0)
        self.classification_weights = {
            "keyword": 0.18,      # Clasificación por palabras clave
            "regex": 0.20,        # Patrones regex específicos
            "ml": 0.12,           # Machine Learning (si está disponible)
            "layout": 0.10,       # Análisis de estructura visual
            "agro": 0.20,         # Clasificación agropecuaria especializada
            "commercial": 0.15,   # Clasificación comercial especializada
            "supplier": 0.05      # Boost por proveedor específico
        }últiples métodos con pesos ajustables
"""
import logging
from typing import Dict, Tuple, List, Optional
from .document_classifier import DocumentClassifier
from .regex_classifier import RegexClassifier
from .ml_classifier import MLClassifier
from .layout_classifier import LayoutClassifier
from .supplier_detector import SupplierDetector
from .agro_classifier import AgroDocumentClassifier
from .commercial_classifier import CommercialDocumentClassifier

logger = logging.getLogger(__name__)


class IntelligentClassifier:
    """
    Clasificador inteligente que combina múltiples métodos de clasificación
    con pesos ajustables y lógica de decisión avanzada
    """
    
    def __init__(self, enable_ml: bool = True, enable_layout: bool = True, enable_agro: bool = True, enable_commercial: bool = True):
        # Inicializar clasificadores
        self.keyword_classifier = DocumentClassifier()
        self.regex_classifier = RegexClassifier()
        self.supplier_detector = SupplierDetector()
        
        # Clasificadores opcionales (más costosos computacionalmente)
        self.ml_classifier = MLClassifier() if enable_ml else None
        self.layout_classifier = LayoutClassifier() if enable_layout else None
        self.agro_classifier = AgroDocumentClassifier() if enable_agro else None
        self.commercial_classifier = CommercialDocumentClassifier() if enable_commercial else None
        
        # Pesos para cada método de clasificación (suman 1.0)
        # Los clasificadores especializados tienen más peso
        self.classification_weights = {
            "keyword": 0.15,      # Clasificación por palabras clave
            "regex": 0.15,        # Patrones regex específicos  
            "ml": 0.10,           # Machine Learning (si está disponible)
            "layout": 0.08,       # Análisis de estructura visual
            "agro": 0.25,         # Clasificación agropecuaria especializada (MAYOR PESO)
            "commercial": 0.22,   # Clasificación comercial especializada (MAYOR PESO)
            "supplier": 0.05      # Boost por proveedor específico
        }
        
        # Configuración de confianza mínima
        self.min_confidence_threshold = 0.15  # Reducido para permitir clasificaciones con un solo método fuerte
        self.high_confidence_threshold = 0.8
        
        # Configuración de consenso (mínimo de métodos que deben coincidir)
        self.consensus_requirements = {
            "high_confidence": 2,   # Al menos 2 métodos para alta confianza
            "medium_confidence": 1,  # Al menos 1 método para confianza media
            "supplier_boost": 0.15   # Boost adicional si se detecta proveedor
        }
    
    def classify_document(self, text: str, file_path: str = None) -> Dict:
        """
        Clasifica un documento usando todos los métodos disponibles
        
        Args:
            text: Texto del documento
            file_path: Ruta al archivo PDF (opcional, para análisis de layout)
            
        Returns:
            Diccionario con clasificación completa y detalles
        """
        results = {
            "final_classification": "desconocido",
            "final_confidence": 0.0,
            "method_results": {},
            "supplier_info": None,
            "consensus_analysis": {},
            "decision_details": {}
        }
        
        try:
            # 1. Clasificación por palabras clave
            keyword_type, keyword_conf = self.keyword_classifier.classify_document(text)
            results["method_results"]["keyword"] = {
                "type": keyword_type,
                "confidence": keyword_conf
            }
            
            # 2. Clasificación por regex
            regex_type, regex_conf = self.regex_classifier.classify_by_regex(text)
            results["method_results"]["regex"] = {
                "type": regex_type,
                "confidence": regex_conf
            }
            
            # 3. Detección de proveedor
            supplier_id, supplier_conf = self.supplier_detector.detect_supplier(text)
            results["supplier_info"] = {
                "supplier_id": supplier_id,
                "confidence": supplier_conf,
                "data": self.supplier_detector.get_supplier_info(supplier_id) if supplier_id else None
            }
            
            # 3.5. Clasificación agropecuaria especializada (si está disponible)
            if self.agro_classifier:
                try:
                    agro_type, agro_conf, agro_details = self.agro_classifier.classify_agro_document(text)
                    results["method_results"]["agro"] = {
                        "type": agro_type,
                        "confidence": agro_conf,
                        "details": agro_details,
                        "is_agro_document": agro_conf > 0.3
                    }
                except Exception as e:
                    logger.warning(f"Error en clasificación agropecuaria: {e}")
                    results["method_results"]["agro"] = {
                        "type": "desconocido",
                        "confidence": 0.0,
                        "error": str(e)
                    }
            
            # 3.6. Clasificación comercial especializada (si está disponible)
            if self.commercial_classifier:
                try:
                    commercial_type, commercial_conf, commercial_details = self.commercial_classifier.classify_commercial_document(text)
                    results["method_results"]["commercial"] = {
                        "type": commercial_type,
                        "confidence": commercial_conf,
                        "details": commercial_details,
                        "is_commercial_document": commercial_conf > 0.3
                    }
                except Exception as e:
                    logger.warning(f"Error en clasificación comercial: {e}")
                    results["method_results"]["commercial"] = {
                        "type": "desconocido",
                        "confidence": 0.0,
                        "error": str(e)
                    }
            
            # 4. Machine Learning (si está disponible)
            if self.ml_classifier:
                try:
                    ml_type, ml_conf = self.ml_classifier.classify_by_ml(text)
                    results["method_results"]["ml"] = {
                        "type": ml_type,
                        "confidence": ml_conf
                    }
                except Exception as e:
                    logger.warning(f"Error en clasificación ML: {e}")
                    results["method_results"]["ml"] = {
                        "type": "desconocido",
                        "confidence": 0.0,
                        "error": str(e)
                    }
            
            # 5. Análisis de layout (si está disponible y se proporciona archivo)
            if self.layout_classifier and file_path:
                try:
                    layout_type, layout_conf = self.layout_classifier.classify_by_layout(file_path)
                    results["method_results"]["layout"] = {
                        "type": layout_type,
                        "confidence": layout_conf
                    }
                except Exception as e:
                    logger.warning(f"Error en clasificación por layout: {e}")
                    results["method_results"]["layout"] = {
                        "type": "desconocido",
                        "confidence": 0.0,
                        "error": str(e)
                    }
            
            # 6. Análisis de consenso y decisión final
            consensus_analysis = self._analyze_consensus(results["method_results"])
            results["consensus_analysis"] = consensus_analysis
            
            # 7. Calcular clasificación final
            final_classification, final_confidence, decision_details = self._calculate_final_classification(
                results["method_results"], 
                results["supplier_info"], 
                consensus_analysis
            )
            
            results["final_classification"] = final_classification
            results["final_confidence"] = final_confidence
            results["decision_details"] = decision_details
            
            logger.info(f"Clasificación inteligente: {final_classification} (confianza: {final_confidence:.3f})")
            
        except Exception as e:
            logger.error(f"Error en clasificación inteligente: {e}")
            results["error"] = str(e)
        
        return results
    
    def _analyze_consensus(self, method_results: Dict) -> Dict:
        """Analiza el consenso entre diferentes métodos de clasificación"""
        
        # Agrupar resultados por tipo de documento predicho
        type_votes = {}
        total_methods = 0
        
        for method, result in method_results.items():
            if result.get("confidence", 0) > 0.1:  # Solo considerar resultados con confianza mínima
                doc_type = result["type"]
                confidence = result["confidence"]
                
                if doc_type not in type_votes:
                    type_votes[doc_type] = []
                
                type_votes[doc_type].append({
                    "method": method,
                    "confidence": confidence
                })
                total_methods += 1
        
        # Calcular estadísticas de consenso
        consensus_stats = {}
        
        for doc_type, votes in type_votes.items():
            vote_count = len(votes)
            avg_confidence = sum(vote["confidence"] for vote in votes) / vote_count
            max_confidence = max(vote["confidence"] for vote in votes)
            
            consensus_stats[doc_type] = {
                "vote_count": vote_count,
                "vote_percentage": vote_count / total_methods if total_methods > 0 else 0,
                "avg_confidence": avg_confidence,
                "max_confidence": max_confidence,
                "supporting_methods": [vote["method"] for vote in votes]
            }
        
        # Identificar el consenso más fuerte
        best_consensus = None
        if consensus_stats:
            best_consensus = max(
                consensus_stats.keys(),
                key=lambda k: (
                    consensus_stats[k]["vote_count"],
                    consensus_stats[k]["avg_confidence"]
                )
            )
        
        return {
            "type_votes": type_votes,
            "consensus_stats": consensus_stats,
            "best_consensus": best_consensus,
            "total_methods": total_methods,
            "has_strong_consensus": (
                best_consensus and 
                consensus_stats[best_consensus]["vote_count"] >= 2 and
                consensus_stats[best_consensus]["avg_confidence"] >= 0.5
            )
        }
    
    def _calculate_final_classification(self, method_results: Dict, 
                                      supplier_info: Dict, 
                                      consensus_analysis: Dict) -> Tuple[str, float, Dict]:
        """Calcula la clasificación final usando pesos y lógica de decisión"""
        
        # **LÓGICA ESPECIAL**: Prioridad para clasificador agropecuario con alta confianza
        agro_result = method_results.get("agro")
        if (agro_result and 
            agro_result.get("confidence", 0) >= 0.9 and 
            agro_result.get("is_agro_document", False)):
            
            # Boost significativo para documentos agropecuarios con muy alta confianza
            agro_type = agro_result["type"]
            agro_confidence = agro_result["confidence"]
            boosted_confidence = min(agro_confidence * self.classification_weights["agro"] + 0.3, 1.0)
            
            decision_details = {
                "method_contributions": {"agro": {
                    "type": agro_type,
                    "confidence": agro_confidence,
                    "weight": self.classification_weights["agro"],
                    "contribution": boosted_confidence
                }},
                "supplier_boost": 0.0,
                "consensus_factor": 0.0,
                "agro_priority_boost": 0.3,
                "final_reasoning": f"Documento agropecuario detectado con alta confianza ({agro_confidence:.3f}) - prioridad automática"
            }
            
            logger.info(f"🌾 Prioridad agropecuaria aplicada: {agro_type} (confianza: {boosted_confidence:.3f})")
            return agro_type, boosted_confidence, decision_details
        
        # **LÓGICA ESPECIAL**: Prioridad para clasificador comercial con alta confianza
        commercial_result = method_results.get("commercial")
        if (commercial_result and 
            commercial_result.get("confidence", 0) >= 0.9 and 
            commercial_result.get("is_commercial_document", False)):
            
            # Boost significativo para documentos comerciales con muy alta confianza
            commercial_type = commercial_result["type"]
            commercial_confidence = commercial_result["confidence"]
            boosted_confidence = min(commercial_confidence * self.classification_weights["commercial"] + 0.25, 1.0)
            
            decision_details = {
                "method_contributions": {"commercial": {
                    "type": commercial_type,
                    "confidence": commercial_confidence,
                    "weight": self.classification_weights["commercial"],
                    "contribution": boosted_confidence
                }},
                "supplier_boost": 0.0,
                "consensus_factor": 0.0,
                "commercial_priority_boost": 0.25,
                "final_reasoning": f"Documento comercial detectado con alta confianza ({commercial_confidence:.3f}) - prioridad automática"
            }
            
            logger.info(f"💼 Prioridad comercial aplicada: {commercial_type} (confianza: {boosted_confidence:.3f})")
            return commercial_type, boosted_confidence, decision_details
        
        # Calcular puntuaciones ponderadas (lógica normal)
        weighted_scores = {}
        decision_details = {
            "method_contributions": {},
            "supplier_boost": 0.0,
            "consensus_factor": 0.0,
            "final_reasoning": ""
        }
        
        # 1. Aplicar pesos a cada método
        for method, weight in self.classification_weights.items():
            if method == "supplier":  # El supplier no clasifica directamente
                continue
                
            result = method_results.get(method)
            if result and result.get("confidence", 0) > 0:
                doc_type = result["type"]
                confidence = result["confidence"]
                weighted_contribution = confidence * weight
                
                if doc_type not in weighted_scores:
                    weighted_scores[doc_type] = 0.0
                
                weighted_scores[doc_type] += weighted_contribution
                
                decision_details["method_contributions"][method] = {
                    "type": doc_type,
                    "confidence": confidence,
                    "weight": weight,
                    "contribution": weighted_contribution
                }
        
        # 2. Aplicar boost por proveedor específico
        supplier_id = supplier_info.get("supplier_id")
        if supplier_id and weighted_scores:
            # Aplicar boost al tipo más probable
            best_type = max(weighted_scores, key=weighted_scores.get)
            supplier_boost = self.supplier_detector.get_supplier_classification_boost(
                supplier_id, best_type
            )
            
            if supplier_boost > 0:
                weighted_scores[best_type] += supplier_boost
                decision_details["supplier_boost"] = supplier_boost
                decision_details["supplier_id"] = supplier_id
        
        # 3. Aplicar factor de consenso
        consensus_stats = consensus_analysis.get("consensus_stats", {})
        if consensus_analysis.get("has_strong_consensus"):
            best_consensus = consensus_analysis["best_consensus"]
            if best_consensus in weighted_scores:
                consensus_boost = 0.1 * consensus_stats[best_consensus]["vote_percentage"]
                weighted_scores[best_consensus] += consensus_boost
                decision_details["consensus_factor"] = consensus_boost
        
        # 4. Determinar clasificación final
        if not weighted_scores:
            return "desconocido", 0.0, decision_details
        
        # Agregar weighted_scores al debug
        decision_details["weighted_scores"] = weighted_scores.copy()
        
        final_type = max(weighted_scores, key=weighted_scores.get)
        raw_confidence = weighted_scores[final_type]
        
        # 5. Ajustar confianza según factores adicionales
        final_confidence = min(raw_confidence, 1.0)
        
        # Penalizar si no hay consenso suficiente
        if not consensus_analysis.get("has_strong_consensus") and final_confidence > 0.7:
            final_confidence *= 0.9  # Reducir ligeramente la confianza
            decision_details["consensus_penalty"] = 0.1
        
        # 6. Aplicar umbral mínimo
        if final_confidence < self.min_confidence_threshold:
            final_type = "desconocido"
            final_confidence = 0.0
        
        # 7. Generar explicación del razonamiento
        decision_details["final_reasoning"] = self._generate_decision_reasoning(
            final_type, final_confidence, method_results, supplier_info, consensus_analysis
        )
        
        return final_type, final_confidence, decision_details
    
    def _generate_decision_reasoning(self, final_type: str, final_confidence: float,
                                   method_results: Dict, supplier_info: Dict,
                                   consensus_analysis: Dict) -> str:
        """Genera una explicación textual del proceso de decisión"""
        
        reasoning_parts = []
        
        # Métodos que contribuyeron
        contributing_methods = []
        for method, result in method_results.items():
            if result.get("confidence", 0) > 0.1 and result.get("type") == final_type:
                contributing_methods.append(f"{method} ({result['confidence']:.2f})")
        
        if contributing_methods:
            reasoning_parts.append(f"Métodos coincidentes: {', '.join(contributing_methods)}")
        
        # Consenso
        if consensus_analysis.get("has_strong_consensus"):
            best_consensus = consensus_analysis["best_consensus"]
            vote_count = consensus_analysis["consensus_stats"][best_consensus]["vote_count"]
            reasoning_parts.append(f"Consenso fuerte: {vote_count} métodos coinciden")
        
        # Proveedor específico
        supplier_id = supplier_info.get("supplier_id")
        if supplier_id:
            reasoning_parts.append(f"Proveedor detectado: {supplier_id}")
        
        # Nivel de confianza
        if final_confidence >= self.high_confidence_threshold:
            confidence_desc = "Alta confianza"
        elif final_confidence >= self.min_confidence_threshold:
            confidence_desc = "Confianza media"
        else:
            confidence_desc = "Baja confianza"
        
        reasoning_parts.append(f"{confidence_desc} ({final_confidence:.3f})")
        
        return " | ".join(reasoning_parts) if reasoning_parts else "Clasificación incierta"
    
    def get_detailed_analysis(self, text: str, file_path: str = None) -> Dict:
        """
        Obtiene un análisis detallado de todos los métodos de clasificación
        
        Args:
            text: Texto del documento
            file_path: Ruta al archivo PDF (opcional)
            
        Returns:
            Diccionario con análisis completo y detallado
        """
        # Clasificación principal
        classification_result = self.classify_document(text, file_path)
        
        # Análisis adicional por método
        detailed_analysis = {
            "classification": classification_result,
            "method_details": {}
        }
        
        # Detalles de clasificación por palabras clave
        keyword_details = self.keyword_classifier.get_classification_details(text)
        detailed_analysis["method_details"]["keyword"] = keyword_details
        
        # Detalles de clasificación por regex
        regex_details = self.regex_classifier.get_regex_details(text)
        detailed_analysis["method_details"]["regex"] = regex_details
        
        # Detalles del proveedor
        supplier_data = self.supplier_detector.extract_supplier_data(text)
        detailed_analysis["method_details"]["supplier"] = supplier_data
        
        # Detalles de ML (si está disponible)
        if self.ml_classifier:
            try:
                ml_probabilities = self.ml_classifier.get_classification_probabilities(text)
                detailed_analysis["method_details"]["ml"] = {
                    "probabilities": ml_probabilities
                }
            except Exception as e:
                detailed_analysis["method_details"]["ml"] = {"error": str(e)}
        
        # Detalles de layout (si está disponible)
        if self.layout_classifier and file_path:
            try:
                layout_report = self.layout_classifier.get_layout_report(file_path)
                detailed_analysis["method_details"]["layout"] = layout_report
            except Exception as e:
                detailed_analysis["method_details"]["layout"] = {"error": str(e)}
        
        return detailed_analysis
    
    def adjust_weights(self, new_weights: Dict):
        """
        Ajusta los pesos de los métodos de clasificación
        
        Args:
            new_weights: Diccionario con nuevos pesos
        """
        # Validar que los pesos sumen aproximadamente 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.1:
            logger.warning(f"Los pesos no suman 1.0 (suma: {total_weight})")
        
        self.classification_weights.update(new_weights)
        logger.info(f"Pesos actualizados: {self.classification_weights}")
    
    def get_performance_metrics(self) -> Dict:
        """Obtiene métricas de rendimiento de cada clasificador"""
        metrics = {
            "available_methods": [],
            "method_status": {}
        }
        
        # Estado de cada método
        metrics["method_status"]["keyword"] = {"available": True, "trained": True}
        metrics["method_status"]["regex"] = {"available": True, "trained": True}
        metrics["method_status"]["supplier"] = {
            "available": True, 
            "suppliers_count": len(self.supplier_detector.get_all_suppliers())
        }
        
        if self.ml_classifier:
            metrics["method_status"]["ml"] = {
                "available": True,
                "trained": self.ml_classifier.is_trained
            }
            metrics["available_methods"].append("ml")
        
        if self.layout_classifier:
            metrics["method_status"]["layout"] = {"available": True, "trained": True}
            metrics["available_methods"].append("layout")
        
        if self.agro_classifier:
            metrics["method_status"]["agro"] = {"available": True, "specialized": True}
            metrics["available_methods"].append("agro")
        
        if self.commercial_classifier:
            metrics["method_status"]["commercial"] = {"available": True, "specialized": True}
            metrics["available_methods"].append("commercial")
        
        metrics["available_methods"].extend(["keyword", "regex", "supplier"])
        
        return metrics