"""
API Web para Agente Clasificador PDF
Interfaz REST profesional para consultas y gestión de documentos
"""
import os
import sys
import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn

# Agregar el directorio padre al path para importaciones
sys.path.append(str(Path(__file__).parent.parent))

from config import OUTPUT_DIR, INPUT_DIR
from processors import DocumentProcessor, BatchProcessor
from exporters import AdvancedDataExporter
from validators import PDFValidator

# Configuración de la aplicación
app = FastAPI(
    title="🤖 Agente Clasificador PDF - API Web",
    description="Sistema Inteligente de Análisis y Clasificación de Documentos PDF",
    version="3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Montar archivos estáticos
static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ============================================================================
# 📊 MODELOS PYDANTIC
# ============================================================================

class DocumentResponse(BaseModel):
    """Modelo de respuesta para documentos"""
    id: int
    filename: str
    tipo: str
    cuit: Optional[str] = None
    proveedor: Optional[str] = None
    proveedor_id: Optional[str] = None
    fecha_documento: Optional[str] = None
    monto: Optional[str] = None
    confidence: Optional[float] = None
    fecha_procesado: str
    detalles_clasificacion: Optional[Dict[str, Any]] = None


class SearchFilters(BaseModel):
    """Filtros de búsqueda"""
    cuit: Optional[str] = None
    proveedor: Optional[str] = None
    tipo: Optional[str] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    monto_min: Optional[float] = None
    monto_max: Optional[float] = None
    confidence_min: Optional[float] = None


class StatsResponse(BaseModel):
    """Respuesta de estadísticas"""
    total_documents: int
    by_type: Dict[str, int]
    by_supplier: Dict[str, int]
    avg_confidence: float
    recent_documents: int
    processing_errors: int


class ProcessRequest(BaseModel):
    """Solicitud de procesamiento"""
    enable_ml: bool = True
    enable_layout: bool = True
    move_files: bool = True


# ============================================================================
# 🔧 FUNCIONES AUXILIARES
# ============================================================================

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    import psycopg2
    from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DB
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a PostgreSQL: {str(e)}")


def clean_numpy_values(obj):
    """Limpia valores numpy de un objeto para serialización JSON"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {key: clean_numpy_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_numpy_values(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.str_):
        return str(obj)
    elif isinstance(obj, (np.bool_, np.True_, np.False_)):
        return bool(obj)
    else:
        return obj


def parse_classification_details(details_str: str) -> Dict[str, Any]:
    """Parsea los detalles de clasificación desde JSON"""
    try:
        if not details_str:
            return {}
        raw_data = json.loads(details_str)
        return clean_numpy_values(raw_data)
    except (json.JSONDecodeError, TypeError):
        return {}


def build_query_conditions(filters: SearchFilters) -> tuple:
    """Construye condiciones SQL y parámetros para filtros"""
    conditions = []
    params = []
    
    if filters.cuit:
        conditions.append("cuit LIKE %s")
        params.append(f"%{filters.cuit}%")
    if filters.proveedor:
        conditions.append("proveedor LIKE %s")
        params.append(f"%{filters.proveedor}%")
    if filters.tipo:
        conditions.append("tipo = %s")
        params.append(filters.tipo)
    if filters.fecha_desde:
        conditions.append("fecha_documento >= %s")
        params.append(filters.fecha_desde)
    if filters.fecha_hasta:
        conditions.append("fecha_documento <= %s")
        params.append(filters.fecha_hasta)
    if filters.confidence_min is not None:
        conditions.append("confidence >= %s")
        params.append(filters.confidence_min)
    # Para filtros de monto, convertir el campo a NUMERIC en PostgreSQL
    if filters.monto_min is not None:
        conditions.append("CAST(REPLACE(REPLACE(monto, '$', ''), ',', '.') AS NUMERIC) >= %s")
        params.append(filters.monto_min)
    if filters.monto_max is not None:
        conditions.append("CAST(REPLACE(REPLACE(monto, '$', ''), ',', '.') AS NUMERIC) <= %s")
        params.append(filters.monto_max)
    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    return where_clause, params


# ============================================================================
# 🌐 ENDPOINTS DE LA API
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    """Página principal"""
    try:
        templates_file = templates_path / "index.html"
        if templates_file.exists():
            content = templates_file.read_text(encoding='utf-8')
            # Reemplazar timestamp para evitar caché
            content = content.replace("{{ timestamp }}", str(int(datetime.now().timestamp())))
            return content
        else:
            return """
            <html>
                <head><title>🤖 Agente PDF - Interfaz Web</title></head>
                <body>
                    <h1>🤖 Agente Clasificador PDF</h1>
                    <p>Sistema web en construcción...</p>
                    <a href="/api/docs">📖 Documentación API</a>
                </body>
            </html>
            """
    except Exception as e:
        return f"<h1>Error cargando interfaz: {str(e)}</h1>"

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Página de test para modal"""
    test_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Modal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>🔍 Test de Modal de Documentos</h1>
        <p><a href="/" class="btn btn-secondary">&larr; Volver a la app principal</a></p>
        
        <div class="row">
            <div class="col-md-12">
                <h3>Documentos de Prueba</h3>
                <div id="debug-info" class="alert alert-info">
                    <h6>Debug Info:</h6>
                    <div id="debug-content">Haciendo peticiones...</div>
                </div>
                
                <table class="table">
                    <thead>
                        <tr><th>ID</th><th>Nombre</th><th>Acciones</th></tr>
                    </thead>
                    <tbody id="test-docs">
                        <tr><td colspan="3">Cargando documentos...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Modal -->
    <div class="modal fade" id="testModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Detalles del Documento</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="modal-content">
                    <!-- Content loaded dynamically -->
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        async function loadTestDocs() {
            try {
                const response = await fetch('/api/documents');
                const docs = await response.json();
                
                document.getElementById('debug-content').innerHTML = 
                    `Status: ${response.status}, Docs: ${docs.length}`;
                
                const tbody = document.getElementById('test-docs');
                tbody.innerHTML = docs.slice(0, 5).map(doc => 
                    `<tr>
                        <td>${doc.id}</td>
                        <td>${doc.filename}</td>
                        <td><button class="btn btn-sm btn-primary" onclick="testModal(${doc.id})">Ver Detalles</button></td>
                    </tr>`
                ).join('');
                
            } catch (error) {
                document.getElementById('debug-content').innerHTML = `Error: ${error.message}`;
            }
        }
        
        async function testModal(documentId) {
            console.log('🔍 Testing modal for document ID:', documentId);
            
            const modalContent = document.getElementById('modal-content');
            modalContent.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2">Cargando documento ID: ${documentId}...</p>
                </div>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('testModal'));
            modal.show();
            
            try {
                const response = await fetch(`/api/documents/${documentId}`);
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP ${response.status}: ${errorText}`);
                }
                
                const document = await response.json();
                console.log('Document received:', document);
                
                modalContent.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Información General</h6>
                            <table class="table table-sm">
                                <tr><td><strong>ID:</strong></td><td>${document.id}</td></tr>
                                <tr><td><strong>Archivo:</strong></td><td>${document.filename}</td></tr>
                                <tr><td><strong>Tipo:</strong></td><td><span class="badge bg-primary">${document.tipo}</span></td></tr>
                                <tr><td><strong>CUIT:</strong></td><td>${document.cuit || 'N/A'}</td></tr>
                                <tr><td><strong>Proveedor:</strong></td><td>${document.proveedor || 'N/A'}</td></tr>
                                <tr><td><strong>Confianza:</strong></td><td>${document.confidence ? (document.confidence * 100).toFixed(2) + '%' : 'N/A'}</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6>Detalles de Clasificación</h6>
                            <div class="bg-light p-3 rounded" style="max-height: 300px; overflow-y: auto;">
                                ${document.detalles_clasificacion ? 
                                    `<pre class="small">${JSON.stringify(document.detalles_clasificacion, null, 2)}</pre>` :
                                    '<p class="text-muted">No disponible</p>'
                                }
                            </div>
                        </div>
                    </div>
                `;
                
            } catch (error) {
                console.error('Error:', error);
                modalContent.innerHTML = `
                    <div class="alert alert-danger">
                        <h6>❌ Error cargando documento</h6>
                        <p><strong>Mensaje:</strong> ${error.message}</p>
                        <p><strong>ID:</strong> ${documentId}</p>
                        <small class="text-muted">Revisa la consola del navegador para más detalles</small>
                    </div>
                `;
            }
        }
        
        // Cargar documentos al iniciar
        document.addEventListener('DOMContentLoaded', loadTestDocs);
    </script>
