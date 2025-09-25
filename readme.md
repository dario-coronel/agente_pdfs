# 🤖 Agente Clasificador de PDFs v3.0

Sistema inteligente para clasificar y organizar documentos PDF automáticamente con interfaz web profesional.

## 🚀 Características Principales

### 🧠 Clasificación Inteligente Avanzada
- **Múltiples Métodos**: Combina análisis por palabras clave, expresiones regulares, machine learning y análisis de layout
- **Detección de Proveedores**: Identifica automáticamente empresas conocidas (Telecom Argentina, Claro, etc.)
- **Consenso Inteligente**: Combina resultados de múltiples métodos para mayor precisión
- **Confianza Ajustable**: Sistema de confianza que mejora automáticamente

### 📊 Extracción Completa de Metadatos
- **CUIT/CUIL**: Detección automática con validación
- **Fechas**: Múltiples formatos de fecha reconocidos
- **Montos**: Extracción de importes en diferentes formatos
- **Números de Documento**: Identificación de facturas, remitos, etc.
- **Información de Proveedores**: Nombres, direcciones y datos de contacto

### 🌐 Interfaz Web Profesional
- **Dashboard Interactivo**: Estadísticas en tiempo real con gráficos Chart.js
- **Búsqueda Avanzada**: Filtros por proveedor, CUIT, fecha, tipo, monto
- **Gestión de Documentos**: Visualización, edición y exportación
- **Procesamiento en Tiempo Real**: Control del procesamiento desde la web
- **API REST Completa**: 14 endpoints documentados con FastAPI

### 🔧 Funcionalidades Adicionales
- **Validación Robusta**: Verificación de integridad y contenido extraíble
- **Logging Avanzado**: Sistema de logs estructurado con niveles configurables
- **Exportación Multi-formato**: CSV, JSON, Excel (opcional)
- **Procesamiento por Lotes**: Manejo eficiente de múltiples archivos
- **CLI Mejorado**: Interfaz de línea de comandos con opciones avanzadas

## 📁 Estructura del Proyecto

```
agente_pdfs/
├── 🧠 classifiers/           # Sistema de clasificación inteligente
│   ├── document_classifier.py   # Clasificador principal basado en reglas
│   ├── intelligent_classifier.py # Clasificador ML con consenso
│   └── __init__.py
├── 🔍 extractors/            # Extractores de datos avanzados
│   ├── text_extractor.py        # Extracción de texto PDF con OCR
│   ├── metadata_extractor.py    # Extracción de metadatos completa
│   └── __init__.py
├── ⚙️ processors/            # Procesadores principales
│   ├── document_processor.py    # Procesador individual mejorado
│   ├── batch_processor.py       # Procesador por lotes optimizado
│   └── __init__.py
├── ✅ validators/            # Validadores robustos
│   ├── pdf_validator.py         # Validación completa de PDFs
│   └── __init__.py
├── 📊 exporters/             # Exportadores multi-formato
│   ├── data_exporter.py         # Exportación CSV/JSON/Excel
│   └── __init__.py
├── 🌐 web_api/               # Interfaz web y API REST
│   ├── main.py                  # Servidor FastAPI principal
│   ├── templates/               # Templates HTML Jinja2
│   │   └── index.html              # Interfaz web profesional
│   └── static/                  # Recursos estáticos
│       ├── css/style.css           # Estilos Bootstrap personalizados
│       └── js/app.js               # JavaScript para interactividad
├── 🛠️ utils/                 # Utilidades y helpers
│   ├── advanced_logger.py       # Sistema de logging avanzado
│   ├── cli.py                   # CLI mejorado con opciones
│   └── __init__.py
├── 📂 input_pdfs/            # Carpeta de archivos de entrada
├── 📁 output_pdfs/           # Carpetas organizadas por tipos
│   ├── facturas/               # Facturas clasificadas
│   ├── remitos/                # Remitos y albaranes
│   ├── notas_credito/          # Notas de crédito
│   └── desconocido/            # Documentos sin clasificar
├── 🗄️ db/                    # Base de datos SQLite
│   └── documentos.db           # BD con metadatos completos
├── 📝 logs/                  # Sistema de logging estructurado
├── config.py                 # Configuración centralizada avanzada
├── main.py                   # CLI principal
├── start_web.py              # Iniciador del servidor web
└── requirements.txt          # Dependencias actualizadas
```

