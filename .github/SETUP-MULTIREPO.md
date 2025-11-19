# 🚀 Setup Multi-Repo para Todos los Repositorios

## 📦 Repositorios a Configurar

Este sistema sincroniza documentación desde **5 repositorios**:

1. **Backend** - Servicios de backend / API monolítica
2. **Frontend** - Cliente web y UI
3. **Infrastructure** - Terraform (AWS EKS, VPC, RDS, Redis)
4. **Kong** - Configuración del API Gateway
5. **Kubernetes** - Manifests de K8s

---

## ⚡ Setup Global (Una sola vez)

### 1️⃣ Crear Personal Access Token

```bash
GitHub.com → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)

Nombre: docs-sync-token-multirepo
Scopes: 
  ✅ repo (Full control)
  ✅ workflow (Update workflows)
Expiration: 90 días o sin expiración
```

**📋 Copia el token**, lo usarás 6 veces.

---

### 2️⃣ Añadir PAT_TOKEN a TODOS los Repositorios

Repite este paso en **cada uno de los 6 repos**:

```bash
# Para cada repositorio:
# - retrogamecloud/docs
# - retrogamecloud/backend
# - retrogamecloud/frontend
# - retrogamecloud/infrastructure
# - retrogamecloud/kong
# - retrogamecloud/kubernetes

Settings → Secrets and variables → Actions → New repository secret

Name: PAT_TOKEN
Value: <pega-tu-token-aquí>
```

---

## 📂 Copiar Workflows a Cada Repositorio

### Backend

```bash
cd /ruta/a/backend
mkdir -p .github/workflows

cp /mnt/c/proyecto_final/docs/.github/workflows/notify-docs-backend.yml \
   .github/workflows/notify-docs.yml

git add .github/workflows/notify-docs.yml
git commit -m "ci: add docs sync notification"
git push
```

---

### Frontend

```bash
cd /ruta/a/frontend
mkdir -p .github/workflows

cp /mnt/c/proyecto_final/docs/.github/workflows/notify-docs-frontend.yml \
   .github/workflows/notify-docs.yml

git add .github/workflows/notify-docs.yml
git commit -m "ci: add docs sync notification"
git push
```

---

### Infrastructure

```bash
cd /ruta/a/infrastructure
mkdir -p .github/workflows

cp /mnt/c/proyecto_final/docs/.github/workflows/notify-docs-infrastructure.yml \
   .github/workflows/notify-docs.yml

git add .github/workflows/notify-docs.yml
git commit -m "ci: add docs sync notification"
git push
```

---

### Kong

```bash
cd /ruta/a/kong
mkdir -p .github/workflows

cp /mnt/c/proyecto_final/docs/.github/workflows/notify-docs-kong.yml \
   .github/workflows/notify-docs.yml

git add .github/workflows/notify-docs.yml
git commit -m "ci: add docs sync notification"
git push
```

---

### Kubernetes

```bash
cd /ruta/a/kubernetes
mkdir -p .github/workflows

cp /mnt/c/proyecto_final/docs/.github/workflows/notify-docs-kubernetes.yml \
   .github/workflows/notify-docs.yml

git add .github/workflows/notify-docs.yml
git commit -m "ci: add docs sync notification"
git push
```

---

## ✅ Verificar Setup

### Opción 1: Ejecutar Manualmente

```bash
# Ve a GitHub Actions del repo docs
https://github.com/retrogamecloud/docs/actions

# Click en "Sync Documentation from Backend"
# Run workflow → Run workflow
# Espera 3-5 minutos
```

### Opción 2: Hacer Push de Prueba

```bash
# En cualquier repositorio (backend, frontend, etc.)
echo "# Test" >> README.md
git add README.md
git commit -m "test: trigger docs sync"
git push

# Ve a Actions del repo docs
# Deberías ver el workflow ejecutándose automáticamente
```

---

## 🔄 Flujo Completo Multi-Repo

```
┌──────────────────────────────────────────────────────────────┐
│  Developer hace cambios en CUALQUIER repositorio            │
└──────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
    Backend             Frontend          Infrastructure
      Push                Push                 Push
        ↓                   ↓                   ↓
    Kong Push         Kubernetes Push      (todos detectan)
        ↓                   ↓                   ↓
        └───────────────────┼───────────────────┘
                            ↓
              GitHub Actions notifica al repo docs
                            ↓
              Workflow "sync-docs.yml" se ejecuta
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
    Clona             Clona                Clona
    Backend           Frontend         Infrastructure
        ↓                   ↓                   ↓
    Genera            Genera              Extrae
    JSDoc             JSDoc               Configs
        ↓                   ↓                   ↓
        └───────────────────┼───────────────────┘
                            ↓
              Transform to MDX (+ frontmatter)
                            ↓
                  Commit & Push al repo docs
                            ↓
              Mintlify detecta → Wiki actualizada ✨
```

---

## 📊 Qué se Genera Automáticamente

| Repositorio | Archivo Generado | Contenido |
|-------------|------------------|-----------|
| **Backend** | `auth-service.mdx`, `score-service.mdx`, etc. | API docs desde JSDoc |
| **Frontend** | `frontend.mdx` | Cliente web, funciones JS |
| **Infrastructure** | `infrastructure-docs.mdx` | Módulos Terraform, variables, outputs |
| **Kong** | `kong-config.mdx` | Configuración YAML del gateway |
| **Kubernetes** | `kubernetes-manifests.mdx` | Deployments, Services, ConfigMaps |

