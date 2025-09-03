// Sistema de Hemodiálisis - JavaScript Principal
class HemodialysisApp {
    constructor() {
        this.patients = [];
        this.alerts = [];
        this.isLoading = false;
        this.init();
    }

    init() {
        console.log('🏥 Iniciando Sistema de Hemodiálisis...');
        this.loadInitialData();
        this.setupEventListeners();
        this.showSection('dashboard');
    }

    setupEventListeners() {
        // Formulario de nuevo paciente
        const newPatientForm = document.getElementById('new-patient-form');
        if (newPatientForm) {
            newPatientForm.addEventListener('submit', (e) => this.handleNewPatient(e));
        }

        // Mostrar tooltips de Bootstrap
        this.initializeTooltips();
    }

    initializeTooltips() {
        // Inicializar tooltips si Bootstrap está disponible
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    async loadInitialData() {
        if (this.isLoading) return;

        this.isLoading = true;
        console.log('📊 Cargando datos iniciales...');

        try {
            await Promise.all([
                this.loadPatients(),
                this.loadAlerts()
            ]);

            this.updateDashboard();
            console.log('✅ Datos cargados exitosamente');
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.showError('Error al cargar los datos del sistema');
        } finally {
            this.isLoading = false;
        }
    }

    async loadPatients() {
        try {
            console.log('👥 Cargando pacientes...');
            const response = await fetch('/api/patients');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.patients = await response.json();
            console.log(`✅ ${this.patients.length} pacientes cargados`);

        } catch (error) {
            console.error('❌ Error loading patients:', error);
            this.patients = [];
            throw error;
        }
    }

    async loadAlerts() {
        try {
            console.log('🚨 Cargando alertas...');
            const response = await fetch('/api/alerts');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.alerts = await response.json();
            console.log(`✅ ${this.alerts.length} alertas cargadas`);

        } catch (error) {
            console.error('❌ Error loading alerts:', error);
            this.alerts = [];
            throw error;
        }
    }

    updateDashboard() {
        console.log('📊 Actualizando dashboard...');

        // Actualizar métricas principales
        this.updateElement('total-patients', this.patients.length);

        const criticalAlerts = this.alerts.filter(a => a.tipo === 'CRITICA').length;
        const moderateAlerts = this.alerts.filter(a => a.tipo === 'MODERADA').length;
        const preventiveAlerts = this.alerts.filter(a => a.tipo === 'PREVENTIVA').length;

        this.updateElement('critical-alerts', criticalAlerts);
        this.updateElement('moderate-alerts', moderateAlerts);
        this.updateElement('preventive-alerts', preventiveAlerts);

        // Renderizar alertas
        this.renderAlerts();

        console.log('✅ Dashboard actualizado');
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = value;
        }
    }

    renderAlerts() {
        const container = document.getElementById('alerts-container');
        const allAlertsContainer = document.getElementById('all-alerts-container');

        if (!container) return;

        if (this.alerts.length === 0) {
            const noAlertsHtml = `
                <div class="text-center text-success py-4">
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <h5>No hay alertas activas</h5>
                    <p class="text-muted">Todos los pacientes están dentro de parámetros normales</p>
                </div>
            `;
            container.innerHTML = noAlertsHtml;
            if (allAlertsContainer) allAlertsContainer.innerHTML = noAlertsHtml;
            return;
        }

        // Mostrar las 5 alertas más importantes en el dashboard
        const dashboardAlerts = this.alerts
            .sort((a, b) => b.prioridad - a.prioridad)
            .slice(0, 5);

        const alertsHtml = dashboardAlerts.map(alert => this.renderAlert(alert)).join('');
        const allAlertsHtml = this.alerts.map(alert => this.renderAlert(alert)).join('');

        container.innerHTML = alertsHtml;
        if (allAlertsContainer) allAlertsContainer.innerHTML = allAlertsHtml;
    }

    renderAlert(alert) {
        const alertClasses = {
            'CRITICA': 'alert-critical',
            'MODERADA': 'alert-moderate',
            'PREVENTIVA': 'alert-preventive'
        };

        const alertIcons = {
            'CRITICA': 'fas fa-exclamation-triangle text-danger',
            'MODERADA': 'fas fa-exclamation-circle text-warning',
            'PREVENTIVA': 'fas fa-info-circle text-info'
        };

        const alertClass = alertClasses[alert.tipo] || 'alert-preventive';
        const icon = alertIcons[alert.tipo] || 'fas fa-info-circle';

        return `
            <div class="${alertClass}">
                <div class="d-flex align-items-start">
                    <i class="${icon} me-3 mt-1" style="font-size: 1.2rem;"></i>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <strong class="text-dark">${alert.tipo} - ${alert.categoria}</strong>
                            <span class="badge bg-secondary">Prioridad ${alert.prioridad}</span>
                        </div>
                        <div class="mb-2">
                            <strong>Paciente:</strong> 
                            <span class="text-primary">${alert.paciente_nombre}</span>
                        </div>
                        <div class="mb-2">
                            <strong>Mensaje:</strong> ${alert.mensaje}
                        </div>
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${new Date(alert.fecha_creacion).toLocaleDateString('es-CO', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            })}
                        </small>
                    </div>
                </div>
            </div>
        `;
    }

