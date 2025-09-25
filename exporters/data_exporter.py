"""
Exportador de datos a diferentes formatos
"""
import csv
import json
import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime
from config import DB_PATH

logger = logging.getLogger(__name__)


class DataExporter:
    """Exporta datos de la base de datos a diferentes formatos"""
    
    def __init__(self):
        pass
    
    def export_to_csv(self, output_path: str, doc_type: str = None) -> bool:
        """
        Exporta documentos a formato CSV
        
        Args:
            output_path: Ruta del archivo CSV de salida
            doc_type: Tipo específico de documento a exportar (opcional)
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            data = self._get_documents_data(doc_type)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                if not data:
                    logger.warning("No hay datos para exportar")
                    return False
                
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Exportación CSV exitosa: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            return False
    
    def export_to_json(self, output_path: str, doc_type: str = None) -> bool:
        """
        Exporta documentos a formato JSON
        
        Args:
            output_path: Ruta del archivo JSON de salida
            doc_type: Tipo específico de documento a exportar (opcional)
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            data = self._get_documents_data(doc_type)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_documents": len(data),
                "document_type_filter": doc_type,
                "documents": data
            }
            
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info(f"Exportación JSON exitosa: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a JSON: {e}")
            return False
    
    def _get_documents_data(self, doc_type: str = None) -> List[Dict]:
        """
        Obtiene datos de documentos de la base de datos
        
        Args:
            doc_type: Filtrar por tipo de documento (opcional)
            
        Returns:
            Lista de diccionarios con datos de documentos
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
            cur = conn.cursor()
            
            if doc_type:
                cur.execute("""
                    SELECT * FROM documentos 
                    WHERE tipo = ? 
                    ORDER BY fecha_procesado DESC
                """, (doc_type,))
            else:
                cur.execute("""
                    SELECT * FROM documentos 
                    ORDER BY fecha_procesado DESC
                """)
            
            rows = cur.fetchall()
            conn.close()
            
            # Convertir a lista de diccionarios
            data = [dict(row) for row in rows]
            
            return data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos: {e}")
            return []
    
    def get_summary_report(self) -> Dict:
        """
        Genera un reporte resumen de todos los documentos
        
        Returns:
            Diccionario con estadísticas y resumen
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Estadísticas generales
            cur.execute("SELECT COUNT(*) as total FROM documentos")
            total = cur.fetchone()[0]
            
            # Documentos por tipo
            cur.execute("""
                SELECT tipo, COUNT(*) as count 
                FROM documentos 
                GROUP BY tipo 
                ORDER BY count DESC
            """)
            by_type = dict(cur.fetchall())
            
            # Confianza promedio por tipo
            cur.execute("""
                SELECT tipo, AVG(confidence) as avg_confidence 
                FROM documentos 
                WHERE confidence IS NOT NULL
                GROUP BY tipo 
                ORDER BY avg_confidence DESC
            """)
            confidence_by_type = dict(cur.fetchall())
            
            # Documentos procesados por fecha
            cur.execute("""
                SELECT DATE(fecha_procesado) as fecha, COUNT(*) as count
                FROM documentos 
                GROUP BY DATE(fecha_procesado)
                ORDER BY fecha DESC
                LIMIT 7
            """)
            by_date = dict(cur.fetchall())
            
            conn.close()
            
            summary = {
                "total_documents": total,
                "documents_by_type": by_type,
                "average_confidence_by_type": {
                    k: round(v, 3) for k, v in confidence_by_type.items()
                },
                "documents_by_date": by_date,
                "generated_at": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generando reporte resumen: {e}")
            return {}
    
    def export_summary_report(self, output_path: str) -> bool:
        """
        Exporta un reporte resumen completo
        
        Args:
            output_path: Ruta del archivo de salida
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            summary = self.get_summary_report()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Reporte resumen exportado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando reporte resumen: {e}")
            return False