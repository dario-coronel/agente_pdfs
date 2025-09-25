# 🗂️ Agente de Procesamiento de PDFs

## 📌 Descripción
Este proyecto es un **agente automatizado** para el tratamiento de archivos **PDF**.  
Su objetivo principal es:

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
