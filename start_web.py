"""
Servidor web para Agente Clasificador PDF - Versión Simplificada
"""
import os
import sys
import uvicorn

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Función principal para iniciar el servidor"""
    print("🤖 Agente Clasificador PDF - Servidor Web v3.0")
    print("=" * 60)
    print(f"🌐 Panel de control: http://localhost:8001")
    print(f"📖 API Docs: http://localhost:8001/api/docs")
    print(f"🔧 ReDoc: http://localhost:8001/api/redoc")
    print("=" * 60)
    print("Presiona Ctrl+C para detener el servidor")
    
    try:
        # Importar la aplicación
        from web_api.main import app
        
        # Iniciar servidor
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True
        )
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    main()