## 🛠️ Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación Rápida

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/dario-coronel/agente_pdfs.git
   cd agente_pdfs
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicializar el sistema:**
   ```bash
   # El sistema creará automáticamente las carpetas necesarias
   python main.py --setup
   ```

## 🚀 Guía de Uso

### 🌐 Interfaz Web (Recomendado)

1. **Iniciar el servidor web:**
   ```bash
   python start_web.py
   ```

2. **Abrir en el navegador:**
   - **Panel de Control**: http://localhost:8001
   - **API Docs**: http://localhost:8001/api/docs
   - **ReDoc**: http://localhost:8001/api/redoc

3. **Usar la interfaz:**
   - **Dashboard**: Ver estadísticas y gráficos en tiempo real
   - **Búsqueda**: Filtrar documentos por múltiples criterios
   - **Documentos**: Gestionar y visualizar la base de datos
   - **Procesamiento**: Subir y procesar PDFs directamente

### 💻 Línea de Comandos

#### Procesamiento Básico
```bash
# Procesar todos los PDFs en input_pdfs/
python main.py

# Procesar con opciones específicas
python main.py --enable-ml --enable-layout --move-files
```

#### Búsquedas en Base de Datos
```bash
# Buscar por tipo de documento
python search.py tipo facturas

# Buscar por CUIT
python search.py cuit 30-71154464-6

# Buscar por proveedor
python search.py proveedor "TELECOM ARGENTINA"

# Búsqueda por rango de fechas
python search.py fecha 2024-01-01 2024-12-31
```

#### CLI Avanzado
```bash
# Ver todas las opciones disponibles
python main.py --help

# Procesar con configuración personalizada
python main.py --input-dir ./mis_pdfs --output-dir ./resultados --confidence 0.8

# Exportar datos
python main.py --export csv --output-file resultados.csv
```

## 📋 Tipos de Documentos Soportados

| Tipo | Carpeta | Descripción |
|------|---------|-------------|
| **Facturas** | `facturas/` | Facturas A, B, C, E, M |
| **Remitos** | `remitos/` | Remitos y albaranes de entrega |
| **Notas de Crédito** | `notas_credito/` | Notas de crédito y devoluciones |
| **Notas de Débito** | `notas_debito/` | Notas de débito y ajustes |
| **Cartas de Porte** | `cartas_porte/` | Documentos de transporte |
| **Recibos** | `recibos/` | Recibos de pago y cobranza |
| **Órdenes de Compra** | `ordenes_compra/` | Órdenes y pedidos |
| **Contratos** | `contratos/` | Contratos y acuerdos |
| **Desconocido** | `desconocido/` | Documentos sin clasificar |

## ⚙️ Configuración Avanzada

### Archivo `config.py`

```python
# Configuración de clasificación inteligente
INTELLIGENT_CLASSIFICATION_CONFIG = {
    "enable_ml": True,                    # Activar machine learning
    "enable_layout_analysis": True,       # Análisis de layout
    "enable_supplier_detection": True,    # Detección de proveedores
    "classification_weights": {
        "keyword": 0.25,                  # Peso de palabras clave
        "regex": 0.30,                    # Peso de expresiones regulares
        "ml": 0.20,                       # Peso de ML
        "layout": 0.15,                   # Peso de análisis de layout
        "supplier_boost": 0.30,           # Boost por proveedor conocido
        "consensus_factor": 0.10          # Factor de consenso
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "log_file": "logs/agente_pdfs.log",
    "max_file_size": 10 * 1024 * 1024,   # 10 MB
    "backup_count": 5,
    "enable_structured_logging": True
}
```

## 🔌 API REST

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/health` | Estado del sistema |
| `GET` | `/api/stats` | Estadísticas generales |
| `GET` | `/api/documents` | Listar documentos |
| `POST` | `/api/documents/search` | Búsqueda avanzada |
| `GET` | `/api/types` | Tipos de documentos |
| `GET` | `/api/suppliers` | Lista de proveedores |
| `POST` | `/api/process` | Iniciar procesamiento |
| `GET` | `/api/input-status` | Estado de archivos de entrada |
| `GET` | `/api/export/{format}` | Exportar datos |

### Ejemplo de Uso de la API

```python
import requests

# Búsqueda de documentos
response = requests.post('http://localhost:8001/api/documents/search', 
    json={
        'proveedor': 'TELECOM',
        'fecha_desde': '2024-01-01',
        'fecha_hasta': '2024-12-31'
    }
)
documentos = response.json()

