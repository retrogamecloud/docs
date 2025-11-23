#!/usr/bin/env python3
"""
Intelligent Documentation Analyzer with Claude AI
Analiza toda la documentación y arquitectura del proyecto para proponer mejoras
"""
import os
import sys
import json
import argparse
import anthropic
from pathlib import Path
from datetime import datetime
from json_repair import repair_json

def scan_directory_structure(base_path):
    """Escanea la estructura completa del directorio"""
    structure = {"files": [], "dirs": []}
    
    for root, dirs, files in os.walk(base_path):
        # Ignorar directorios ocultos y node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        rel_root = os.path.relpath(root, base_path)
        if rel_root != '.':
            structure["dirs"].append(rel_root)
        
        for file in files:
            if file.endswith(('.md', '.mdx', '.js', '.py', '.tf', '.yml', '.yaml')):
                structure["files"].append(os.path.join(rel_root, file))
    
    return structure

def read_documentation_files(docs_path, max_files=50):
    """Lee los archivos de documentación existentes"""
    docs_content = {}
    docs_dir = Path(docs_path)
    
    # Buscar archivos .mdx y .md
    doc_files = list(docs_dir.rglob('*.mdx')) + list(docs_dir.rglob('*.md'))
    doc_files = [f for f in doc_files if not any(part.startswith('.') for part in f.parts)]
    
    print(f"📚 Encontrados {len(doc_files)} archivos de documentación")
    
    for doc_file in doc_files[:max_files]:
        try:
            rel_path = doc_file.relative_to(docs_dir)
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Limitar a primeros 2000 caracteres por archivo
                docs_content[str(rel_path)] = content[:2000] if len(content) > 2000 else content
        except Exception as e:
            print(f"⚠️  Error leyendo {doc_file}: {e}")
    
    return docs_content

def analyze_architecture_files(repos_path):
    """Analiza archivos clave de arquitectura en los repos"""
    architecture = {
        "services": [],
        "infrastructure": [],
        "apis": [],
        "configs": []
    }
    
    repos_dir = Path(repos_path)
    
    # Buscar archivos importantes
    important_patterns = [
        "**/package.json",
        "**/README.md",
        "**/*.tf",
        "**/docker-compose.yml",
        "**/Dockerfile",
        "**/kong.yml"
    ]
    
    for pattern in important_patterns:
        for file in repos_dir.rglob(pattern):
            if not any(part.startswith('.') or part == 'node_modules' for part in file.parts):
                rel_path = file.relative_to(repos_dir)
                category = categorize_file(str(rel_path))
                
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()[:1000]  # Primeros 1000 chars
                        architecture[category].append({
                            "file": str(rel_path),
                            "preview": content
                        })
                except:
                    pass
    
    return architecture

def categorize_file(filepath):
    """Categoriza un archivo según su tipo"""
    if 'package.json' in filepath or 'Dockerfile' in filepath:
        return 'services'
    elif '.tf' in filepath or 'infrastructure' in filepath:
        return 'infrastructure'
    elif 'kong' in filepath or 'api' in filepath.lower():
        return 'apis'
    else:
        return 'configs'

