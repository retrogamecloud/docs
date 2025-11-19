# Sistema de Sincronización Automática de Documentación

## 🎯 Objetivo

Este sistema mantiene la documentación de la API sincronizada automáticamente con el código fuente de los servicios backend.

## 🏗️ Arquitectura

```
┌─────────────────┐         ┌──────────────────┐
│  Backend Repo   │         │   Docs Repo      │
│                 │         │                  │
│  ├─ src/        │         │  ├─ .github/     │
│  │  ├─ auth/   │         │  │  ├─ workflows/│
│  │  ├─ games/  │ ──────> │  │  └─ scripts/  │
│  │  ├─ scores/ │ trigger │  │                │
│  │  └─ ...     │         │  ├─ api-ref/     │
│  │             │         │  │  ├─ auth.mdx  │
│  └─ .github/   │         │  │  ├─ games.mdx │
│     └─ notify  │         │  │  └─ ...       │
└─────────────────┘         └──────────────────┘
```

## 📋 Componentes

### 1. Workflow en Backend (`notify-docs-backend.yml`)
- **Trigger**: Cuando hay cambios en archivos `.js` de `src/`
- **Acción**: Envía evento a repo `docs` vía GitHub API
- **Requiere**: PAT token con permisos de `repo`

### 2. Workflow en Docs (`sync-docs.yml`)
- **Triggers**:
  - `repository_dispatch` desde backend
  - Manual con `workflow_dispatch`
  - Programado cada 6 horas
- **Proceso**:
  1. Clona repo backend
  2. Genera docs con JSDoc
  3. Transforma a formato MDX
  4. Commitea cambios si existen

### 3. Script de Transformación (`transform-to-mdx.js`)
- Convierte Markdown generado por JSDoc a MDX
- Añade frontmatter de Mintlify
- Inserta componentes (`Info`, `Warning`)
- Organiza por servicio

## 🚀 Setup

### Paso 1: Crear Personal Access Token (PAT)

1. Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Nombre: `docs-sync-token`
4. Permisos necesarios:
   - ✅ `repo` (Full control)
   - ✅ `workflow` (Update workflows)
5. Copia el token generado

### Paso 2: Configurar Secrets en Repositorio Docs

1. En el repo `docs`: Settings → Secrets and variables → Actions
2. Crear secret `PAT_TOKEN` con el token del paso 1

### Paso 3: Configurar Secrets en Repositorio Backend

1. En el repo `backend`: Settings → Secrets and variables → Actions
2. Crear secret `PAT_TOKEN` con el mismo token

### Paso 4: Copiar Workflow al Backend

Copia el archivo `.github/workflows/notify-docs-backend.yml` al repositorio backend:

```bash
# En el repo backend
mkdir -p .github/workflows
cp /path/to/docs/.github/workflows/notify-docs-backend.yml .github/workflows/
git add .github/workflows/notify-docs-backend.yml
git commit -m "ci: add docs sync notification workflow"
git push
```

### Paso 5: Ajustar Nombres de Repositorio

Edita `.github/workflows/sync-docs.yml` línea 30:

```yaml
repository: retrogamecloud/backend  # Cambia si tu repo tiene otro nombre
```

### Paso 6: Probar Manualmente

1. Ve a Actions en el repo `docs`
2. Selecciona "Sync Documentation from Backend"
3. Click "Run workflow"
4. Observa la ejecución y verifica errores

## 📝 Formato JSDoc Requerido

Para que la documentación se genere correctamente, documenta tus funciones así:

