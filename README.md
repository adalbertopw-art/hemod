# Sistema Integral de Hemodiálisis

Sistema web completo desarrollado en Flask para el manejo integral de pacientes con enfermedad renal crónica en hemodiálisis.

## 🚀 Características Principales

- **Gestión Completa de Pacientes**: Registro, búsqueda y seguimiento
- **Dashboard Inteligente**: Métricas en tiempo real y visualizaciones
- **Sistema de Alertas**: Clasificadas por criticidad médica
- **API REST Completa**: Endpoints para todas las operaciones
- **Base de Datos Integrada**: SQLite con datos de ejemplo
- **Interface Responsiva**: Optimizada para desktop, tablet y móvil
- **Terminología Médica**: Especializada para Colombia

## 📋 Requisitos

- Python 3.8 o superior
- Flask 2.3+
- SQLite (incluido con Python)

## 🔧 Instalación Local

1. **Clonar repositorio:**
```bash
git clone <tu-repositorio>
cd hemodialisis-render
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecutar aplicación:**
```bash
python app.py
```

5. **Abrir en navegador:**
```
http://localhost:5000
```

## 🌐 Despliegue en Render.com

### Método 1: Desde GitHub (Recomendado)

1. **Sube este repositorio a GitHub**
2. **Ve a [render.com](https://render.com)**
3. **Crea cuenta gratuita**
4. **New + → Web Service**
5. **Connect a repository → Selecciona tu repo**
6. **Configuración:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
7. **Deploy**

### Método 2: Deploy Manual

1. **Comprimir proyecto en ZIP**
2. **Subir a Render.com directamente**

## 📊 Funcionalidades

### Dashboard Principal
- Métricas de pacientes activos
- Contadores de alertas por categoría
- Centro de alertas recientes
- Visualización en tiempo real

### Gestión de Pacientes
- Formulario de registro completo
- Validación de documentos colombianos
- Lista interactiva de pacientes
- Cálculos automáticos de edad y tiempo en diálisis

### Sistema de Alertas
- **Críticas**: Requieren atención inmediata
- **Moderadas**: Seguimiento necesario
- **Preventivas**: Alertas tempranas

### API REST
- `GET /api/patients` - Lista de pacientes
- `POST /api/patients` - Crear paciente
- `GET /api/alerts` - Alertas activas
- `GET /api/patients/<id>` - Paciente específico

## 📁 Estructura del Proyecto

```
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── templates/
│   └── index.html        # Template HTML principal
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   └── js/
│       └── app.js        # JavaScript del frontend
└── README.md             # Este archivo
```

## 🗄️ Base de Datos

### Tablas Principales
- **pacientes**: Información demográfica y clínica
- **laboratorios**: Resultados de análisis clínicos
- **alertas**: Sistema de notificaciones médicas

### Datos de Ejemplo
El sistema incluye 3 pacientes de ejemplo con:
- Datos demográficos completos
- Historial de laboratorios
- Alertas médicas generadas automáticamente

## 🎯 Casos de Uso

### Para Clínicas Pequeñas (20-50 pacientes)
- Costo: Gratuito en Render.com
- Funcionalidades completas
- Sin límites de funcionalidad

### Para Centros Medianos (50-200 pacientes)
- Escalabilidad automática
- Performance optimizado
- Backup automático

## 🔒 Seguridad

- Validación de datos de entrada
- Sanitización de SQL queries
- CORS configurado correctamente
- Headers de seguridad implementados

## 🚀 Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Base de Datos**: SQLite
- **UI Framework**: Bootstrap 5
- **Iconos**: Font Awesome 6
- **Servidor**: Gunicorn (producción)

## 📞 Soporte

Para reportar problemas o solicitar características:
1. Crear issue en GitHub
2. Incluir pasos para reproducir el error
3. Especificar navegador y sistema operativo

## 📄 Licencia

Sistema desarrollado para uso médico profesional.

## 🔄 Próximas Versiones

- [ ] Módulo de sesiones de diálisis
- [ ] Reportes en PDF
- [ ] Gráficos de evolución temporal
- [ ] Sistema de notificaciones por email
- [ ] App móvil complementaria

---

**Desarrollado con ❤️ para mejorar el cuidado de pacientes en hemodiálisis**