def create_comprehensive_prompt(docs_content, architecture, docs_structure, analysis_depth):
    """Crea un prompt comprehensivo para Claude"""
    
    prompt = f"""Eres un arquitecto de software senior y experto en documentación técnica. Analiza COMPLETAMENTE esta documentación y arquitectura de sistema para proponer mejoras integrales.

## CONTEXTO DEL PROYECTO

Sistema: RetroGameCloud - Plataforma de juegos retro con microservicios

Repositorios:
- backend: Servicios de autenticación, catálogo, scores, ranking, usuarios
- frontend: Interfaz web con JS-DOS para emulación
- infrastructure: Terraform para AWS (EKS, CloudFront, Route53, OAuth2)
- kong: API Gateway con configuración de rutas y plugins
- kubernetes: Manifiestos K8s para despliegue

## DOCUMENTACIÓN ACTUAL

Total de archivos: {len(docs_content)}

### Estructura de documentación:
{json.dumps(docs_structure, indent=2)}

### Contenido de documentación (muestra):
"""
    
    # Añadir muestra de docs
    for i, (filepath, content) in enumerate(list(docs_content.items())[:15]):
        prompt += f"\n#### {filepath}\n```\n{content[:500]}...\n```\n"
    
    prompt += f"""

## ARQUITECTURA DEL SISTEMA

### Servicios identificados:
{json.dumps([s['file'] for s in architecture['services'][:10]], indent=2)}

### Infraestructura:
{json.dumps([i['file'] for i in architecture['infrastructure'][:10]], indent=2)}

### APIs y Gateway:
{json.dumps([a['file'] for a in architecture['apis'][:10]], indent=2)}

## ANÁLISIS REQUERIDO (Profundidad: {analysis_depth})

Analiza TODO y propón mejoras en:

1. **ESTRUCTURA Y ORGANIZACIÓN**
   - ¿La estructura actual tiene sentido?
   - ¿Falta alguna sección importante?
   - ¿Hay que reorganizar o consolidar secciones?

2. **CONTENIDO Y GAPS**
   - ¿Qué documentación crítica falta?
   - ¿Qué aspectos están mal documentados?
   - ¿Qué ejemplos o tutoriales faltan?

3. **CONSOLIDACIÓN Y REORGANIZACIÓN (PRIORIDAD MÁXIMA)**
   - ¿Hay archivos duplicados o con contenido similar que deberían fusionarse?
   - ¿Hay páginas sin numeración correcta (formato X.Y. Título)?
   - ¿Archivos en ubicaciones incorrectas que deben moverse?
   - ¿Contenido redundante que debe eliminarse?
   - ¿Estructura de navegación confusa que necesita simplificación?

4. **DIAGRAMAS Y VISUALIZACIONES**
   - ¿Qué diagramas de arquitectura se necesitan? (especifica tipo: secuencia, componentes, flujo, etc)
   - ¿Qué visualizaciones ayudarían? (gráficos, tablas comparativas, etc)
   - Propón contenido exacto en Mermaid.js

5. **MEJORAS DE CALIDAD**
   - Inconsistencias en estilo o formato
   - Información desactualizada o contradictoria
   - Mejoras en claridad y usabilidad

**IMPORTANTE**: ANTES de crear archivos nuevos, verifica si ya existe contenido similar que puede mejorarse o consolidarse. Prioriza MODIFICAR y REORGANIZAR sobre CREAR.

## FORMATO DE RESPUESTA

**IMPORTANTE: TODO el contenido debe estar en español de España (castellano), incluyendo títulos, descripciones, contenido propuesto y diagramas. Usa terminología técnica en español cuando exista traducción estándar (por ejemplo: "Despliegue" en lugar de "Deployment", "Autenticación" en lugar de "Authentication", etc.).**

Responde en JSON puro (sin markdown, sin bloques ```):

{{
  "analysis_summary": "Resumen ejecutivo del análisis en 2-3 líneas EN ESPAÑOL DE ESPAÑA",
  "overall_score": 7.5,
  "improvements": [
    {{
      "priority": "high|medium|low",
      "category": "structure|content|diagrams|quality|new_section",
      "title": "Título de la mejora EN ESPAÑOL",
      "description": "Descripción detallada EN ESPAÑOL",
      "files_to_create": ["path/to/new/file.mdx"],
      "files_to_modify": ["path/to/existing/file.mdx"],
      "files_to_delete": ["path/to/obsolete/file.mdx"],
      "proposed_content": "",
      "mermaid_diagram": "",
      "rationale": "Por qué es importante EN ESPAÑOL (máx 100 chars)"
    }}
  ],
  ],
  "new_sections": [
    {{
      "name": "Nombre de sección EN ESPAÑOL",
      "description": "Propósito de la sección EN ESPAÑOL",
      "files": [
        {{
          "filename": "section/intro.mdx",
          "title": "Título EN ESPAÑOL",
          "content_outline": "Outline del contenido EN ESPAÑOL"
        }}
      ]
    }}
  ],
  "diagrams_needed": [
    {{
      "type": "architecture|sequence|flow|component",
      "title": "Título del diagrama EN ESPAÑOL",
      "description": "Qué muestra EN ESPAÑOL",
      "location": "Dónde colocarlo",
      "mermaid_code": "Código mermaid con labels EN ESPAÑOL"
    }}
  ],
  "quick_wins": [
    "Mejoras rápidas que se pueden implementar ya EN ESPAÑOL"
  ],
  "critical_gaps": [
    "Documentación crítica que falta EN ESPAÑOL"
  ]
}}

**REGLAS CRÍTICAS PARA JSON VÁLIDO (OBLIGATORIO):**

⚠️ LONGITUD MÁXIMA ESTRICTA:
- analysis_summary: MÁXIMO 150 caracteres
- title: MÁXIMO 70 caracteres
- description: MÁXIMO 180 caracteres
- proposed_content: DEJAR VACÍO "" (no incluir contenido)
- mermaid_diagram: DEJAR VACÍO "" (no incluir diagramas)
- rationale: MÁXIMO 100 caracteres

🚨 FORMATO JSON CRÍTICO:
1. NO incluyas bloques de código en proposed_content
2. NO incluyas saltos de línea (\n) en ningún string
3. proposed_content y mermaid_diagram: usa "" vacío
4. Si algo es largo, RESUME o usa ""
5. Máximo 8-10 mejoras totales

🎯 PRIORIDAD ABSOLUTA: CONSOLIDACIÓN PRIMERO
Cuando detectes duplicación:
- files_to_delete: ["archivo1.mdx", "archivo2.mdx"] ← OBLIGATORIO
- files_to_modify: ["archivo-destino.mdx"] ← donde se consolida
- category: "structure"
- priority: "high"
- description: "Fusionar X e Y en Z, eliminar duplicados"

💡 ESTRATEGIA:
1. Identifica 2-3 consolidaciones críticas (alta prioridad)
2. Identifica 3-4 correcciones de numeración
3. Identifica 2-3 mejoras de contenido existente
4. Propón 1-2 archivos nuevos SOLO si son esenciales
TOTAL: Máximo 10-12 mejoras

RECUERDA: 
- TODO en español de España
- SÉ BREVE Y PRECISO
- Prioriza CONSOLIDAR > MEJORAR > CREAR
- Strings cortos = JSON válido
"""
    
    return prompt