</body>
</html>
    """
    return test_html


@app.get("/api/health")
async def health_check():
    """Verificación de salud del sistema"""
    try:
        # Verificar base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documentos")
        doc_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database_status": "connected",
            "total_documents": doc_count,
            "version": "3.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de salud: {str(e)}")


@app.get("/api/documents", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(50, ge=1, le=1000, description="Número máximo de registros"),
    order_by: str = Query("fecha_procesado", description="Campo de ordenamiento"),
    order_desc: bool = Query(True, description="Orden descendente"),
):
    """Obtiene lista paginada de documentos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validar campo de ordenamiento
        valid_fields = ["id", "filename", "tipo", "fecha_procesado", "confidence"]
        if order_by not in valid_fields:
            order_by = "fecha_procesado"
        
        order_direction = "DESC" if order_desc else "ASC"
        
        query = f"""
            SELECT id, filename, tipo, cuit, proveedor, proveedor_id,
                   fecha_documento, monto, confidence, fecha_procesado,
                   detalles_clasificacion
            FROM documentos 
            ORDER BY {order_by} {order_direction}
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            doc = DocumentResponse(
                id=row[0],
                filename=row[1],
                tipo=row[2],
                cuit=row[3],
                proveedor=row[4],
                proveedor_id=row[5],
                fecha_documento=row[6],
                monto=row[7],
                confidence=row[8],
                fecha_procesado=row[9],
                detalles_clasificacion=parse_classification_details(row[10])
            )
            documents.append(doc)
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo documentos: {str(e)}")


@app.post("/api/documents/search", response_model=List[DocumentResponse])
async def search_documents(
    filters: SearchFilters,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    order_by: str = Query("fecha_procesado"),
    order_desc: bool = Query(True)
):
    """Busca documentos con filtros avanzados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir consulta con filtros
        where_clause, params = build_query_conditions(filters)
        
        # Validar campo de ordenamiento
        valid_fields = ["id", "filename", "tipo", "fecha_procesado", "confidence", "cuit"]
        if order_by not in valid_fields:
            order_by = "fecha_procesado"
        
        order_direction = "DESC" if order_desc else "ASC"
        
        query = f"""
            SELECT id, filename, tipo, cuit, proveedor, proveedor_id,
                   fecha_documento, monto, confidence, fecha_procesado,
                   detalles_clasificacion
            FROM documentos 
            WHERE {where_clause}
            ORDER BY {order_by} {order_direction}
            LIMIT %s OFFSET %s
        """
        params.extend([limit, skip])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            doc = DocumentResponse(
                id=row[0],
                filename=row[1],
                tipo=row[2],
                cuit=row[3],
                proveedor=row[4],
                proveedor_id=row[5],
                fecha_documento=row[6],
                monto=row[7],
                confidence=row[8],
                fecha_procesado=row[9],
                detalles_clasificacion=parse_classification_details(row[10])
            )
            documents.append(doc)
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")


