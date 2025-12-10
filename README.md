# 📚 RetroGameCloud - Documentación

[![Mintlify](https://img.shields.io/badge/Powered%20by-Mintlify-blue?logo=markdown)](https://mintlify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Documentación técnica completa de RetroGameCloud. Incluye guías de desarrollo, arquitectura, despliegue, API endpoints, configuración de infraestructura y troubleshooting.

**Documentación General:** [Ir al README Principal](https://github.com/retrogamecloud/.github/blob/main/README.md)  
**Documentación Profesional:** [Acceder a la Wiki](https://www.retrogamehub.games/wiki)

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Estructura de la Documentación](#estructura-de-la-documentación)
- [Desarrollo Local](#desarrollo-local)
- [Configuración](#configuración)
- [Publicación de Cambios](#publicación-de-cambios)
- [Temas Documentados](#temas-documentados)
- [Troubleshooting](#troubleshooting)

---

## 📖 Descripción

Este repositorio contiene la **documentación técnica completa** de RetroGameCloud construida con Mintlify. La documentación incluye:

- ✅ Guías de configuración local y desarrollo
- ✅ Arquitectura del sistema completo
- ✅ Especificaciones de API endpoints
- ✅ Configuración de infraestructura AWS con Terraform
- ✅ Pipelines CI/CD y GitOps con ArgoCD
- ✅ Testing (unit, integration, E2E)
- ✅ Monitoreo y observabilidad
- ✅ Troubleshooting y solución de problemas comunes

---

## 📂 Estructura de la Documentación

```
docs/
├── index.mdx                    # Página principal
├── quickstart.mdx               # Guía de inicio rápido
├── architecture.mdx             # Arquitectura general
├── backend/                     # Documentación del backend
│   ├── overview.mdx
│   ├── api-endpoints.mdx
│   └── database-schema.mdx
├── frontend/                    # Documentación del frontend
│   ├── overview.mdx
│   └── jsdos-integration.mdx
├── infrastructure/              # Infraestructura AWS
│   ├── overview.mdx
│   ├── eks-cluster.mdx
│   ├── rds-database.mdx
│   └── terraform-bootstrap.mdx
├── cicd/                        # CI/CD y GitOps
│   ├── overview.mdx
│   ├── github-actions.mdx
│   └── kubernetes-deployment.mdx
├── kong/                        # API Gateway
│   ├── overview.mdx
│   └── configuration.mdx
├── development/                 # Guías de desarrollo
│   ├── local-setup.mdx
│   ├── testing-guide.mdx
│   └── contributing.mdx
└── troubleshooting/             # Solución de problemas
    └── index.mdx
```

---

## 🛠️ Desarrollo Local

### Prerrequisitos

- Node.js 18+ o superior
- npm 9+ o superior

### Instalación

Instala la [CLI de Mintlify](https://www.npmjs.com/package/mint) para previsualizar los cambios localmente:

```bash
npm i -g mint
```

### Ejecutar en Local

Ejecuta el siguiente comando en la raíz de la documentación (donde está `docs.json`):

```bash
mint dev
```

La documentación estará disponible en **http://localhost:3000**

---

## ⚙️ Configuración

La configuración principal se encuentra en `docs.json`:

- **Navegación:** Define la estructura del menú lateral
- **Tema:** Colores, logo y estilo personalizado
- **Metadatos:** SEO, favicons, analytics
- **Integraciones:** GitHub, feedback widgets

Personaliza el tema visual editando `retro-theme.css` y los componentes en JavaScript.

---

## 🚀 Publicación de Cambios

Los cambios se despliegan **automáticamente a producción** al hacer push a la rama `main`.

1. Realiza cambios en archivos `.mdx`
2. Haz commit y push:
   ```bash
   git add .
   git commit -m "docs: actualizar guía de API"
   git push origin main
   ```
3. Mintlify detecta el cambio vía GitHub App y despliega automáticamente

**No requiere acción manual** después del push.

---

## 📖 Temas Documentados

### Backend
- API REST endpoints completos
- Esquema de base de datos PostgreSQL
- Autenticación JWT y seguridad
- Gestión de usuarios y puntuaciones

### Frontend
- Integración con js-dos para emulación
- Sistema de tracking de puntuaciones
- UI/UX y componentes personalizados

### Infraestructura
- Cluster EKS en AWS
- Base de datos RDS PostgreSQL
- Route53 + SSL/TLS
- Secrets Manager
- Monitoreo con CloudWatch

### CI/CD
- GitHub Actions workflows
- Despliegue GitOps con ArgoCD
- Docker multi-stage builds
- Kubernetes manifests

### Kong API Gateway
- Configuración declarativa
- Rate limiting y CORS
- Routing y plugins

---

## 🔧 Troubleshooting

### El entorno de desarrollo no arranca

Ejecuta `mint update` para asegurar que tienes la versión más reciente de la CLI:

```bash
mint update
```

### Una página carga como 404

Verifica que:
1. Estás ejecutando `mint dev` en la carpeta con el archivo `docs.json`
2. La ruta del archivo `.mdx` está correctamente registrada en `docs.json`
3. El archivo existe y no tiene errores de sintaxis

### Cambios no se reflejan en producción

1. Verifica que la GitHub App de Mintlify esté instalada: [Dashboard](https://dashboard.mintlify.com/settings/organization/github-app)
2. Comprueba que los cambios se hicieron en la rama `main`
3. Revisa los logs de deployment en el dashboard de Mintlify

---

## 📚 Recursos

- [Documentación de Mintlify](https://mintlify.com/docs)
- [Guías de MDX](https://mdxjs.com/docs/)
- [Componentes disponibles](https://mintlify.com/docs/components/overview)