# Estadísticas
stats = requests.get('http://localhost:8001/api/stats').json()
print(f"Total documentos: {stats['total_documentos']}")
```

## 🧪 Ejemplos de Uso

### 1. Procesamiento Automático Diario
```bash
#!/bin/bash
# Script para procesamiento automático
cd /ruta/agente_pdfs
python main.py --input-dir /ruta/documentos_nuevos --move-files --quiet
python main.py --export csv --output-file /ruta/reportes/$(date +%Y%m%d).csv
```

### 2. Integración con Python
```python
from processors import BatchProcessor
from exporters import DataExporter

# Procesar documentos
processor = BatchProcessor(enable_ml=True, enable_layout=True)
result = processor.process_directory("./nuevos_pdfs")

# Exportar resultados
exporter = DataExporter()
exporter.export_to_csv("resultados.csv")
```

### 3. Búsqueda Programática
```python
import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Buscar facturas de un proveedor específico
cursor.execute("""
    SELECT filename, monto, fecha_documento 
    FROM documentos 
    WHERE tipo = 'facturas' AND proveedor LIKE '%TELECOM%'
    ORDER BY fecha_documento DESC
""")

for doc in cursor.fetchall():
    print(f"Factura: {doc[0]}, Monto: {doc[1]}, Fecha: {doc[2]}")
```

## 🔧 Troubleshooting

### Problemas Comunes

1. **Error de dependencias:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Base de datos no inicializada:**
   ```bash
   python -c "from processors import DocumentProcessor; DocumentProcessor()._init_database()"
   ```

3. **Puerto 8001 ocupado:**
   ```bash
   # Cambiar puerto en web_api/main.py o usar:
   netstat -ano | findstr :8001
   taskkill /F /PID <PID>
   ```

4. **Problemas con PDFs corruptos:**
   - Los archivos se mueven automáticamente a `output_pdfs/desconocido/`
   - Revisar logs en `logs/agente_pdfs.log`

## 📊 Métricas y Monitoreo

### Dashboard Web
- **Estadísticas en Tiempo Real**: Documentos procesados, tipos, proveedores
- **Gráficos Interactivos**: Distribución por tipos con Chart.js
- **Estado del Sistema**: Salud de la aplicación y rendimiento

### Logging Estructurado
```bash
# Ver logs en tiempo real
tail -f logs/agente_pdfs.log

# Filtrar por nivel
grep "ERROR" logs/agente_pdfs.log
grep "CLASSIFICATION" logs/agente_pdfs.log
```

## 🚀 Próximas Funcionalidades

- [ ] **Integración con Nextcloud/WebDAV** para almacenamiento en la nube
- [ ] **Modelo ML personalizado** entrenado con datos específicos
- [ ] **Procesamiento OCR avanzado** para documentos escaneados
- [ ] **API de Webhooks** para integraciones externas
- [ ] **Interface móvil** responsiva para tablets y smartphones
- [ ] **Análisis de duplicados** automático
- [ ] **Flujos de trabajo** configurables por tipo de documento

## 📝 Changelog

### v3.0 (2025-09-25)
- ✨ **Nueva interfaz web profesional** con Bootstrap 5.3
- 🧠 **Sistema de clasificación inteligente** con múltiples métodos
- 🔍 **Detección automática de proveedores** conocidos
- 📊 **API REST completa** con FastAPI y documentación automática
- 🎯 **Consenso inteligente** entre métodos de clasificación
- 📈 **Dashboard interactivo** con estadísticas en tiempo real
- 🔧 **CLI mejorado** con opciones avanzadas
- 📋 **Logging estructurado** con múltiples niveles
- 🗃️ **Base de datos optimizada** con metadatos completos

### v2.0 (2024-12-15)
- 🔍 **Extracción mejorada de metadatos**
- 📊 **Sistema de exportación** a múltiples formatos
- ✅ **Validación robusta** de archivos PDF
- 🗄️ **Base de datos SQLite** integrada
- 📝 **Sistema de logging** completo

### v1.0 (2024-10-01)
- 🤖 **Clasificación automática** básica por reglas
- 📂 **Organización automática** en carpetas
- 🔍 **Extracción básica** de CUIT y fechas
- ⚙️ **Procesamiento por lotes**

## 🤝 Contribuir

1. **Fork** del repositorio
2. **Crear rama** para nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** de cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear Pull Request**

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autor

**Darío Coronel** - [GitHub](https://github.com/dario-coronel)

---

🤖 *Sistema desarrollado para automatizar la clasificación y gestión de documentos PDF empresariales*