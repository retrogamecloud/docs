# Guía Rápida de Setup

## 🎯 Objetivo
Configurar sincronización automática de documentación desde backend → docs.

## ⚡ Setup en 5 Minutos

### 1️⃣ Crear Personal Access Token

```bash
# GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
# Nombre: docs-sync-token
# Scopes: ✅ repo, ✅ workflow
# Expiration: 90 días (o sin expiración)
```

**Copia el token**, lo necesitarás en los siguientes pasos.

---

### 2️⃣ Añadir Secret al Repo DOCS

```bash
# Repo: retrogamecloud/docs
# Settings → Secrets and variables → Actions → New repository secret

Name: PAT_TOKEN
Value: <pega-tu-token-aquí>
```

---

### 3️⃣ Añadir Secret al Repo BACKEND

```bash
# Repo: retrogamecloud/backend (o el nombre que uses)
# Settings → Secrets and variables → Actions → New repository secret

Name: PAT_TOKEN
Value: <pega-el-mismo-token>
```

---

### 4️⃣ Copiar Workflow al Backend

Copia el archivo de notificación al repo backend:

```bash
# Desde tu terminal local
cd /ruta/a/backend
mkdir -p .github/workflows

# Copia el contenido de notify-docs-backend.yml
cat > .github/workflows/notify-docs.yml << 'EOF'
name: Notify Docs Update

on:
  push:
    branches:
      - main
    paths:
      - 'src/**/*.js'
      - '**/*.controller.js'
      - '**/*.service.js'

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger docs sync
        run: |
          curl -X POST \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Authorization: token ${{ secrets.PAT_TOKEN }}" \
            https://api.github.com/repos/retrogamecloud/docs/dispatches \
            -d '{"event_type":"docs-update"}'
EOF

# Commit y push
git add .github/workflows/notify-docs.yml
git commit -m "ci: add docs sync notification"
git push
```

---

### 5️⃣ Commit y Push los Workflows

```bash
# En el repo DOCS
cd /mnt/c/proyecto_final/docs
git add -A
git commit -m "ci: add automated documentation sync system

- GitHub Actions workflow for auto-generating API docs
- JSDoc to MDX transformation script
- Setup guide and documentation
- Example auth-service API reference"
git push origin main
```

---

## ✅ Verificar que Funciona

### Opción A: Ejecutar Manualmente

1. Ve a: https://github.com/retrogamecloud/docs/actions
2. Click en "Sync Documentation from Backend"
3. Click "Run workflow" → "Run workflow"
4. Espera 2-3 minutos
5. Verifica que se crearon archivos en `api-reference/`

### Opción B: Hacer Push al Backend

1. Edita cualquier archivo `.js` en el backend
2. Haz commit y push a main
3. Ve a Actions del repo docs
4. Deberías ver un workflow ejecutándose automáticamente

---

## 🐛 Troubleshooting Rápido

### Error: "Resource not accessible by integration"

```bash
# Solución: Verifica que el PAT_TOKEN tenga permisos 'repo' y 'workflow'
# Genera un nuevo token si es necesario
```

### El workflow no se ejecuta

```bash
# Verifica que los paths en notify-docs.yml coincidan con tu estructura
# Ejemplo: si tu código está en 'services/' en lugar de 'src/', cambia:

paths:
  - 'services/**/*.js'  # En lugar de 'src/**/*.js'
```

### No aparece documentación

```bash
# Verifica que tus funciones tengan comentarios JSDoc:

/**
 * Descripción de la función
 * @param {string} param - Descripción del parámetro
 * @returns {Object} Descripción del retorno
 */
function miFuncion(param) {
  // ...
}
```

---

## 📊 Qué Esperar

Después del setup:

- ✅ Cada push a `backend/main` dispara sincronización
- ✅ Documentación se genera automáticamente de JSDoc
- ✅ Archivos MDX aparecen en `api-reference/`
- ✅ Mintlify actualiza la wiki automáticamente
- ✅ También se ejecuta cada 6 horas automáticamente

---

## 🎨 Personalizar

### Cambiar frecuencia de sync

Edita `.github/workflows/sync-docs.yml`:

```yaml
schedule:
  - cron: '0 */12 * * *'  # Cada 12 horas en lugar de 6
```

### Ajustar paths que disparan sync

Edita en backend `.github/workflows/notify-docs.yml`:

```yaml
paths:
  - 'src/**/*.js'
  - 'controllers/**/*.ts'  # Añadir TypeScript
  - 'routes/**/*.js'       # Añadir rutas
```

---

## 📚 Documentación Completa

Para más detalles, ver: `.github/README.md`

---

## 🆘 Soporte

Si algo no funciona:

1. Revisa los logs en GitHub Actions
2. Verifica que los secrets estén configurados
3. Confirma que el token no ha expirado
4. Verifica los nombres de los repositorios en los workflows

---

**¡Listo!** Tu documentación ahora se sincroniza automáticamente. 🎉