def analyze_with_claude(client, docs_content, architecture, docs_structure, analysis_depth):
    """Realiza el análisis con Claude"""
    
    prompt = create_comprehensive_prompt(docs_content, architecture, docs_structure, analysis_depth)
    
    print(f"🤖 Enviando análisis a Claude Sonnet 4.5...")
    print(f"📊 Tokens estimados: ~{len(prompt) // 4}")
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16384,  # Aumentado para respuestas completas sin truncar
            temperature=0.3,  # Más determinista para JSON consistente
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        print(f"✅ Respuesta recibida ({len(response_text)} chars)")
        print(f"📄 Primeros 1000 caracteres de la respuesta:")
        print(response_text[:1000])
        print(f"\n📄 Últimos 500 caracteres de la respuesta:")
        print(response_text[-500:])
        
        # Limpiar markdown code blocks si existen
        json_text = response_text
        if "```json" in json_text:
            print("🔍 Detectado bloque de código markdown ```json, extrayendo...")
            json_start = json_text.find("```json") + 7
            json_end = json_text.find("```", json_start)
            if json_end == -1:
                json_end = len(json_text)
            json_text = json_text[json_start:json_end].strip()
            print(f"✅ JSON extraído de markdown, longitud: {len(json_text)} caracteres")
            print(f"🔍 Primeros 200 chars después de extraer: {json_text[:200]}")
        elif "```" in json_text:
            print("🔍 Detectado bloque de código genérico, extrayendo...")
            json_start = json_text.find("```") + 3
            json_end = json_text.find("```", json_start)
            if json_end == -1:
                json_end = len(json_text)
            json_text = json_text[json_start:json_end].strip()
            print(f"✅ JSON extraído de bloque genérico, longitud: {len(json_text)} caracteres")
        
        # NUEVO: Limpieza agresiva del JSON antes de parsear
        print("🧹 Limpiando JSON...")
        
        # Eliminar saltos de línea dentro de strings (causa principal del problema)
        # Buscar patrones como "text\n  more text" y reemplazar por "text more text"
        import re
        
        # Paso 1: Encontrar todos los strings y limpiarlos
        def clean_json_string(match):
            content = match.group(1)
            # Reemplazar saltos de línea y múltiples espacios por un solo espacio
            cleaned = re.sub(r'\s+', ' ', content)
            # Limitar longitud si es muy largo
            if len(cleaned) > 300:
                cleaned = cleaned[:297] + "..."
            return f'"{cleaned}"'
        
        # Limpiar strings entre comillas que contengan saltos de línea
        json_text = re.sub(r'"([^"]*(?:\n[^"]*)*)"', clean_json_string, json_text)
        
        print(f"✅ JSON limpiado, longitud final: {len(json_text)} caracteres")
        
        # Intentar parsear
        try:
            result = json.loads(json_text)
            print("✅ JSON parseado correctamente")
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parseando JSON: {e}")
            print(f"📄 Error en posición: línea {e.lineno}, columna {e.colno}")
            print(f"📄 Primeros 500 chars del JSON:")
            print(json_text[:500])
            print(f"\n📄 Últimos 500 chars del JSON:")
            print(json_text[-500:])
            
            # Intentar reparar el JSON con estrategias incrementales
            try:
                print("🔧 Estrategia 1: Reparación con json-repair...")
                repaired = repair_json(json_text)
                result = json.loads(repaired)
                print("✅ JSON reparado exitosamente con json-repair")
                return result
            except Exception as repair_error_1:
                print(f"❌ json-repair falló: {repair_error_1}")
                
                # Estrategia 2: Truncar en el último } válido
                try:
                    print("🔧 Estrategia 2: Buscar última llave válida...")
                    last_brace = json_text.rfind('}')
                    if last_brace > 0:
                        truncated = json_text[:last_brace + 1]
                        result = json.loads(truncated)
                        print(f"✅ JSON parseado truncando a posición {last_brace}")
                        return result
                except Exception as repair_error_2:
                    print(f"❌ Truncado falló: {repair_error_2}")
                    
                    # Estrategia 3: Retornar estructura mínima
                    print("⚠️  Usando estructura de análisis mínima por defecto")
                    return {
                        "analysis_summary": "Error parseando respuesta de Claude",
                        "critical_gaps": [],
                        "improvements": [],
                        "new_pages_needed": []
                    }
            
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return None