    renderPatients() {
        const container = document.getElementById('patients-table');
        if (!container) return;

        if (this.patients.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h5>No hay pacientes registrados</h5>
                    <p>Utiliza el formulario de la izquierda para registrar el primer paciente</p>
                </div>
            `;
            return;
        }

        const table = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-hashtag me-1"></i>ID</th>
                            <th><i class="fas fa-id-card me-1"></i>Documento</th>
                            <th><i class="fas fa-user me-1"></i>Nombre Completo</th>
                            <th><i class="fas fa-birthday-cake me-1"></i>Edad</th>
                            <th><i class="fas fa-venus-mars me-1"></i>Género</th>
                            <th><i class="fas fa-hospital me-1"></i>EPS</th>
                            <th><i class="fas fa-clipboard-list me-1"></i>Causa ERC</th>
                            <th><i class="fas fa-clock me-1"></i>Tiempo HD</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.patients.map(patient => `
                            <tr>
                                <td><span class="badge bg-primary">${patient.id}</span></td>
                                <td>
                                    <strong>${patient.documento}</strong>
                                </td>
                                <td>
                                    <strong>${patient.nombres} ${patient.apellidos}</strong>
                                </td>
                                <td>
                                    ${patient.edad} años
                                </td>
                                <td>
                                    <i class="fas fa-${patient.genero === 'M' ? 'mars text-primary' : 'venus text-danger'} me-1"></i>
                                    ${patient.genero === 'M' ? 'Masculino' : 'Femenino'}
                                </td>
                                <td>
                                    <span class="badge bg-info">${patient.eps || 'N/A'}</span>
                                </td>
                                <td>
                                    <small>${patient.causa_erc || 'No especificada'}</small>
                                </td>
                                <td>
                                    <span class="badge bg-success">${patient.tiempo_dialisis_meses} meses</span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <div class="mt-3 text-muted text-center">
                <small>
                    <i class="fas fa-info-circle me-1"></i>
                    Total de pacientes activos: <strong>${this.patients.length}</strong>
                </small>
            </div>
        `;

        container.innerHTML = table;
    }

    async handleNewPatient(e) {
        e.preventDefault();

        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        // Deshabilitar botón y mostrar loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Registrando...';

        try {
            const formData = new FormData(e.target);
            const patientData = Object.fromEntries(formData.entries());

            console.log('👤 Registrando nuevo paciente:', patientData);

            const response = await fetch('/api/patients', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(patientData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('✅ Paciente registrado:', result);

            this.showSuccess(`Paciente registrado exitosamente con ID: ${result.id}`);
            e.target.reset();

            // Recargar datos
            await this.loadPatients();
            this.renderPatients();
            this.updateDashboard();

        } catch (error) {
            console.error('❌ Error creating patient:', error);
            this.showError(`Error al registrar el paciente: ${error.message}`);
        } finally {
            // Restaurar botón
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Remover notificaciones existentes
        const existingNotifications = document.querySelectorAll('.notification-toast');
        existingNotifications.forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} notification-toast position-fixed`;
        notification.style.cssText = `
            top: 20px; 
            right: 20px; 
            z-index: 9999; 
            min-width: 350px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            border-radius: 8px;
        `;

        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);

        console.log(`${type === 'success' ? '✅' : '❌'} ${message}`);
    }

    showSection(sectionName) {
        console.log(`📄 Mostrando sección: ${sectionName}`);

        // Ocultar todas las secciones
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });

        // Mostrar la sección seleccionada
        const selectedSection = document.getElementById(`${sectionName}-section`);
        if (selectedSection) {
            selectedSection.style.display = 'block';

            // Renderizar contenido específico de la sección
            if (sectionName === 'patients') {
                this.renderPatients();
            } else if (sectionName === 'dashboard') {
                this.updateDashboard();
            } else if (sectionName === 'alerts') {
                this.renderAlerts();
            }
        }

        // Actualizar navegación activa
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
    }
}

// Funciones globales
function showSection(sectionName) {
    if (window.app) {
        window.app.showSection(sectionName);

        // Actualizar navegación activa
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Encontrar y activar el enlace correcto
        const activeLink = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM cargado, inicializando aplicación...');
    window.app = new HemodialysisApp();
});

// Manejo de errores globales
window.addEventListener('error', (event) => {
    console.error('❌ Error global:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Promise rechazada:', event.reason);
});