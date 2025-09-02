# Sistema de Hemodiálisis para Cloudflare Pages

Sistema web completo para el manejo integral de pacientes en hemodiálisis, optimizado para despliegue en Cloudflare Pages con Functions y base de datos D1.

## 🚀 Características para Cloudflare

- **Cloudflare Pages**: Hosting estático ultrarrápido
- **Cloudflare Functions**: API serverless con JavaScript
- **Cloudflare D1**: Base de datos SQLite distribuida
- **Edge Computing**: Latencia ultra-baja globalmente
- **Escalabilidad automática**: Sin límites de tráfico
- **SSL/TLS automático**: Seguridad integrada

## 📁 Estructura del Proyecto

```
HEMODIALISIS_CLOUDFLARE/
├── public/                    # Archivos estáticos
│   └── index.html            # Aplicación principal
├── static/
│   ├── css/
│   │   └── style.css         # Estilos personalizados
│   └── js/
│       └── app.js            # Lógica del frontend
├── functions/
│   └── api/
│       └── [[path]].js       # API serverless
├── package.json              # Configuración Node.js
├── wrangler.toml            # Configuración Cloudflare
├── schema.sql               # Esquema base de datos D1
└── README.md                # Esta documentación
```

## 🛠 Instalación y Despliegue

### Paso 1: Preparación Local

1. **Instalar Wrangler CLI**:
   ```bash
   npm install -g wrangler
   ```

2. **Autenticar con Cloudflare**:
   ```bash
   wrangler login
   ```

3. **Clonar/descargar el proyecto** y navegar al directorio:
   ```bash
   cd HEMODIALISIS_CLOUDFLARE
   ```

### Paso 2: Configurar Base de Datos D1

1. **Crear base de datos D1**:
   ```bash
   wrangler d1 create hemodialisis-db
   ```

2. **Copiar el database_id** del output y actualizar `wrangler.toml`:
   ```toml
   [[d1_databases]]
   binding = "DB"
   database_name = "hemodialisis-db"
   database_id = "TU_DATABASE_ID_AQUI"
   ```

3. **Inicializar esquema**:
   ```bash
   wrangler d1 execute hemodialisis-db --file=schema.sql
   ```

### Paso 3: Desplegar en Cloudflare Pages

#### Opción A: Desde Git (Recomendado)

1. **Subir código a GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/hemodialisis-app.git
   git push -u origin main
   ```

2. **En Cloudflare Dashboard**:
   - Ir a **Pages** → **Create a project**
   - Conectar con GitHub
   - Seleccionar repositorio
   - **Build settings**:
     - Framework preset: `None`
     - Build command: `echo "No build needed"`
     - Build output directory: `public`

3. **Configurar Variables de Entorno**:
   - En Pages → Settings → Environment variables
   - Añadir: `NODE_VERSION = 18`

#### Opción B: Despliegue Directo con Wrangler

1. **Desplegar directamente**:
   ```bash
   wrangler pages publish public --project-name hemodialisis-app
   ```

2. **Configurar Functions**:
   ```bash
   wrangler pages deployment create --project-name hemodialisis-app
   ```

### Paso 4: Configuración Final

1. **Verificar D1 binding** en Cloudflare Dashboard:
   - Pages → tu-proyecto → Settings → Functions
   - D1 database bindings: `DB = hemodialisis-db`

2. **Dominio personalizado** (opcional):
   - Pages → Custom domains
   - Añadir tu dominio

## 🌐 Endpoints de la API

### Pacientes
- `GET /api/patients` - Obtener todos los pacientes
- `POST /api/patients` - Crear nuevo paciente
- `GET /api/patients/{id}` - Obtener paciente específico

### Laboratorios
- `POST /api/labs` - Registrar resultado de laboratorio

### Sesiones de Diálisis
- `POST /api/sessions` - Registrar sesión de diálisis

### Alertas
- `GET /api/alerts` - Obtener alertas activas

### Ejemplo de uso:
```javascript
// Crear nuevo paciente
const response = await fetch('/api/patients', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        documento: '12345678',
        tipo_documento: 'CC',
        nombres: 'Juan',
        apellidos: 'Pérez',
        fecha_nacimiento: '1980-01-01',
        genero: 'M',
        eps: 'Nueva EPS',
        fecha_inicio_hd: '2024-01-01',
        causa_erc: 'Diabetes Mellitus tipo 2'
    })
});
```

## 📊 Base de Datos D1

### Comandos Útiles:

```bash
# Ver tablas
wrangler d1 execute hemodialisis-db --command="SELECT name FROM sqlite_master WHERE type='table';"

