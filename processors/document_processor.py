"""
Procesador principal de documentos PDF con clasificación inteligente
"""
import os
import psycopg2
import logging
import json
from datetime import datetime
from typing import Optional, Dict
from config import OUTPUT_DIR, DB_SCHEMA
from extractors import TextExtractor, MetadataExtractor
from classifiers import IntelligentClassifier
from validators import PDFValidator

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Procesador principal que coordina la extracción, clasificación y almacenamiento"""
    
    def __init__(self, enable_ml: bool = True, enable_layout: bool = True):
        self.text_extractor = TextExtractor()
        self.metadata_extractor = MetadataExtractor()
        self.intelligent_classifier = IntelligentClassifier(
            enable_ml=enable_ml, 
            enable_layout=enable_layout
        )
        self.pdf_validator = PDFValidator()
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos SQLite"""
        try:
            from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASSWORD,
                dbname=PG_DB
            )
            cur = conn.cursor()
            
            # Crear tabla con el esquema actualizado
            cur.execute(DB_SCHEMA["documentos"])
            conn.commit()
            conn.close()
            
            logger.info("Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def process_document(self, file_path: str) -> Dict:
        """
        Procesa un documento PDF completo
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con los resultados del procesamiento
        """
        result = {
            "success": False,
            "filename": os.path.basename(file_path),
            "error": None,
            "classification": None,
            "confidence": 0.0,
            "metadata": {},
            "destination": None
        }
        
        try:
            logger.info(f"Iniciando procesamiento de {file_path}")
            
            # 1. Validar archivo PDF
            if not self.pdf_validator.validate_pdf(file_path):
                result["error"] = "Archivo PDF inválido"
                return result
            
            # 2. Extraer texto
            text = self.text_extractor.extract_from_pdf(file_path)
            if not text:
                result["error"] = "No se pudo extraer texto del PDF"
                return result
            
            # 3. Clasificación inteligente
            classification_result = self.intelligent_classifier.classify_document(text, file_path)
            doc_type = classification_result["final_classification"]
            confidence = classification_result["final_confidence"]
            result["classification"] = doc_type
            result["confidence"] = confidence
            result["classification_analysis"] = classification_result
            
            # 4. Extraer metadatos
            metadata = self.metadata_extractor.extract_all_metadata(text)
            result["metadata"] = metadata
            
            # 5. Organizar archivo
            destination = self._organize_file(file_path, doc_type)
            result["destination"] = destination
            
            # 6. Guardar en base de datos
            self._save_to_database(
                filename=os.path.basename(file_path),
                doc_type=doc_type,
                confidence=confidence,
                metadata=metadata,
                classification_result=classification_result
            )
            
            result["success"] = True
            logger.info(f"Procesamiento exitoso: {file_path} → {doc_type} (confianza: {confidence:.2f})")
            
        except Exception as e:
            error_msg = f"Error procesando {file_path}: {e}"
            logger.error(error_msg)
            result["error"] = str(e)
        
        return result
    
    def _organize_file(self, file_path: str, doc_type: str) -> str:
        """
        Organiza el archivo en la carpeta correspondiente a su tipo
        
        Args:
            file_path: Ruta original del archivo
            doc_type: Tipo de documento clasificado
            
        Returns:
            Ruta del archivo organizado
        """
        # Crear carpeta destino
        dest_dir = os.path.join(OUTPUT_DIR, doc_type)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Generar nombre de destino
        filename = os.path.basename(file_path)
        dest_path = os.path.join(dest_dir, filename)
        
        # Si el archivo ya existe, agregar timestamp
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}{ext}"
            dest_path = os.path.join(dest_dir, filename)
        
        # Mover archivo
        os.rename(file_path, dest_path)
        logger.info(f"Archivo movido: {file_path} → {dest_path}")
        
        return dest_path
    
    def _save_to_database(self, filename: str, doc_type: str, confidence: float, 
                         metadata: Dict, classification_result: Dict = None):
        """
        Guarda la información del documento en la base de datos con datos de clasificación inteligente
        
        Args:
            filename: Nombre del archivo
            doc_type: Tipo de documento
            confidence: Confianza de la clasificación
            metadata: Metadatos extraídos
            classification_result: Resultado completo de la clasificación inteligente
        """
        try:
            from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASSWORD,
                dbname=PG_DB
            )
            cur = conn.cursor()
            
            # Extraer datos específicos de los metadatos
            cuit = metadata.get("cuit")
            supplier = metadata.get("supplier")
            dates = metadata.get("dates", [])
            amounts = metadata.get("amounts", [])
            
            # Usar la primera fecha encontrada como fecha del documento
            doc_date = dates[0] if dates else None
            # Usar el primer monto encontrado
            amount = amounts[0] if amounts else None
            
            # Información adicional de la clasificación inteligente
            supplier_id = None
            classification_details = None
            
            if classification_result:
                supplier_info = classification_result.get("supplier_info", {})
                supplier_id = supplier_info.get("supplier_id")
                
                # Función para convertir objetos no serializables
                def safe_serialize(obj):
                    if isinstance(obj, bool):
                        return obj
                    elif isinstance(obj, dict):
                        return {k: safe_serialize(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [safe_serialize(item) for item in obj]
                    else:
                        return str(obj) if obj is not None else None
                
                classification_data = {
                    "method_results": safe_serialize(classification_result.get("method_results", {})),
                    "decision_details": safe_serialize(classification_result.get("decision_details", {})),
                    "consensus_analysis": safe_serialize(classification_result.get("consensus_analysis", {}))
                }
                
                classification_details = json.dumps(classification_data, ensure_ascii=False, indent=2)
            
            cur.execute("""
                INSERT INTO documentos (
                    filename, tipo, cuit, proveedor, fecha_documento, 
                    monto, confidence, fecha_procesado, proveedor_id, 
                    detalles_clasificacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filename, doc_type, cuit, supplier, doc_date,
                amount, confidence, datetime.now().isoformat(),
                supplier_id, classification_details
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Documento guardado en BD: {filename}")
            
        except Exception as e:
            logger.error(f"Error guardando en BD: {e}")
            raise
    
    def get_processing_stats(self) -> Dict:
        """
        Obtiene estadísticas de procesamiento
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASSWORD,
                dbname=PG_DB
            )
            cur = conn.cursor()
            
            # Total de documentos
            cur.execute("SELECT COUNT(*) FROM documentos")
            total_docs = cur.fetchone()[0]
            
            # Documentos por tipo
            cur.execute("SELECT tipo, COUNT(*) FROM documentos GROUP BY tipo")
            docs_by_type = dict(cur.fetchall())
            
            # Confianza promedio
            cur.execute("SELECT AVG(confidence) FROM documentos")
            avg_confidence = cur.fetchone()[0] or 0
            
            conn.close()
            
            stats = {
                "total_documents": total_docs,
                "documents_by_type": docs_by_type,
                "average_confidence": round(avg_confidence, 3)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def reprocess_document(self, document_id: int) -> Dict:
        """
        Reprocesa un documento existente
        
        Args:
            document_id: ID del documento en la base de datos
            
        Returns:
            Resultado del reprocesamiento
        """
        # Esta funcionalidad se puede implementar más adelante
        # para permitir reprocessar documentos con nuevos clasificadores
        pass