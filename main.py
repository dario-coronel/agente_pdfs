"""
Agente Clasificador de PDFs - Punto de entrada principal
"""
import os
import sys
import logging
from pathlib import Path
from processors import BatchProcessor
from config import INPUT_DIR, LOGGING_CONFIG


def setup_logging():
    """Configura el sistema de logging"""
    # Crear directorio de logs si no existe
    log_dir = Path(LOGGING_CONFIG["log_file"]).parent
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG["level"]),
        format=LOGGING_CONFIG["format"],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG["log_file"]),
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_banner():
    """Imprime el banner de inicio del agente"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                    🤖 AGENTE CLASIFICADOR PDF                 ║
║                     Versión 2.0 - Refactorizado              ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_results(results):
    """Imprime los resultados del procesamiento"""
    print("\n" + "="*60)
    print("📊 RESULTADOS DEL PROCESAMIENTO")
    print("="*60)
    
    print(f"📁 Archivos totales: {results['total_files']}")
    print(f"✅ Procesados exitosamente: {results['processed']}")
    print(f"❌ Errores: {results['errors']}")
    print(f"⏭️ Omitidos: {results['skipped']}")
    
    if results['summary']:
        print("\n📋 Distribución por tipo:")
        for doc_type, count in results['summary'].items():
            print(f"   • {doc_type}: {count} documentos")
    
    print("\n📄 Detalles por archivo:")
    for result in results['results']:
        if result['success']:
            confidence_str = f"({result['confidence']:.2f})" if result['confidence'] else ""
            print(f"   ✅ {result['filename']} → {result['classification']} {confidence_str}")
        else:
            print(f"   ❌ {result['filename']}: {result['error']}")


def main():
    """Función principal del agente"""
    try:
        # Configurar logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Banner de inicio
        print_banner()
        
        logger.info("🚀 Iniciando Agente Clasificador PDF v2.0")
        
        # Verificar directorio de entrada
        if not os.path.exists(INPUT_DIR):
            print(f"\n⚠️  El directorio de entrada no existe: {INPUT_DIR}")
            print(f"📁 Creando directorio: {INPUT_DIR}")
            os.makedirs(INPUT_DIR, exist_ok=True)
            print(f"✅ Directorio creado. Coloca archivos PDF aquí y ejecuta nuevamente.")
            return
        
        # Verificar si hay archivos PDF
        pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print(f"\n📂 No se encontraron archivos PDF en: {INPUT_DIR}")
            print("💡 Coloca archivos PDF en la carpeta 'input_pdfs' y ejecuta nuevamente.")
            return
        
        print(f"\n🔍 Encontrados {len(pdf_files)} archivos PDF para procesar:")
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file}")
        
        print("\n⚡ Iniciando procesamiento...")
        
        # Crear procesador por lotes
        batch_processor = BatchProcessor(max_workers=2)  # Procesar 2 archivos en paralelo
        
        # Procesar todos los archivos
        results = batch_processor.process_directory(INPUT_DIR)
        
        # Mostrar resultados
        print_results(results)
        
        # Mostrar estadísticas finales
        stats = batch_processor.document_processor.get_processing_stats()
        if stats:
            print(f"\n📈 Total de documentos en base de datos: {stats['total_documents']}")
            print(f"🎯 Confianza promedio: {stats['average_confidence']:.3f}")
        
        print("\n🏁 Procesamiento completado.")
        logger.info("Procesamiento completado exitosamente")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Procesamiento interrumpido por el usuario")
        logger.info("Procesamiento interrumpido por el usuario")
        
    except Exception as e:
        error_msg = f"Error crítico en el procesamiento: {e}"
        print(f"\n💥 {error_msg}")
        logger.error(error_msg, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()