# Consultar pacientes
wrangler d1 execute hemodialisis-db --command="SELECT * FROM pacientes LIMIT 5;"

# Backup de datos
wrangler d1 export hemodialisis-db --output=backup.sql

# Restaurar desde backup
wrangler d1 execute hemodialisis-db --file=backup.sql
```

## 🔧 Desarrollo Local

1. **Instalar dependencias**:
   ```bash
   npm install
   ```

2. **Ejecutar en modo desarrollo**:
   ```bash
   wrangler pages dev public --d1 DB=hemodialisis-db
   ```

3. **Acceder localmente**:
   ```
   http://localhost:8788
   ```

## 🔒 Seguridad y Configuración

### Variables de Entorno
Configurar en Cloudflare Pages:
```
NODE_VERSION=18
ENVIRONMENT=production
```

### Configuración CORS
Las APIs incluyen headers CORS automáticos:
```javascript
'Access-Control-Allow-Origin': '*'
'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
'Access-Control-Allow-Headers': 'Content-Type, Authorization'
```

## 📈 Monitorización

### Analytics de Cloudflare
- Visitas y rendimiento en tiempo real
- Métricas de Functions y D1
- Logs de errores automáticos

### Comandos de monitorización:
```bash
# Ver logs en tiempo real
wrangler pages deployment tail

# Métricas de D1
wrangler d1 info hemodialisis-db

# Estado del despliegue
wrangler pages project list
```

## 🚀 Características de Rendimiento

### Edge Computing
- **Latencia global < 50ms**
- **100+ ubicaciones mundiales**
- **Caché automático de assets**

### Escalabilidad
- **Requests ilimitados**
- **Concurrent users: Sin límite**
- **D1 queries: 100,000/día gratis**

### Disponibilidad
- **99.9% uptime garantizado**
- **DDoS protection automático**
- **Failover automático**

## 💰 Costos Estimados

### Plan Gratuito Cloudflare:
- **500 builds/mes**: ✅ Suficiente
- **100 custom domains**: ✅ Más que suficiente
- **Functions requests**: 100,000/día gratis
- **D1**: 5GB gratis + 100k queries/día

### Estimación para clínica mediana (100 pacientes):
- **Costo mensual**: $0 - $5 USD
- **Requests típicos**: <10,000/día
- **Storage D1**: <100MB

## 🔄 Actualizaciones

### Automáticas desde Git:
```bash
git add .
git commit -m "Actualización"
git push origin main
# Cloudflare despliega automáticamente
```

### Manuales:
```bash
wrangler pages publish public --project-name hemodialisis-app
```

## 🆘 Solución de Problemas

### Error: "D1 binding not found"
```bash
# Verificar configuración
wrangler pages project get hemodialisis-app

# Re-configurar binding
wrangler pages project edit hemodialisis-app --d1 DB=hemodialisis-db
```

### Error: "Function timeout"
```javascript
// En [[path]].js, optimizar queries:
const result = await env.DB.prepare("SELECT * FROM pacientes LIMIT 50").all();
```

### Error de CORS
```javascript
// Verificar headers en respuesta
headers: {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
}
```

## 📞 Soporte

### Recursos Cloudflare:
- [Documentación Oficial](https://developers.cloudflare.com/pages/)
- [Discord Cloudflare](https://discord.cloudflare.com)
- [Workers/Pages Status](https://www.cloudflarestatus.com/)

### Logs y Debug:
```bash
# Ver logs de Functions
wrangler pages deployment tail --project-name hemodialisis-app

# Debug D1
wrangler d1 execute hemodialisis-db --command="PRAGMA table_info(pacientes);"
```

---

## 🎯 URL del Sistema Desplegado

Una vez desplegado, tu aplicación estará disponible en:
```
https://hemodialisis-app.pages.dev
```

O en tu dominio personalizado:
```
https://tu-dominio.com
```

## ✅ Checklist de Despliegue

- [ ] Wrangler CLI instalado
- [ ] Autenticado con Cloudflare
- [ ] Base de datos D1 creada
- [ ] Esquema inicializado
- [ ] Código subido a Git
- [ ] Proyecto conectado en Pages
- [ ] D1 binding configurado
- [ ] Primer despliegue exitoso
- [ ] API funcionando
- [ ] Datos de prueba cargados

**¡Tu sistema de hemodiálisis estará disponible globalmente en minutos!** 🚀