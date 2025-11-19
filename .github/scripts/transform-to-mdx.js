#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const tempDocsDir = path.join(__dirname, '../../temp-docs');
const apiDocsDir = path.join(__dirname, '../../api-reference');

// Asegurar que existe el directorio de destino
if (!fs.existsSync(apiDocsDir)) {
  fs.mkdirSync(apiDocsDir, { recursive: true });
}

// Mapeo de servicios a títulos y descripciones
const serviceMetadata = {
  // Backend Services
  'auth-service': {
    title: 'Auth Service API',
    description: 'Endpoints de autenticación, registro y gestión de tokens JWT',
    icon: 'shield',
    category: 'backend'
  },
  'game-catalog-service': {
    title: 'Game Catalog API',
    description: 'Catálogo de juegos retro disponibles en la plataforma',
    icon: 'gamepad',
    category: 'backend'
  },
  'score-service': {
    title: 'Score Service API',
    description: 'Gestión de puntuaciones y validación anti-trampas',
    icon: 'trophy',
    category: 'backend'
  },
  'ranking-service': {
    title: 'Ranking Service API',
    description: 'Rankings globales y por juego con cache inteligente',
    icon: 'chart-bar',
    category: 'backend'
  },
  'user-service': {
    title: 'User Service API',
    description: 'Perfiles de usuario y gestión de datos personales',
    icon: 'user',
    category: 'backend'
  },
  'backend-main': {
    title: 'Backend Monolith API',
    description: 'API principal del backend monolítico',
    icon: 'server',
    category: 'backend'
  },
  
  // Frontend
  'frontend': {
    title: 'Frontend Client',
    description: 'Interfaz de usuario y cliente web de Retro Game Hub',
    icon: 'window',
    category: 'frontend'
  },
  
  // Infrastructure
  'infrastructure-docs': {
    title: 'Infrastructure as Code',
    description: 'Módulos Terraform para AWS EKS, VPC, RDS y Redis',
    icon: 'cloud',
    category: 'infrastructure'
  },
  
  // Kong
  'kong-config': {
    title: 'Kong Gateway',
    description: 'Configuración del API Gateway Kong',
    icon: 'route',
    category: 'infrastructure'
  },
  
  // Kubernetes
  'kubernetes-manifests': {
    title: 'Kubernetes Manifests',
    description: 'Deployments, Services, ConfigMaps y Secrets de K8s',
    icon: 'cubes',
    category: 'infrastructure'
  }
};

// Procesar cada archivo de documentación
if (fs.existsSync(tempDocsDir)) {
  const files = fs.readdirSync(tempDocsDir);
  
  files.forEach(file => {
    if (file.endsWith('-api.md') || file.endsWith('-docs.md') || file.endsWith('-config.md') || file.endsWith('-manifests.md')) {
      const serviceName = file.replace(/-(api|docs|config|manifests)\.md$/, '');
      const metadata = serviceMetadata[serviceName] || {
        title: serviceName,
        description: 'Documentación generada automáticamente',
        icon: 'code',
        category: 'other'
      };
      
      // Leer contenido generado
      const mdContent = fs.readFileSync(
        path.join(tempDocsDir, file),
        'utf-8'
      );
      
      // Crear MDX con frontmatter adaptado al tipo de contenido
      let mdxContent;
      
      if (metadata.category === 'infrastructure') {
        // Formato especial para infraestructura
        mdxContent = `---
title: "${metadata.title}"
description: "${metadata.description}"
icon: "${metadata.icon}"
---

<Info>
  Documentación de infraestructura generada automáticamente.
  Última actualización: ${new Date().toISOString().split('T')[0]}
</Info>

${mdContent}

## Uso

Para aplicar esta infraestructura:

\`\`\`bash
cd infrastructure
terraform init
terraform plan
terraform apply
\`\`\`

<Warning>
  Revisa los costos estimados antes de aplicar cambios en producción.
</Warning>
`;
      } else if (metadata.category === 'backend') {
        // Formato para APIs backend
        mdxContent = `---
title: "${metadata.title}"
description: "${metadata.description}"
icon: "${metadata.icon}"
---

<Info>
  Documentación generada automáticamente desde el código fuente.
  Última actualización: ${new Date().toISOString().split('T')[0]}
</Info>

${mdContent}

## Autenticación

Todos los endpoints requieren un token JWT válido en el header:

\`\`\`
Authorization: Bearer <token>
\`\`\`

<Warning>
  Los tokens expiran después de 24 horas. Usa el endpoint de refresh para renovarlos.
</Warning>
`;
      } else if (metadata.category === 'frontend') {
        // Formato para frontend
        mdxContent = `---
title: "${metadata.title}"
description: "${metadata.description}"
icon: "${metadata.icon}"
---

<Info>
  Documentación del cliente frontend generada automáticamente.
  Última actualización: ${new Date().toISOString().split('T')[0]}
</Info>

${mdContent}

## Desarrollo Local

Para ejecutar el frontend localmente:

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

<Note>
  El frontend se conecta al backend en \`http://localhost:3000\` por defecto.
</Note>
`;
      } else {
        // Formato genérico
        mdxContent = `---
title: "${metadata.title}"
description: "${metadata.description}"
icon: "${metadata.icon}"
---

<Info>
  Documentación generada automáticamente.
  Última actualización: ${new Date().toISOString().split('T')[0]}
</Info>

${mdContent}
`;
      }
      
      // Escribir archivo MDX
      const outputPath = path.join(apiDocsDir, `${serviceName}.mdx`);
      fs.writeFileSync(outputPath, mdxContent);
      
      console.log(`✅ Generated: ${outputPath}`);
    }
  });
  
  console.log('\n✨ Documentation transformation complete!');
} else {
  console.log('⚠️  No temp-docs directory found. Skipping transformation.');
}
