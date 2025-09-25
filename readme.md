# 🤖 Agente Clasificador de PDFs v2.0

Sistema inteligente para clasificar y organizar documentos PDF automáticamente basado en su contenido.

## 🚀 Características

- **Clasificación Inteligente**: Detecta automáticamente el tipo de documento (facturas, remitos, notas de crédito, etc.)
- **Extracción de Metadatos**: Extrae CUIT, fechas, montos y nombres de proveedores
- **Validación de PDFs**: Verifica integridad y contenido extraíble
- **Organización Automática**: Mueve archivos a carpetas según su clasificación
- **Base de Datos**: Almacena metadatos para búsquedas y reportes
- **Procesamiento por Lotes**: Maneja múltiples archivos simultáneamente
- **Logging Completo**: Registro detallado de todas las operaciones
- **Exportación de Datos**: CSV, JSON y reportes de estadísticas

## � Estructura del Proyecto

```
agente_pdfs/
├── 🧠 classifiers/           # Clasificadores de documentos
│   ├── document_classifier.py   # Clasificador principal basado en reglas
│   └── __init__.py
├── 🔍 extractors/            # Extractores de datos
│   ├── text_extractor.py        # Extracción de texto PDF
│   ├── metadata_extractor.py    # Extracción de metadatos (CUIT, fechas, etc.)
│   └── __init__.py
├── ⚙️ processors/            # Procesadores principales
│   ├── document_processor.py    # Procesador individual de documentos
│   ├── batch_processor.py       # Procesador por lotes
│   └── __init__.py
├── ✅ validators/            # Validadores
│   ├── pdf_validator.py         # Validación de archivos PDF
│   └── __init__.py
├── 📊 exporters/             # Exportadores de datos
│   ├── data_exporter.py         # Exportación a CSV/JSON
│   └── __init__.py
├── 🛠️ utils/                 # Utilidades generales
├── 📂 input_pdfs/            # Carpeta de archivos de entrada
├── 📁 output_pdfs/           # Carpeta organizada por tipos
├── 🗄️ db/                    # Base de datos SQLite
├── 📝 logs/                  # Archivos de log
├── config.py                 # Configuración centralizada
├── main.py                   # Punto de entrada principal
├── search.py                 # Búsqueda en base de datos
└── requirements.txt          # Dependencias
```

## 🛠️ Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/dario-coronel/agente_pdfs.git
   cd agente_pdfs
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Crear directorio de entrada:**
   ```bash
   mkdir input_pdfs  # El programa lo creará automáticamente si no existe
   ```

## 🚀 Uso

### Procesamiento Básico

1. **Colocar PDFs** en la carpeta `input_pdfs/`
2. **Ejecutar el agente:**
   ```bash
   python main.py
   ```
3. **Revisar resultados** en `output_pdfs/` organizados por tipo

### Búsqueda de Documentos

```bash
# Buscar por tipo
python search.py tipo facturas

# Buscar por CUIT
python search.py cuit 20-12345678-9

# Buscar por proveedor
python search.py proveedor "Acme S.A."
```

## 📋 Tipos de Documentos Soportados

- **Facturas** (`facturas/`)
- **Remitos** (`remitos/`)
- **Notas de Crédito** (`notas_credito/`)
- **Notas de Débito** (`notas_debito/`)
- **Cartas de Porte** (`cartas_porte/`)
- **Recibos** (`recibos/`)
- **Órdenes de Compra** (`ordenes_compra/`)
- **Contratos** (`contratos/`)
- **Documentos Desconocidos** (`desconocido/`)

## ⚙️ Configuración

Editar `config.py` para personalizar

- Validar que los archivos sean **PDF válidos**.
- Leer el contenido de cada archivo.
- **Clasificar** el documento como:
  - Factura
  - Remito
  - Nota de Crédito
  - Nota de Débito
  - Carta de Porte
- Extraer información relevante como el **CUIT** y el **proveedor**.
- Guardar los archivos en carpetas de salida organizadas por tipo de documento.
- Registrar la información en una base de datos **SQLite**, permitiendo búsquedas posteriores (ej. por CUIT o proveedor).

En versiones futuras se integrará con **Nextcloud (WebDAV)** y un modelo de **clasificación NLP** para mejorar la identificación de documentos.

---

## 📂 Estructura del Proyecto