---

## 🎯 Triggers por Repositorio

### Backend
- Archivos: `src/**/*.js`, `**/*.controller.js`, `**/*.service.js`
- Frecuencia: Cada push a main

### Frontend
- Archivos: `**/*.js`, `**/*.html`, `**/*.css`, `package.json`
- Frecuencia: Cada push a main

### Infrastructure
- Archivos: `**/*.tf`, `**/*.tfvars`, `modules/**/*`
- Frecuencia: Cada push a main

### Kong
- Archivos: `**/*.yml`, `**/*.yaml`, `kong.yml`
- Frecuencia: Cada push a main

### Kubernetes
- Archivos: `**/*.yml`, `**/*.yaml`, `deployments/**/*`, `services/**/*`
- Frecuencia: Cada push a main

### Adicional: Sync Programado
- **Cada 6 horas** automáticamente (sin necesidad de push)

---

## 🐛 Troubleshooting

### Error: "Resource not accessible by integration"

**Causa**: PAT_TOKEN no tiene permisos suficientes

**Solución**:
```bash
# Verifica que el token tenga scopes 'repo' y 'workflow'
# Regenera el token si es necesario
# Actualiza el secret en TODOS los 6 repositorios
```

---

### No se ejecuta el workflow

**Causa**: Paths incorrectos o secret faltante

**Solución**:
```bash
# Verifica que PAT_TOKEN exista en el repositorio:
Settings → Secrets and variables → Actions

# Verifica los paths en notify-docs.yml coincidan con tu estructura
```

---

### Workflow falla al clonar repositorio

**Causa**: Nombre de repositorio incorrecto en sync-docs.yml

**Solución**:
```bash
# Edita .github/workflows/sync-docs.yml
# Líneas con "repository: retrogamecloud/NOMBRE"
# Cambia NOMBRE por el nombre real de tu repo
```

---

### No aparece documentación generada

**Causa**: Sin comentarios JSDoc o estructura incorrecta

**Backend - Añade JSDoc**:
```javascript
/**
 * Autentica un usuario
 * @param {Object} req - Request
 * @param {Object} res - Response
 * @returns {Object} Token JWT
 */
async function login(req, res) {
  // ...
}
```

**Infrastructure - Comenta tus variables**:
```hcl
variable "cluster_name" {
  description = "Nombre del cluster EKS"
  type        = string
  default     = "retrogame-cluster"
}
```

---

## 📈 Monitoreo

### Ver último sync:
```bash
# En GitHub Actions del repo docs
https://github.com/retrogamecloud/docs/actions

# Busca: "Sync Documentation from Backend"
# Click en la última ejecución
# Expande cada step para ver detalles
```

### Ver archivos generados:
```bash
cd /mnt/c/proyecto_final/docs
ls -la api-reference/

# Deberías ver:
# auth-service.mdx
# frontend.mdx
# infrastructure-docs.mdx
# kong-config.mdx
# kubernetes-manifests.mdx
# etc.
```

---

## 🎨 Personalización

### Cambiar frecuencia de sync automático

Edita `.github/workflows/sync-docs.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Cada 6 horas (actual)
  # Cambia a:
  - cron: '0 0 * * *'    # Diario a medianoche
  - cron: '0 */12 * * *' # Cada 12 horas
  - cron: '0 0 * * 1'    # Semanal (lunes a medianoche)
```

### Añadir más paths que disparen sync

Edita en cada repo el archivo `notify-docs.yml`:

```yaml
paths:
  - 'src/**/*.js'
  - 'lib/**/*.ts'      # Añadir TypeScript
  - 'api/**/*.go'      # Añadir Go
  - 'docs/**/*.md'     # Añadir cambios en docs
```

---

## 📚 Archivos de Workflow Creados

En el repo **docs** (ya están):
- ✅ `.github/workflows/sync-docs.yml`
- ✅ `.github/workflows/notify-docs-backend.yml` → copiar a backend
- ✅ `.github/workflows/notify-docs-frontend.yml` → copiar a frontend
- ✅ `.github/workflows/notify-docs-infrastructure.yml` → copiar a infrastructure
- ✅ `.github/workflows/notify-docs-kong.yml` → copiar a kong
- ✅ `.github/workflows/notify-docs-kubernetes.yml` → copiar a kubernetes
- ✅ `.github/scripts/transform-to-mdx.js`

---

## ✨ Resultado Final

Después del setup completo:

- ✅ **5 repositorios** sincronizando docs automáticamente
- ✅ Cambios en **cualquier repo** → wiki actualizada
- ✅ Sync programado cada **6 horas** (configurable)
- ✅ Ejecución **manual** cuando lo necesites
- ✅ Documentación **siempre actualizada** con el código
- ✅ **Sin intervención manual** en el día a día

---

## 🆘 Soporte

Si algo falla:

1. ✅ Verifica que PAT_TOKEN esté en **los 6 repos**
2. ✅ Confirma que el token tenga scopes `repo` y `workflow`
3. ✅ Revisa nombres de repos en `sync-docs.yml`
4. ✅ Verifica logs en GitHub Actions
5. ✅ Confirma paths en cada `notify-docs.yml`

---

**¡Todo listo para sincronización multi-repo!** 🎉