```javascript
/**
 * Autentica un usuario y genera tokens JWT
 * 
 * @route POST /api/auth/login
 * @param {Object} req.body - Credenciales del usuario
 * @param {string} req.body.email - Email del usuario
 * @param {string} req.body.password - Contraseña
 * @returns {Object} 200 - Token de acceso y refresh token
 * @returns {Object} 401 - Credenciales inválidas
 * @returns {Object} 500 - Error del servidor
 * 
 * @example
 * // Request
 * POST /api/auth/login
 * {
 *   "email": "user@example.com",
 *   "password": "securePassword123"
 * }
 * 
 * @example
 * // Response 200
 * {
 *   "success": true,
 *   "data": {
 *     "token": "eyJhbGciOiJIUzI1NiIs...",
 *     "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
 *     "user": {
 *       "id": 123,
 *       "email": "user@example.com",
 *       "username": "player1"
 *     }
 *   }
 * }
 */
async function login(req, res) {
  // ... implementation
}
```

## 🔄 Flujo de Sincronización

1. **Desarrollador hace push** a `backend/main` con cambios en archivos JS
2. **GitHub Actions detecta** cambios en paths de `src/**/*.js`
3. **Backend workflow** ejecuta y llama a GitHub API
4. **Docs workflow** recibe `repository_dispatch` event
5. **Docs workflow** clona repo backend
6. **JSDoc genera** documentación en formato Markdown
7. **Script transforma** Markdown → MDX con frontmatter
8. **Git commitea** cambios (si existen)
9. **Mintlify detecta** push y actualiza wiki automáticamente

## 🛠️ Troubleshooting

### Error: "Resource not accessible by integration"

**Causa**: Token sin permisos suficientes

**Solución**:
```bash
# Verifica que el PAT_TOKEN tenga permisos de 'repo' y 'workflow'
# Regenera el token si es necesario
```

### No se genera documentación

**Causa**: Archivos sin comentarios JSDoc

**Solución**:
```javascript
// Añade documentación JSDoc a tus funciones
/**
 * Descripción de la función
 * @param {Type} paramName - Descripción
 * @returns {Type} Descripción
 */
```

### Workflow no se ejecuta

**Causa**: Paths incorrectos en el trigger

**Solución**:
```yaml
# Verifica que los paths en notify-docs-backend.yml coincidan
paths:
  - 'src/**/*.js'  # Ajusta según tu estructura
```

### Commit loop infinito

**Causa**: Workflow se activa con sus propios commits

**Solución**: El workflow ya está configurado para evitar esto con:
```yaml
if: steps.check_changes.outputs.has_changes == 'true'
```

## 📊 Monitoreo

### Ver logs de sincronización:
1. Repo `docs` → Actions → "Sync Documentation from Backend"
2. Click en última ejecución
3. Expande cada step para ver detalles

### Verificar cambios generados:
```bash
cd docs
git log --oneline --grep="auto-sync"
```

## 🎨 Personalización

### Cambiar frecuencia de sincronización

Edita `.github/workflows/sync-docs.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Cada 6 horas
  # Cambia a:
  - cron: '0 0 * * *'    # Diario a medianoche
  - cron: '0 */12 * * *' # Cada 12 horas
```

### Añadir más servicios

Edita `.github/scripts/transform-to-mdx.js`:

```javascript
const serviceMetadata = {
  'nuevo-service': {
    title: 'Nuevo Service API',
    description: 'Descripción del servicio',
    icon: 'rocket'
  },
  // ... servicios existentes
};
```

### Cambiar formato de salida

Modifica el template MDX en `transform-to-mdx.js`:

```javascript
const mdxContent = `---
title: "${metadata.title}"
# Añade más campos aquí
---

${mdContent}
`;
```

## 📚 Referencias

- [JSDoc Documentation](https://jsdoc.app/)
- [GitHub Actions - repository_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch)
- [Mintlify MDX Format](https://mintlify.com/docs/content/components)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

## 🤝 Contribuir

Para mejorar este sistema:

1. Fork el repo
2. Crea branch: `git checkout -b feature/mejora-sync`
3. Commitea cambios: `git commit -m 'feat: añadir soporte para TypeScript'`
4. Push: `git push origin feature/mejora-sync`
5. Abre Pull Request

## 📄 Licencia

Este sistema es parte del proyecto Retro Game Hub.