def generate_improvements_report(analysis_result, output_path):
    """Genera reporte de mejoras en Markdown"""
    
    if not analysis_result:
        return False
    
    report = f"""# 🤖 Análisis Inteligente de Documentación

**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Generado por**: Claude Sonnet 4.5  
**Puntuación General**: {analysis_result.get('overall_score', 'N/A')}/10

## 📊 Resumen Ejecutivo

{analysis_result.get('analysis_summary', 'Sin resumen')}

## 🎯 Mejoras Prioritarias

"""
    
    improvements = analysis_result.get('improvements', [])
    
    # Agrupar por prioridad
    for priority in ['high', 'medium', 'low']:
        priority_items = [imp for imp in improvements if imp.get('priority') == priority]
        
        if priority_items:
            priority_label = {"high": "Alta ⚡", "medium": "Media 📌", "low": "Baja 💡"}[priority]
            report += f"\n### Prioridad {priority_label}\n\n"
            
            for imp in priority_items:
                report += f"#### {imp.get('title', 'Sin título')}\n\n"
                report += f"**Categoría**: {imp.get('category', 'N/A')}  \n"
                report += f"**Descripción**: {imp.get('description', '')}  \n"
                report += f"**Razón**: {imp.get('rationale', '')}  \n\n"
                
                if imp.get('files_to_create'):
                    report += f"**Archivos a crear**: {', '.join(imp['files_to_create'])}  \n"
                if imp.get('files_to_modify'):
                    report += f"**Archivos a modificar**: {', '.join(imp['files_to_modify'])}  \n"
                if imp.get('mermaid_diagram'):
                    report += f"\n**Diagrama propuesto**:\n```mermaid\n{imp['mermaid_diagram']}\n```\n\n"
                
                report += "\n---\n\n"
    
    # Nuevas secciones
    new_sections = analysis_result.get('new_sections', [])
    if new_sections:
        report += "\n## 📁 Nuevas Secciones Propuestas\n\n"
        for section in new_sections:
            report += f"### {section.get('name', 'Sin nombre')}\n\n"
            report += f"{section.get('description', '')}  \n\n"
            
            files = section.get('files', [])
            if files:
                report += "**Archivos**:\n"
                for file in files:
                    report += f"- `{file.get('filename', '')}`: {file.get('title', '')}  \n"
                report += "\n"
    
    # Diagramas necesarios
    diagrams = analysis_result.get('diagrams_needed', [])
    if diagrams:
        report += "\n## 📈 Diagramas Requeridos\n\n"
        for diag in diagrams:
            # Validar que diag sea un diccionario
            if isinstance(diag, str):
                report += f"- {diag}\n"
                continue
            
            report += f"### {diag.get('title', 'Diagrama')}\n\n"
            report += f"**Tipo**: {diag.get('type', 'N/A')}  \n"
            report += f"**Ubicación**: {diag.get('location', 'N/A')}  \n"
            report += f"**Descripción**: {diag.get('description', '')}  \n\n"
            
            if diag.get('mermaid_code'):
                report += f"{diag['mermaid_code']}\n\n"
    
    # Quick wins
    quick_wins = analysis_result.get('quick_wins', [])
    if quick_wins:
        report += "\n## ⚡ Quick Wins\n\n"
        for win in quick_wins:
            report += f"- {win}  \n"
    
    report += "\n\n---\n*Análisis generado automáticamente*\n"
    
    # Guardar reporte
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Reporte generado: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Intelligent Documentation Analyzer')
    parser.add_argument('--docs-path', required=True, help='Path to docs repository')
    parser.add_argument('--repos-path', required=True, help='Path to source repositories')
    parser.add_argument('--depth', default='full', choices=['quick', 'full', 'deep'])
    parser.add_argument('--output', default='analysis-results.json')
    
    args = parser.parse_args()
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY no configurada")
        sys.exit(1)
    
    print("🚀 Iniciando análisis inteligente de documentación...")
    print(f"📂 Docs: {args.docs_path}")
    print(f"📂 Repos: {args.repos_path}")
    print(f"🔍 Profundidad: {args.depth}")
    
    # 1. Escanear estructura
    print("\n📊 Escaneando estructura...")
    docs_structure = scan_directory_structure(args.docs_path)
    print(f"   ✓ {len(docs_structure['files'])} archivos, {len(docs_structure['dirs'])} directorios")
    
    # 2. Leer documentación
    print("\n📚 Leyendo documentación...")
    docs_content = read_documentation_files(args.docs_path)
    print(f"   ✓ {len(docs_content)} archivos procesados")
    
    # 3. Analizar arquitectura
    print("\n🏗️  Analizando arquitectura...")
    architecture = analyze_architecture_files(args.repos_path)
    print(f"   ✓ {len(architecture['services'])} servicios, {len(architecture['infrastructure'])} infra files")
    
    # 4. Análisis con Claude
    print("\n🤖 Ejecutando análisis con Claude AI...")
    client = anthropic.Anthropic(api_key=api_key)
    
    analysis_result = analyze_with_claude(
        client, 
        docs_content, 
        architecture, 
        docs_structure, 
        args.depth
    )
    
    if not analysis_result:
        print("❌ Análisis falló")
        sys.exit(1)
    
    # 5. Guardar resultados
    print(f"\n💾 Guardando resultados en {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    
    # 6. Generar reporte
    print("\n📝 Generando reporte de mejoras...")
    if generate_improvements_report(analysis_result, 'IMPROVEMENTS.md'):
        print("✅ Reporte generado: IMPROVEMENTS.md")
    
    # 7. Resumen
    improvements_count = len(analysis_result.get('improvements', []))
    diagrams_count = len(analysis_result.get('diagrams_needed', []))
    sections_count = len(analysis_result.get('new_sections', []))
    
    print(f"\n🎉 Análisis completado!")
    print(f"   📋 {improvements_count} mejoras propuestas")
    print(f"   📊 {diagrams_count} diagramas recomendados")
    print(f"   📁 {sections_count} secciones nuevas sugeridas")
    print(f"   ⭐ Puntuación: {analysis_result.get('overall_score', 'N/A')}/10")

if __name__ == '__main__':
    main()