@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int):
    """Obtiene un documento específico"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, tipo, cuit, proveedor, proveedor_id,
                   fecha_documento, monto, confidence, fecha_procesado,
                   detalles_clasificacion
            FROM documentos WHERE id = %s
        """, (document_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        return DocumentResponse(
            id=row[0],
            filename=row[1],
            tipo=row[2],
            cuit=row[3],
            proveedor=row[4],
            proveedor_id=row[5],
            fecha_documento=row[6],
            monto=row[7],
            confidence=row[8],
            fecha_procesado=row[9],
            detalles_clasificacion=parse_classification_details(row[10])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo documento: {str(e)}")


@app.get("/api/stats", response_model=StatsResponse)
async def get_statistics():
    """Obtiene estadísticas del sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total de documentos
        cursor.execute("SELECT COUNT(*) FROM documentos")
        total_docs = cursor.fetchone()[0]
        # Distribución por tipo
        cursor.execute("""
            SELECT tipo, COUNT(*) 
            FROM documentos 
            GROUP BY tipo 
            ORDER BY COUNT(*) DESC
        """)
        by_type = dict(cursor.fetchall())
        # Distribución por proveedor
        cursor.execute("""
            SELECT COALESCE(proveedor, 'Sin proveedor'), COUNT(*) 
            FROM documentos 
            GROUP BY proveedor 
            ORDER BY COUNT(*) DESC 
            LIMIT 10
        """)
        by_supplier = dict(cursor.fetchall())
        # Confianza promedio
        cursor.execute("SELECT AVG(confidence) FROM documentos WHERE confidence IS NOT NULL")
        avg_conf_result = cursor.fetchone()[0]
        avg_confidence = float(avg_conf_result) if avg_conf_result else 0.0
        # Documentos recientes (últimas 24 horas)
        cursor.execute("""
            SELECT COUNT(*) FROM documentos 
            WHERE TO_TIMESTAMP(fecha_procesado, 'YYYY-MM-DD HH24:MI:SS') > NOW() - INTERVAL '1 day'
        """)
        recent_docs = cursor.fetchone()[0]
        
        conn.close()
        
        return StatsResponse(
            total_documents=total_docs,
            by_type=by_type,
            by_supplier=by_supplier,
            avg_confidence=round(avg_confidence, 3),
            recent_documents=recent_docs,
            processing_errors=0  # TODO: Implementar tracking de errores
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/api/types")
async def get_document_types():
    """Obtiene lista de tipos de documentos disponibles"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT tipo FROM documentos ORDER BY tipo")
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        return {"types": types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tipos: {str(e)}")


@app.get("/api/suppliers")
async def get_suppliers():
    """Obtiene lista de proveedores"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT proveedor 
            FROM documentos 
            WHERE proveedor IS NOT NULL 
            ORDER BY proveedor
        """)
        suppliers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"suppliers": suppliers}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo proveedores: {str(e)}")


