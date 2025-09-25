"""
Procesador por lotes para múltiples documentos
"""
import os
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from processors.document_processor import DocumentProcessor
from config import INPUT_DIR, SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_MB

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Procesador por lotes que maneja múltiples documentos"""
    
    def __init__(self, max_workers: int = 4, enable_ml: bool = True, enable_layout: bool = True):
        self.document_processor = DocumentProcessor(enable_ml=enable_ml, enable_layout=enable_layout)
        self.max_workers = max_workers
    
    def process_directory(self, input_dir: str = None) -> Dict:
        """
        Procesa todos los PDFs en un directorio
        
        Args:
            input_dir: Directorio de entrada (usa INPUT_DIR por defecto)
            
        Returns:
            Diccionario con resultados del procesamiento por lotes
        """
        input_dir = input_dir or INPUT_DIR
        
        results = {
            "total_files": 0,
            "processed": 0,
            "errors": 0,
            "skipped": 0,
            "results": [],
            "summary": {}
        }
        
        try:
            logger.info(f"Iniciando procesamiento por lotes en {input_dir}")
            
            # Obtener archivos PDF válidos
            pdf_files = self._get_pdf_files(input_dir)
            results["total_files"] = len(pdf_files)
            
            if not pdf_files:
                logger.warning(f"No se encontraron archivos PDF en {input_dir}")
                return results
            
            # Procesar archivos
            if self.max_workers > 1:
                results["results"] = self._process_parallel(pdf_files)
            else:
                results["results"] = self._process_sequential(pdf_files)
            
            # Calcular estadísticas
            results["processed"] = sum(1 for r in results["results"] if r["success"])
            results["errors"] = sum(1 for r in results["results"] if not r["success"])
            
            # Resumen por tipo de documento
            type_summary = {}
            for result in results["results"]:
                if result["success"]:
                    doc_type = result["classification"]
                    type_summary[doc_type] = type_summary.get(doc_type, 0) + 1
            
            results["summary"] = type_summary
            
            logger.info(f"Procesamiento por lotes completado: {results['processed']}/{results['total_files']} exitosos")
            
        except Exception as e:
            logger.error(f"Error en procesamiento por lotes: {e}")
            results["error"] = str(e)
        
        return results
    
    def _get_pdf_files(self, directory: str) -> List[str]:
        """
        Obtiene lista de archivos PDF válidos en el directorio
        
        Args:
            directory: Directorio a escanear
            
        Returns:
            Lista de rutas a archivos PDF
        """
        pdf_files = []
        
        if not os.path.exists(directory):
            logger.warning(f"Directorio no existe: {directory}")
            return pdf_files
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Verificar extensión
            if not any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                logger.debug(f"Archivo ignorado (extensión no soportada): {filename}")
                continue
            
            # Verificar que es un archivo
            if not os.path.isfile(file_path):
                continue
            
            # Verificar tamaño
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                logger.warning(f"Archivo muy grande ({file_size_mb:.1f}MB): {filename}")
                continue
            
            pdf_files.append(file_path)
            logger.debug(f"Archivo PDF válido encontrado: {filename}")
        
        return pdf_files
    
    def _process_sequential(self, file_paths: List[str]) -> List[Dict]:
        """
        Procesa archivos secuencialmente
        
        Args:
            file_paths: Lista de rutas de archivos
            
        Returns:
            Lista de resultados de procesamiento
        """
        results = []
        
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Procesando archivo {i}/{len(file_paths)}: {os.path.basename(file_path)}")
            
            result = self.document_processor.process_document(file_path)
            results.append(result)
            
            # Log del resultado
            if result["success"]:
                logger.info(f"✅ {result['filename']} → {result['classification']}")
            else:
                logger.error(f"❌ {result['filename']}: {result['error']}")
        
        return results
    
    def _process_parallel(self, file_paths: List[str]) -> List[Dict]:
        """
        Procesa archivos en paralelo
        
        Args:
            file_paths: Lista de rutas de archivos
            
        Returns:
            Lista de resultados de procesamiento
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar tareas
            future_to_file = {
                executor.submit(self.document_processor.process_document, file_path): file_path
                for file_path in file_paths
            }
            
            # Recoger resultados
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["success"]:
                        logger.info(f"✅ {result['filename']} → {result['classification']}")
                    else:
                        logger.error(f"❌ {result['filename']}: {result['error']}")
                        
                except Exception as e:
                    error_result = {
                        "success": False,
                        "filename": os.path.basename(file_path),
                        "error": f"Error en hilo de ejecución: {e}",
                        "classification": None,
                        "confidence": 0.0,
                        "metadata": {},
                        "destination": None
                    }
                    results.append(error_result)
                    logger.error(f"❌ Error procesando {os.path.basename(file_path)}: {e}")
        
        return results
    
    def process_single_file(self, file_path: str) -> Dict:
        """
        Procesa un único archivo
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Resultado del procesamiento
        """
        return self.document_processor.process_document(file_path)