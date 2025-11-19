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
  'auth-service': {
    title: 'Auth Service API',
    description: 'Endpoints de autenticación, registro y gestión de tokens JWT',
    icon: 'shield'
  },
  'game-catalog-service': {
    title: 'Game Catalog API',
    description: 'Catálogo de juegos retro disponibles en la plataforma',
    icon: 'gamepad'
  },
  'score-service': {
    title: 'Score Service API',
    description: 'Gestión de puntuaciones y validación anti-trampas',
    icon: 'trophy'
  },
  'ranking-service': {
    title: 'Ranking Service API',
    description: 'Rankings globales y por juego con cache inteligente',
    icon: 'chart-bar'
  },
  'user-service': {
    title: 'User Service API',
    description: 'Perfiles de usuario y gestión de datos personales',
    icon: 'user'
  }
};

// Procesar cada archivo de documentación
if (fs.existsSync(tempDocsDir)) {
  const files = fs.readdirSync(tempDocsDir);
  
  files.forEach(file => {
    if (file.endsWith('-api.md')) {
      const serviceName = file.replace('-api.md', '');
      const metadata = serviceMetadata[serviceName] || {
        title: serviceName,
        description: 'API Documentation',
        icon: 'code'
      };
      
      // Leer contenido generado
      const mdContent = fs.readFileSync(
        path.join(tempDocsDir, file),
        'utf-8'
      );
      
      // Crear MDX con frontmatter
      const mdxContent = `---
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
