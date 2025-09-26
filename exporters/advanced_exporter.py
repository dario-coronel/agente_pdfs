"""
Sistema de exportación avanzado para múltiples formatos
"""
import csv
import json
import sqlite3
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from config import EXPORT_CONFIG
from utils import get_logger

logger = get_logger(__name__)

try:
    import pandas as pd
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    logger.warning("pandas/openpyxl no disponible - exportación a Excel deshabilitada")


class ExportResult:
    """Clase para encapsular resultados de exportación"""
    
    def __init__(self):
        self.success = False
        self.file_path = ""
        self.format = ""
        self.records_exported = 0
        self.file_size = 0
        self.export_time = 0.0
        self.errors = []
        self.warnings = []
    
    def to_dict(self) -> Dict:
        """Convierte el resultado a diccionario"""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "format": self.format,
            "records_exported": self.records_exported,
            "file_size": self.file_size,
            "export_time": self.export_time,
            "errors": self.errors,
            "warnings": self.warnings
        }


class AdvancedDataExporter:
    """Exportador avanzado con soporte para múltiples formatos y opciones"""
    
    def __init__(self, db_path: str = None):
        self.db_path = None  # Ya no se usa DB_PATH, solo PostgreSQL
        self.config = EXPORT_CONFIG
        self.supported_formats = ["csv", "json", "xml"]
        
        if EXCEL_AVAILABLE:
            self.supported_formats.append("excel")
    
    def export_data(self, output_path: str, format_type: str = None, 
                   filters: Dict = None, include_details: bool = True) -> ExportResult:
        """
        Exporta datos de la base de datos al formato especificado
        
        Args:
            output_path: Ruta del archivo de salida
            format_type: Formato de exportación (auto-detecta si es None)
            filters: Filtros para la consulta de datos
            include_details: Si incluir detalles de clasificación
            
        Returns:
            ExportResult con información de la exportación
        """
        result = ExportResult()
        start_time = datetime.now()
        
        try:
            # Detectar formato si no se especifica
            if format_type is None:
                format_type = self._detect_format(output_path)
            
            result.format = format_type
            
            # Validar formato
            if format_type not in self.supported_formats:
                result.errors.append(f"Formato no soportado: {format_type}")
                return result
            
            # Obtener datos de la base de datos
            data = self._fetch_data(filters, include_details)
            if not data:
                result.warnings.append("No se encontraron datos para exportar")
                result.success = True
                return result
            
            # Crear directorio de salida si no existe
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Exportar según el formato
            if format_type == "csv":
                self._export_csv(data, output_path, result)
            elif format_type == "json":
                self._export_json(data, output_path, result)
            elif format_type == "excel":
                self._export_excel(data, output_path, result)
            elif format_type == "xml":
                self._export_xml(data, output_path, result)
            
            # Calcular estadísticas finales
            if Path(output_path).exists():
                result.file_path = str(Path(output_path).absolute())
                result.file_size = Path(output_path).stat().st_size
                result.records_exported = len(data)
                result.success = True
            
            result.export_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Exportación exitosa: {len(data)} registros a {format_type} en {result.export_time:.2f}s")
            
        except Exception as e:
            result.errors.append(f"Error durante exportación: {str(e)}")
            logger.error(f"Error exportando datos: {e}")
        
        return result
    
    def _detect_format(self, file_path: str) -> str:
        """Detecta el formato basándose en la extensión del archivo"""
        extension = Path(file_path).suffix.lower()
        format_map = {
            ".csv": "csv",
            ".json": "json", 
            ".xlsx": "excel",
            ".xls": "excel",
            ".xml": "xml"
        }
        return format_map.get(extension, self.config.get("default_format", "csv"))
    
    def _fetch_data(self, filters: Dict = None, include_details: bool = True) -> List[Dict]:
        """Obtiene datos de la base de datos con filtros opcionales"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
            
            # Construcción de consulta base
            base_query = """
                SELECT 
                    d.*
                FROM documentos d
            """
            
            params = []
            where_conditions = []
            
            # Aplicar filtros si se proporcionan
            if filters:
                if filters.get("document_type"):
                    where_conditions.append("d.tipo = ?")
                    params.append(filters["document_type"])
                
                if filters.get("min_confidence"):
                    where_conditions.append("d.confidence >= ?")
                    params.append(filters["min_confidence"])
                
                if filters.get("date_from"):
                    where_conditions.append("d.fecha_procesado >= ?")
                    params.append(filters["date_from"])
                
                if filters.get("date_to"):
                    where_conditions.append("d.fecha_procesado <= ?")
                    params.append(filters["date_to"])
                
                if filters.get("supplier_id"):
                    where_conditions.append("d.proveedor_id = ?")
                    params.append(filters["supplier_id"])
            
            # Construir consulta final
            if where_conditions:
                query = base_query + " WHERE " + " AND ".join(where_conditions)
            else:
                query = base_query
            
            query += " ORDER BY d.fecha_procesado DESC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            data = []
            for row in rows:
                record = dict(row)
                
                # Parsear detalles de clasificación si están disponibles
                if include_details and record.get("detalles_clasificacion"):
                    try:
                        details = json.loads(record["detalles_clasificacion"])
                        record["classification_details"] = details
                    except json.JSONDecodeError:
                        record["classification_details"] = None
                
                data.append(record)
            
            conn.close()
            return data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos: {e}")
            return []
    
    def _export_csv(self, data: List[Dict], output_path: str, result: ExportResult):
        """Exporta datos a formato CSV"""
        try:
            with open(output_path, 'w', newline='', encoding=self.config.get("csv_encoding", "utf-8")) as csvfile:
                if not data:
                    return
                
                # Preparar datos para CSV (aplanar estructuras complejas)
                flattened_data = []
                for record in data:
                    flat_record = {}
                    
                    # Campos básicos
                    for key, value in record.items():
                        if key != "classification_details":
                            flat_record[key] = value
                    
                    # Detalles de clasificación (si se incluyen)
                    if self.config.get("include_classification_details", True):
                        details = record.get("classification_details")
                        if details:
                            # Resultados por método
                            if self.config.get("include_method_results", True):
                                method_results = details.get("method_results", {})
                                for method, method_data in method_results.items():
                                    flat_record[f"method_{method}_type"] = method_data.get("type")
                                    flat_record[f"method_{method}_confidence"] = method_data.get("confidence")
                            
                            # Información de consenso
                            consensus = details.get("consensus_analysis", {})
                            if consensus:
                                flat_record["consensus_best"] = consensus.get("best_consensus")
                                flat_record["consensus_strong"] = consensus.get("has_strong_consensus")
                    
                    flattened_data.append(flat_record)
                
                # Escribir CSV
                fieldnames = flattened_data[0].keys() if flattened_data else []
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                                      delimiter=self.config.get("csv_separator", ","))
                
                writer.writeheader()
                writer.writerows(flattened_data)
                
        except Exception as e:
            result.errors.append(f"Error exportando CSV: {str(e)}")
    
    def _export_json(self, data: List[Dict], output_path: str, result: ExportResult):
        """Exporta datos a formato JSON"""
        try:
            export_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "total_records": len(data),
                    "format": "json",
                    "version": "1.0"
                },
                "records": data
            }
            
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            result.errors.append(f"Error exportando JSON: {str(e)}")
    
    def _export_excel(self, data: List[Dict], output_path: str, result: ExportResult):
        """Exporta datos a formato Excel (requiere pandas)"""
        if not EXCEL_AVAILABLE:
            result.errors.append("Excel no disponible - instalar pandas y openpyxl")
            return
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Hoja principal con resumen
                df_main = pd.DataFrame([{
                    key: value for key, value in record.items() 
                    if key != "classification_details"
                } for record in data])
                
                df_main.to_excel(writer, sheet_name=self.config["excel_sheets"]["summary"], index=False)
                
                # Hoja detallada con información de clasificación
                if self.config.get("include_classification_details", True) and data:
                    detailed_records = []
                    
                    for record in data:
                        details = record.get("classification_details")
                        if details:
                            method_results = details.get("method_results", {})
                            for method, method_data in method_results.items():
                                detailed_records.append({
                                    "documento_id": record.get("id"),
                                    "filename": record.get("filename"),
                                    "metodo": method,
                                    "tipo_predicho": method_data.get("type"),
                                    "confianza": method_data.get("confidence"),
                                    "tipo_final": record.get("tipo"),
                                    "confianza_final": record.get("confidence")
                                })
                    
                    if detailed_records:
                        df_detailed = pd.DataFrame(detailed_records)
                        df_detailed.to_excel(writer, sheet_name=self.config["excel_sheets"]["methods"], index=False)
                
                # Hoja de estadísticas
                stats = self._generate_statistics(data)
                df_stats = pd.DataFrame([stats])
                df_stats.to_excel(writer, sheet_name="Estadisticas", index=False)
                
        except Exception as e:
            result.errors.append(f"Error exportando Excel: {str(e)}")
    
    def _export_xml(self, data: List[Dict], output_path: str, result: ExportResult):
        """Exporta datos a formato XML"""
        try:
            root = ET.Element("document_export")
            
            # Metadatos
            metadata = ET.SubElement(root, "metadata")
            ET.SubElement(metadata, "export_date").text = datetime.now().isoformat()
            ET.SubElement(metadata, "total_records").text = str(len(data))
            ET.SubElement(metadata, "format").text = "xml"
            
            # Documentos
            documents = ET.SubElement(root, "documents")
            
            for record in data:
                doc_elem = ET.SubElement(documents, "document")
                
                for key, value in record.items():
                    if key != "classification_details":
                        elem = ET.SubElement(doc_elem, key.replace(" ", "_"))
                        elem.text = str(value) if value is not None else ""
                
                # Detalles de clasificación
                if self.config.get("include_classification_details", True):
                    details = record.get("classification_details")
                    if details:
                        details_elem = ET.SubElement(doc_elem, "classification_details")
                        
                        # Métodos
                        method_results = details.get("method_results", {})
                        if method_results:
                            methods_elem = ET.SubElement(details_elem, "methods")
                            for method, method_data in method_results.items():
                                method_elem = ET.SubElement(methods_elem, "method", name=method)
                                ET.SubElement(method_elem, "type").text = str(method_data.get("type", ""))
                                ET.SubElement(method_elem, "confidence").text = str(method_data.get("confidence", 0))
            
            # Escribir archivo XML
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
        except Exception as e:
            result.errors.append(f"Error exportando XML: {str(e)}")
    
    def _generate_statistics(self, data: List[Dict]) -> Dict:
        """Genera estadísticas de los datos exportados"""
        if not data:
            return {}
        
        # Estadísticas básicas
        total_docs = len(data)
        doc_types = {}
        confidence_sum = 0
        suppliers = set()
        
        for record in data:
            # Contar tipos de documento
            doc_type = record.get("tipo", "desconocido")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Sumar confianza para promedio
            confidence = record.get("confidence", 0)
            if confidence:
                confidence_sum += confidence
            
            # Proveedores únicos
            supplier = record.get("proveedor_id")
            if supplier:
                suppliers.add(supplier)
        
        avg_confidence = confidence_sum / total_docs if total_docs > 0 else 0
        
        stats = {
            "total_documentos": total_docs,
            "confianza_promedio": round(avg_confidence, 3),
            "tipos_documento": len(doc_types),
            "proveedores_unicos": len(suppliers),
            "tipo_mas_comun": max(doc_types.items(), key=lambda x: x[1])[0] if doc_types else "N/A"
        }
        
        # Agregar conteos por tipo
        for doc_type, count in doc_types.items():
            stats[f"count_{doc_type}"] = count
        
        return stats
    
    def export_multiple_formats(self, base_path: str, formats: List[str] = None, 
                              filters: Dict = None) -> Dict[str, ExportResult]:
        """
        Exporta datos a múltiples formatos simultáneamente
        
        Args:
            base_path: Ruta base para los archivos (sin extensión)
            formats: Lista de formatos a exportar
            filters: Filtros para los datos
            
        Returns:
            Diccionario con resultados por formato
        """
        if formats is None:
            formats = self.supported_formats
        
        results = {}
        
        for fmt in formats:
            if fmt in self.supported_formats:
                # Generar nombre de archivo con extensión apropiada
                if fmt == "excel":
                    file_path = f"{base_path}.xlsx"
                else:
                    file_path = f"{base_path}.{fmt}"
                
                result = self.export_data(file_path, fmt, filters)
                results[fmt] = result
            else:
                logger.warning(f"Formato no soportado: {fmt}")
        
        return results
    
    def get_export_summary(self, results: Dict[str, ExportResult]) -> Dict:
        """
        Genera resumen de múltiples exportaciones
        
        Args:
            results: Resultados de exportaciones
            
        Returns:
            Diccionario con resumen
        """
        summary = {
            "total_formats": len(results),
            "successful_exports": 0,
            "failed_exports": 0,
            "total_records": 0,
            "total_file_size": 0,
            "formats": []
        }
        
        for fmt, result in results.items():
            format_info = {
                "format": fmt,
                "success": result.success,
                "file_path": result.file_path,
                "records": result.records_exported,
                "file_size": result.file_size,
                "export_time": result.export_time
            }
            
            if result.success:
                summary["successful_exports"] += 1
                summary["total_records"] = max(summary["total_records"], result.records_exported)
                summary["total_file_size"] += result.file_size
            else:
                summary["failed_exports"] += 1
                format_info["errors"] = result.errors
            
            summary["formats"].append(format_info)
        
        return summary


# Clase de compatibilidad
DataExporter = AdvancedDataExporter