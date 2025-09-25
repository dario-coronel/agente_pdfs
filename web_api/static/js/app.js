/**
 * Agente Clasificador PDF - Web Interface
 * JavaScript principal para la interfaz web
 */

// Variables globales
let currentPage = 0;
let pageSize = 50;
let sortField = 'fecha_procesado';
let sortDesc = true;
let totalDocuments = 0;
let typeChart = null;

// Configuración de API
const API_BASE = '';
const API_ENDPOINTS = {
    health: '/api/health',
    documents: '/api/documents',
    search: '/api/documents/search',
    stats: '/api/stats',
    types: '/api/types',
    suppliers: '/api/suppliers',
    process: '/api/process',
    inputStatus: '/api/input-status',
    export: '/api/export'
};

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Agente PDF Web Interface v3.0 cargado');
    
    // Inicializar la interfaz
    initializeInterface();
    
    // Verificar salud del sistema
    checkSystemHealth();
    
    // Cargar datos iniciales
    loadInitialData();
    
    // Configurar event listeners
    setupEventListeners();
});

function initializeInterface() {
    // Mostrar tab por defecto
    showTab('dashboard');
    
    // Configurar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupEventListeners() {
    // Navigation tabs
    document.querySelectorAll('[data-tab]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = e.target.closest('[data-tab]').getAttribute('data-tab');
            showTab(tabName);
        });
    });
}

// ============================================================================
// NAVEGACIÓN Y TABS
// ============================================================================

function showTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remover clase active de todos los links
    document.querySelectorAll('[data-tab]').forEach(link => {
        link.classList.remove('active');
    });
    
    // Mostrar el tab seleccionado
    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Activar el link correspondiente
    const activeLink = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // Cargar datos específicos del tab
    switch(tabName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'documents':
            loadDocuments(0);
            break;
        case 'search':
            loadSearchOptions();
            break;
        case 'process':
            checkProcessingStatus();
            break;
    }
}

// ============================================================================
// API CALLS Y DATOS
// ============================================================================

async function checkSystemHealth() {
    try {
        const response = await fetch(API_ENDPOINTS.health);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatusIndicator('success', 'Sistema Activo');
            console.log('✅ Sistema saludable:', data);
        } else {
            updateStatusIndicator('danger', 'Sistema con Issues');
        }
    } catch (error) {
        console.error('❌ Error verificando salud del sistema:', error);
        updateStatusIndicator('danger', 'Error de Conexión');
    }
}

function updateStatusIndicator(type, text) {
    const indicator = document.getElementById('status-indicator');
    if (indicator) {
        indicator.innerHTML = `
            <i class="bi bi-circle-fill text-${type} me-1"></i>
            ${text}
        `;
    }
}

async function loadInitialData() {
    try {
        await Promise.all([
            loadStatistics(),
            loadDocumentTypes(),
            loadSuppliers()
        ]);
    } catch (error) {
        console.error('❌ Error cargando datos iniciales:', error);
        showToast('Error cargando datos iniciales', 'danger');
    }
}

async function loadStatistics() {
    try {
        const response = await fetch(API_ENDPOINTS.stats);
        const stats = await response.json();
        
        // Actualizar sidebar de estadísticas
        document.getElementById('total-docs').textContent = stats.total_documents;
        document.getElementById('avg-confidence').textContent = stats.avg_confidence.toFixed(3);
        document.getElementById('recent-docs').textContent = stats.recent_documents;
        
        // Actualizar distribución por tipos
        updateTypesDistribution(stats.by_type);
        
        return stats;
    } catch (error) {
        console.error('❌ Error cargando estadísticas:', error);
        throw error;
    }
}