@app.get("/api/input-status")
async def get_input_status():
    """Obtiene el estado del directorio de entrada"""
    try:
        input_path = Path(INPUT_DIR)
        
        if not input_path.exists():
            return {
                "directory_exists": False,
                "directory_path": str(input_path),
                "pdf_files": [],
                "total_files": 0,
                "message": "Directorio de entrada no existe"
            }
        
        # Buscar archivos PDF
        pdf_files = list(input_path.glob("*.pdf")) + list(input_path.glob("*.PDF"))
        
        return {
            "directory_exists": True,
            "directory_path": str(input_path),
            "pdf_files": [{"name": f.name, "size": f.stat().st_size} for f in pdf_files],
            "total_files": len(pdf_files),
            "message": f"Encontrados {len(pdf_files)} archivos PDF para procesar" if pdf_files else "No hay archivos PDF para procesar"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando directorio de entrada: {str(e)}")


@app.post("/api/process")
async def process_documents(
    background_tasks: BackgroundTasks,
    request: ProcessRequest
):
    """Procesa documentos en input_pdfs"""
    try:
        # Verificar que existe el directorio de entrada
        input_path = Path(INPUT_DIR)
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Directorio de entrada no existe: {INPUT_DIR}")
        
        # Verificar que hay archivos PDF para procesar
        pdf_files = list(input_path.glob("*.pdf")) + list(input_path.glob("*.PDF"))
        if not pdf_files:
            return {
                "status": "no_files",
                "message": "No se encontraron archivos PDF para procesar",
                "timestamp": datetime.now().isoformat(),
                "input_directory": str(input_path)
            }
        
        def process_in_background():
            """Función para procesamiento en background"""
            try:
                print(f"🔄 Iniciando procesamiento de {len(pdf_files)} archivos...")
                print(f"📁 Directorio de entrada: {input_path}")
                print(f"⚙️  Configuración: ML={request.enable_ml}, Layout={request.enable_layout}")
                processor = BatchProcessor(
                    enable_ml=request.enable_ml,
                    enable_layout=request.enable_layout
                )
                print(f"🚀 Llamando process_directory con: {str(input_path)}")
                result = processor.process_directory(str(input_path))
                print(f"✅ Procesamiento completado: {result}")
                # Guardar resumen por tipo en un archivo temporal para mostrarlo luego
                with open("import_summary.json", "w", encoding="utf-8") as f:
                    json.dump(result.get("summary", {}), f, ensure_ascii=False, indent=2)
                return result
            except Exception as e:
                print(f"❌ Error en procesamiento background: {e}")
                import traceback
                traceback.print_exc()
                raise e

        background_tasks.add_task(process_in_background)

        # Si existe el resumen previo, mostrarlo
        import_summary = {}
        try:
            with open("import_summary.json", "r", encoding="utf-8") as f:
                import_summary = json.load(f)
        except Exception:
            pass

        return {
            "status": "processing_started",
            "message": f"Procesamiento iniciado: {len(pdf_files)} archivos encontrados",
            "timestamp": datetime.now().isoformat(),
            "files_found": len(pdf_files),
            "input_directory": str(input_path),
            "file_list": [f.name for f in pdf_files[:10]],  # Mostrar hasta 10 archivos
            "import_summary": import_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando procesamiento: {str(e)}")


@app.get("/api/export/{format}")
async def export_data(
    format: str,
    filters: SearchFilters = None
):
    """Exporta datos en formato especificado"""
    try:
        # Validar formato
        if format not in ['csv', 'json', 'xml']:
            raise HTTPException(status_code=400, detail="Formato no soportado")
        
        # Obtener datos con filtros si se proporcionan
        if filters:
            conn = get_db_connection()
            cursor = conn.cursor()
            where_clause, params = build_query_conditions(filters)
            
            query = f"""
                SELECT * FROM documentos WHERE {where_clause}
            """
            cursor.execute(query, params)
            
        exporter = AdvancedDataExporter()
        
        # Crear archivo temporal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.{format}"
        export_path = Path("exports") / filename
        export_path.parent.mkdir(exist_ok=True)
        
        if format == "csv":
            result = exporter.export_to_csv(str(export_path))
        elif format == "json":
            result = exporter.export_to_json(str(export_path))
        elif format == "xml":
            result = exporter.export_to_xml(str(export_path))
        
        if result.success:
            return FileResponse(
                path=str(export_path),
                filename=filename,
                media_type='application/octet-stream'
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error en exportación: {result.error}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando datos: {str(e)}")


# ============================================================================
# 🚀 CONFIGURACIÓN DEL SERVIDOR
# ============================================================================

def start_server():
    """Inicia el servidor web"""
    print("🚀 Iniciando servidor web del Agente Clasificador PDF...")
    print(f"📊 Panel de control: http://localhost:8001")
    print(f"📖 Documentación API: http://localhost:8001/api/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()

from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(templates_path))

@app.get("/manual_review", response_class=HTMLResponse)
async def manual_review(request: Request):
    """Vista para revisión manual de documentos desconocidos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, proveedor, confidence, texto_extraido FROM documentos WHERE tipo = %s LIMIT 30", ('desconocido',))
    docs = [
        {
            "id": row[0],
            "filename": row[1],
            "proveedor": row[2],
            "confidence": row[3],
            "texto_extraido": row[4] or ""
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return templates.TemplateResponse("manual_review.html", {"request": request, "documentos": docs})

@app.post("/manual_review/set_category")
async def set_manual_category(request: Request, doc_id: int = Form(...), categoria: str = Form(...)):
    """Actualiza la categoría manualmente en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE documentos SET tipo = %s WHERE id = %s", (categoria, doc_id))
    conn.commit()
    conn.close()
    # Redirigir de nuevo a la vista de revisión
    return RedirectResponse(url="/manual_review", status_code=303)

@app.get("/view_pdf/{doc_id}", response_class=FileResponse)
async def view_pdf(doc_id: int):
    """Devuelve el PDF procesado para visualización"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, tipo FROM documentos WHERE id = %s", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    filename, tipo = row
    # Limpiar espacios y saltos de línea del nombre de archivo
    filename = filename.strip().replace('\n', '').replace('\r', '')
    pdf_path = os.path.join(OUTPUT_DIR, tipo, filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"Archivo PDF no encontrado en salida: {pdf_path}")
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)