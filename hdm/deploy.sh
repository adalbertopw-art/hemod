#!/bin/bash
# Script de despliegue automatizado para Cloudflare Pages
# Archivo: deploy.sh

set -e

echo "🚀 Iniciando despliegue del Sistema de Hemodiálisis en Cloudflare..."

# Verificar si wrangler está instalado
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI no está instalado"
    echo "📦 Instalando Wrangler..."
    npm install -g wrangler
fi

# Verificar autenticación
echo "🔐 Verificando autenticación con Cloudflare..."
if ! wrangler whoami &> /dev/null; then
    echo "❌ No estás autenticado con Cloudflare"
    echo "🔑 Por favor ejecuta: wrangler login"
    exit 1
fi

echo "✅ Autenticación verificada"

# Crear base de datos D1 si no existe
echo "🗄️ Configurando base de datos D1..."
DB_NAME="hemodialisis-db"

# Verificar si la base de datos ya existe
if wrangler d1 list | grep -q "$DB_NAME"; then
    echo "✅ Base de datos $DB_NAME ya existe"
else
    echo "📊 Creando base de datos D1..."
    wrangler d1 create "$DB_NAME"
    echo "✅ Base de datos $DB_NAME creada"
    echo "⚠️  IMPORTANTE: Copia el database_id del output anterior y actualiza wrangler.toml"
    read -p "Presiona Enter cuando hayas actualizado wrangler.toml..."
fi

# Inicializar esquema de base de datos
echo "🏗️ Inicializando esquema de base de datos..."
if [ -f "schema.sql" ]; then
    wrangler d1 execute "$DB_NAME" --file=schema.sql
    echo "✅ Esquema inicializado con datos de ejemplo"
else
    echo "❌ Archivo schema.sql no encontrado"
    exit 1
fi

# Verificar estructura del proyecto
echo "📁 Verificando estructura del proyecto..."
required_files=("public/index.html" "functions/api/[[path]].js" "wrangler.toml" "package.json")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Archivo requerido no encontrado: $file"
        exit 1
    fi
done

echo "✅ Estructura del proyecto verificada"

# Instalar dependencias si existen
if [ -f "package.json" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Desplegar a Cloudflare Pages
echo "🚀 Desplegando a Cloudflare Pages..."

# Opción 1: Despliegue directo
PROJECT_NAME="hemodialisis-app"

# Crear proyecto si no existe
if ! wrangler pages project list | grep -q "$PROJECT_NAME"; then
    echo "📝 Creando proyecto Pages..."
    wrangler pages project create "$PROJECT_NAME" --production-branch main
fi

# Publicar
echo "📤 Publicando archivos..."
wrangler pages publish public --project-name "$PROJECT_NAME"

# Configurar D1 binding
echo "🔗 Configurando binding de base de datos..."
wrangler pages project edit "$PROJECT_NAME" --d1 "DB=$DB_NAME"

echo ""
echo "🎉 ¡Despliegue completado exitosamente!"
echo ""
echo "📊 Tu aplicación está disponible en:"
echo "   https://$PROJECT_NAME.pages.dev"
echo ""
echo "🔧 Para configurar un dominio personalizado:"
echo "   1. Ve a Cloudflare Dashboard → Pages → $PROJECT_NAME"
echo "   2. Selecciona 'Custom domains'"
echo "   3. Añade tu dominio"
echo ""
echo "📈 Para monitorizar:"
echo "   wrangler pages deployment tail --project-name $PROJECT_NAME"
echo ""
echo "✅ ¡Sistema de Hemodiálisis desplegado y funcionando!"