function updateTypesDistribution(byType) {
    const container = document.getElementById('types-distribution');
    if (!container || !byType) return;
    
    const colors = {
        'facturas': '#198754',
        'remitos': '#0dcaf0', 
        'notas_credito': '#ffc107',
        'notas_debito': '#dc3545',
        'desconocido': '#6c757d'
    };
    
    let html = '';
    Object.entries(byType).forEach(([type, count]) => {
        const color = colors[type] || '#6c757d';
        html += `
            <div class="type-distribution-item">
                <span>
                    <span class="type-color-indicator" style="background-color: ${color}"></span>
                    ${type}
                </span>
                <span class="badge" style="background-color: ${color}">${count}</span>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

async function loadDocumentTypes() {
    try {
        const response = await fetch(API_ENDPOINTS.types);
        const data = await response.json();
        
        // Actualizar select de tipos en búsqueda
        const select = document.getElementById('search-type');
        if (select && data.types) {
            select.innerHTML = '<option value="">Todos los tipos</option>';
            data.types.forEach(type => {
                select.innerHTML += `<option value="${type}">${type}</option>`;
            });
        }
        
        return data.types;
    } catch (error) {
        console.error('❌ Error cargando tipos:', error);
    }
}

async function loadSuppliers() {
    try {
        const response = await fetch(API_ENDPOINTS.suppliers);
        const data = await response.json();
        
        // Podríamos usar esto para autocompletar proveedores
        return data.suppliers;
    } catch (error) {
        console.error('❌ Error cargando proveedores:', error);
    }
}

// ============================================================================
// DASHBOARD
// ============================================================================

async function loadDashboardData() {
    try {
        const stats = await loadStatistics();
        
        // Crear/actualizar gráfico de tipos
        if (stats.by_type && Object.keys(stats.by_type).length > 0) {
            createTypeChart(stats.by_type);
        }
        
    } catch (error) {
        console.error('❌ Error cargando dashboard:', error);
    }
}

function createTypeChart(byType) {
    const canvas = document.getElementById('typeChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destruir gráfico existente si existe
    if (typeChart) {
        typeChart.destroy();
    }
    
    const labels = Object.keys(byType);
    const data = Object.values(byType);
    const colors = [
        '#198754', '#0dcaf0', '#ffc107', '#dc3545', '#6c757d',
        '#fd7e14', '#6f42c1', '#20c997', '#f8f9fa', '#495057'
    ];
    
    typeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(label => label.replace('_', ' ').toUpperCase()),
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                title: {
                    display: true,
                    text: 'Distribución por Tipo de Documento',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            }
        }
    });
}

async function refreshStats() {
    try {
        showToast('Actualizando estadísticas...', 'info');
        await loadStatistics();
        await loadDashboardData();
        showToast('Estadísticas actualizadas', 'success');
    } catch (error) {
        console.error('❌ Error actualizando stats:', error);
        showToast('Error actualizando estadísticas', 'danger');
    }
}

// ============================================================================
// DOCUMENTOS
// ============================================================================

async function loadDocuments(page = 0, filters = null) {
    try {
        currentPage = page;
        
        let url = `${API_ENDPOINTS.documents}?skip=${page * pageSize}&limit=${pageSize}&order_by=${sortField}&order_desc=${sortDesc}`;
        
        let options = {
            method: 'GET'
        };
        
        // Si hay filtros, usar POST para búsqueda
        if (filters) {
            url = `${API_ENDPOINTS.search}?skip=${page * pageSize}&limit=${pageSize}&order_by=${sortField}&order_desc=${sortDesc}`;
            options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(filters)
            };
        }
        
        const response = await fetch(url, options);
        const documents = await response.json();
        
        displayDocuments(documents);
        updatePagination();
        
        return documents;
    } catch (error) {
        console.error('❌ Error cargando documentos:', error);
        showToast('Error cargando documentos', 'danger');
        return [];
    }
}

function displayDocuments(documents) {
    const tbody = document.getElementById('documents-table');
    if (!tbody) return;
    
    if (!documents || documents.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="bi bi-inbox display-4 opacity-25"></i>
                    <p class="mt-2">No se encontraron documentos</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = documents.map(doc => `
        <tr>
            <td>
                <div class="fw-semibold">${doc.filename}</div>
                <small class="text-muted">ID: ${doc.id}</small>
            </td>
            <td>
                <span class="badge badge-${doc.tipo || 'desconocido'}">${doc.tipo || 'Desconocido'}</span>
            </td>
            <td>${doc.cuit || '-'}</td>
            <td>${doc.proveedor || '-'}</td>
            <td>${doc.fecha_documento || '-'}</td>
            <td>${doc.monto || '-'}</td>
            <td>
                ${doc.confidence ? `
                    <div>
                        <small>${(doc.confidence * 100).toFixed(1)}%</small>
                        <div class="confidence-bar">
                            <div class="confidence-fill confidence-${getConfidenceLevel(doc.confidence)}" 
                                 style="width: ${doc.confidence * 100}%"></div>
                        </div>
                    </div>
                ` : '-'}
            </td>
            <td>
                <small>${formatDate(doc.fecha_procesado)}</small>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="showDocumentDetails(${doc.id})">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function getConfidenceLevel(confidence) {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleString('es-AR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dateString;
    }
}

function updatePagination() {
    const nav = document.getElementById('pagination');
    if (!nav) return;
    
    // Aquí podríamos implementar paginación real
    // Por ahora, botones básicos
    nav.innerHTML = `
        <li class="page-item ${currentPage === 0 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadDocuments(${currentPage - 1})">Anterior</a>
        </li>
        <li class="page-item active">
            <span class="page-link">Página ${currentPage + 1}</span>
        </li>
        <li class="page-item">
            <a class="page-link" href="#" onclick="loadDocuments(${currentPage + 1})">Siguiente</a>
        </li>
    `;
}

function changePageSize() {
    const select = document.getElementById('page-size');
    if (select) {
        pageSize = parseInt(select.value);
        loadDocuments(0);
    }
}

function changeSorting() {
    const select = document.getElementById('sort-field');
    if (select) {
        sortField = select.value;
        loadDocuments(currentPage);
    }
}

function toggleSortOrder() {
    sortDesc = !sortDesc;
    const button = document.getElementById('sort-order');
    if (button) {
        button.innerHTML = sortDesc ? 
            '<i class="bi bi-sort-down"></i>' : 
            '<i class="bi bi-sort-up"></i>';
    }
    loadDocuments(currentPage);
}

async function showDocumentDetails(documentId) {
    try {
        const response = await fetch(`${API_ENDPOINTS.documents}/${documentId}`);
        const document = await response.json();
        
        const modalBody = document.getElementById('document-details');
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Información General</h6>
                        <table class="table table-sm">
                            <tr><td class="fw-semibold">ID:</td><td>${document.id}</td></tr>
                            <tr><td class="fw-semibold">Archivo:</td><td>${document.filename}</td></tr>
                            <tr><td class="fw-semibold">Tipo:</td><td><span class="badge badge-${document.tipo || 'desconocido'}">${document.tipo || 'Desconocido'}</span></td></tr>
                            <tr><td class="fw-semibold">CUIT:</td><td>${document.cuit || 'N/A'}</td></tr>
                            <tr><td class="fw-semibold">Proveedor:</td><td>${document.proveedor || 'N/A'}</td></tr>
                            <tr><td class="fw-semibold">Fecha Doc.:</td><td>${document.fecha_documento || 'N/A'}</td></tr>
                            <tr><td class="fw-semibold">Monto:</td><td>${document.monto || 'N/A'}</td></tr>
                            <tr><td class="fw-semibold">Confianza:</td><td>${document.confidence ? (document.confidence * 100).toFixed(2) + '%' : 'N/A'}</td></tr>
                            <tr><td class="fw-semibold">Procesado:</td><td>${formatDate(document.fecha_procesado)}</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Detalles de Clasificación</h6>
                        <div class="bg-light p-3 rounded">
                            ${document.detalles_clasificacion ? 
                                `<pre class="small mb-0">${JSON.stringify(document.detalles_clasificacion, null, 2)}</pre>` :
                                '<p class="text-muted mb-0">No hay detalles de clasificación disponibles</p>'
                            }
                        </div>
                    </div>
                </div>
            `;
        }
        
        const modal = new bootstrap.Modal(document.getElementById('documentModal'));
        modal.show();
        
    } catch (error) {
        console.error('❌ Error cargando detalles del documento:', error);
        showToast('Error cargando detalles del documento', 'danger');
    }
}

// ============================================================================
// BÚSQUEDA AVANZADA
// ============================================================================

function loadSearchOptions() {
    // Los tipos y proveedores ya se cargan en loadInitialData
    console.log('🔍 Tab de búsqueda cargado');
}

function performSearch(event) {
    event.preventDefault();
    
    const filters = {
        cuit: document.getElementById('search-cuit')?.value || null,
        proveedor: document.getElementById('search-supplier')?.value || null,
        tipo: document.getElementById('search-type')?.value || null,
        fecha_desde: document.getElementById('search-date-from')?.value || null,
        fecha_hasta: document.getElementById('search-date-to')?.value || null,
        confidence_min: parseFloat(document.getElementById('search-confidence')?.value) || null
    };
    
    // Filtrar valores nulos/vacíos
    const cleanFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== null && v !== '')
    );
    
    console.log('🔍 Realizando búsqueda con filtros:', cleanFilters);
    
    // Realizar búsqueda y mostrar en resultados
    searchDocuments(cleanFilters);
}

async function searchDocuments(filters) {
    try {
        const documents = await loadDocuments(0, filters);
        
        // Mostrar resultados en el área de search-results
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer && documents.length > 0) {
            resultsContainer.innerHTML = `
                <h6>Resultados de búsqueda (${documents.length} documentos encontrados)</h6>
                <div class="table-responsive">
                    <table class="table table-hover table-striped">
                        <thead class="table-dark">
                            <tr>
                                <th>Archivo</th>
                                <th>Tipo</th>
                                <th>CUIT</th>
                                <th>Proveedor</th>
                                <th>Fecha Doc.</th>
                                <th>Confianza</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${documents.map(doc => `
                                <tr>
                                    <td>${doc.filename}</td>
                                    <td><span class="badge badge-${doc.tipo || 'desconocido'}">${doc.tipo || 'Desconocido'}</span></td>
                                    <td>${doc.cuit || '-'}</td>
                                    <td>${doc.proveedor || '-'}</td>
                                    <td>${doc.fecha_documento || '-'}</td>
                                    <td>${doc.confidence ? (doc.confidence * 100).toFixed(1) + '%' : '-'}</td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" onclick="showDocumentDetails(${doc.id})">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-search display-1 opacity-25"></i>
                    <p class="mt-2">No se encontraron documentos que coincidan con los filtros</p>
                </div>
            `;
        }
        
        showToast(`Búsqueda completada: ${documents.length} documentos encontrados`, 'info');
        
    } catch (error) {
        console.error('❌ Error en búsqueda:', error);
        showToast('Error realizando búsqueda', 'danger');
    }
}

// ============================================================================
// PROCESAMIENTO
// ============================================================================

async function checkProcessingStatus() {
    try {
        // Verificar estado del directorio de entrada
        const response = await fetch(API_ENDPOINTS.inputStatus);
        const status = await response.json();
        
        const statusDiv = document.getElementById('process-status');
        if (statusDiv && status) {
            if (status.total_files > 0) {
                statusDiv.innerHTML = `
                    <i class="bi bi-files me-2 text-info"></i>
                    ${status.total_files} archivos listos para procesar
                `;
                statusDiv.className = 'alert alert-info';
            } else {
                statusDiv.innerHTML = '<i class="bi bi-pause-circle me-2"></i>No hay archivos para procesar';
                statusDiv.className = 'alert alert-secondary';
            }
        }
    } catch (error) {
        console.error('Error verificando estado:', error);
        const statusDiv = document.getElementById('process-status');
        if (statusDiv) {
            statusDiv.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>Error verificando estado';
            statusDiv.className = 'alert alert-warning';
        }
    }
}

async function startProcessing() {
    try {
        // Verificar primero si hay archivos para procesar
        const statusResponse = await fetch(API_ENDPOINTS.inputStatus);
        const inputStatus = await statusResponse.json();
        
        if (inputStatus.total_files === 0) {
            showToast('No hay archivos PDF en la carpeta input_pdfs para procesar', 'warning');
            return;
        }
        
        const enableML = document.getElementById('enable-ml')?.checked ?? true;
        const enableLayout = document.getElementById('enable-layout')?.checked ?? true;
        
        const request = {
            enable_ml: enableML,
            enable_layout: enableLayout,
            move_files: true
        };
        
        console.log('🚀 Iniciando procesamiento con:', request);
        console.log('📁 Archivos a procesar:', inputStatus.total_files);
        
        const response = await fetch(API_ENDPOINTS.process, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });
        
        const result = await response.json();
        console.log('📋 Respuesta del servidor:', result);
        
        if (response.ok) {
            if (result.status === 'no_files') {
                showToast(result.message, 'warning');
                return;
            }
            
            showProcessingStarted(result);
            showToast(`Procesamiento iniciado: ${result.files_found || 'varios'} archivos`, 'success');
            
            // Verificar progreso más frecuentemente
            setTimeout(() => {
                checkProcessingProgress();
            }, 3000);
        } else {
            throw new Error(result.detail || 'Error iniciando procesamiento');
        }
        
    } catch (error) {
        console.error('❌ Error iniciando procesamiento:', error);
        showToast(`Error iniciando procesamiento: ${error.message}`, 'danger');
    }
}

async function checkProcessingProgress() {
    try {
        // Verificar si aún hay archivos en input_pdfs
        const response = await fetch(API_ENDPOINTS.inputStatus);
        const status = await response.json();
        
        if (status.total_files === 0) {
            // No hay archivos, probablemente se procesaron
            showProcessingCompleted();
            refreshStats();
            showToast('Procesamiento completado exitosamente', 'success');
        } else {
            // Aún hay archivos, seguir esperando
            setTimeout(() => {
                checkProcessingProgress();
            }, 2000);
        }
    } catch (error) {
        console.error('Error verificando progreso:', error);
        showProcessingCompleted();
    }
}

function showProcessingStarted(result) {
    const statusDiv = document.getElementById('process-status');
    const progressDiv = document.getElementById('process-progress');
    
    if (statusDiv) {
        const filesCount = result?.files_found || 'varios';
        statusDiv.innerHTML = `<i class="bi bi-gear me-2 text-warning"></i>Procesando ${filesCount} archivos...`;
        statusDiv.className = 'alert alert-warning processing-active';
    }
    
    if (progressDiv) {
        progressDiv.classList.remove('d-none');
    }
}

function showProcessingCompleted() {
    const statusDiv = document.getElementById('process-status');
    const progressDiv = document.getElementById('process-progress');
    
    if (statusDiv) {
        statusDiv.innerHTML = '<i class="bi bi-check-circle me-2 text-success"></i>Procesamiento completado';
        statusDiv.className = 'alert alert-success processing-success';
    }
    
    if (progressDiv) {
        progressDiv.classList.add('d-none');
    }
    
    // Volver al estado normal después de un tiempo
    setTimeout(() => {
        checkProcessingStatus();
    }, 3000);
}

// ============================================================================
// EXPORTACIÓN
// ============================================================================

async function exportData(format = 'csv') {
    try {
        showToast(`Preparando exportación ${format.toUpperCase()}...`, 'info');
        
        const response = await fetch(`${API_ENDPOINTS.export}/${format}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `documentos_export_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showToast(`Archivo ${format.toUpperCase()} descargado exitosamente`, 'success');
        } else {
            throw new Error(`Error en exportación: ${response.status}`);
        }
        
    } catch (error) {
        console.error(`❌ Error exportando ${format}:`, error);
        showToast(`Error exportando archivo ${format.toUpperCase()}`, 'danger');
    }
}

// ============================================================================
// UTILIDADES
// ============================================================================

function showToast(message, type = 'info') {
    // Crear toast dinámico
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: type === 'danger' ? 5000 : 3000
    });
    
    toast.show();
    
    // Limpiar después de ocultar
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1100';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Función global para debugging
window.AgenteAPI = {
    loadDocuments,
    loadStatistics,
    exportData,
    showToast,
    checkSystemHealth
};