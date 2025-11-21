#!/usr/bin/env python3
"""
Script para generar/actualizar documentación usando Claude (Anthropic)
"""
import os
import sys
import json
import anthropic
from pathlib import Path

def get_changed_files(repo_path):
    """Obtiene archivos cambiados en el último commit"""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n') if result.stdout else []
    except Exception as e:
        print(f"Error obteniendo cambios: {e}")
        return []

def read_file_content(filepath):
    """Lee contenido de un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return ""

def analyze_changes_with_claude(client, repo_name, changed_files, repo_path):
    """Analiza cambios usando Claude y sugiere actualizaciones de docs"""
    
    # Recopilar contexto de archivos cambiados
    files_content = {}
    for file in changed_files[:10]:  # Limitar a 10 archivos para no exceder tokens
        if file and (file.endswith('.js') or file.endswith('.py') or file.endswith('.tf')):
            filepath = Path(repo_path) / file
            if filepath.exists():
                files_content[file] = read_file_content(filepath)
    
    if not files_content:
        print("No hay archivos relevantes para analizar")
        return None
    
    # Preparar prompt para Claude
    prompt = f"""Eres un experto en documentación técnica. Analiza estos cambios recientes en el repositorio {repo_name} y genera/actualiza la documentación correspondiente.

**IMPORTANTE: TODO el contenido debe estar en español de España (castellano). Usa terminología técnica en español cuando exista traducción estándar.**

## Archivos Modificados:

{json.dumps(list(files_content.keys()), indent=2)}

## Contenido de Archivos:

"""
    
    for file, content in files_content.items():
        # Limitar contenido por archivo para no exceder tokens
        content_preview = content[:2000] if len(content) > 2000 else content
        prompt += f"\n### {file}\n```\n{content_preview}\n```\n"
    
    prompt += """

## Tareas:

1. Identifica qué tipo de cambios se hicieron (nueva feature, bug fix, refactor, etc.)
2. Determina qué sección de documentación necesita actualizarse o crearse
3. Genera un resumen de lo que se debe documentar

## Formato de Respuesta:

Responde SOLO con un objeto JSON válido (sin markdown, sin bloques de código). Usa esta estructura EXACTA:

Para cambios que requieren documentación:
{"action": "create", "section": "api-authentication", "filename": "docs/api/auth-register.mdx", "title": "Endpoint de Registro EN ESPAÑOL", "description": "Descripción del cambio EN ESPAÑOL", "summary": "Resumen breve EN ESPAÑOL"}

Para cambios sin documentación:
{"action": "none"}

IMPORTANTE: 
- **TODO el texto debe estar en español de España**
- NO incluyas saltos de línea en los valores
- NO uses bloques ```json```
- Responde SOLO el JSON, nada más
"""
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        print(f"📝 Respuesta de Claude (primeros 500 chars):")
        print(response_text[:500])
        
        # Extraer JSON de la respuesta de múltiples formas
        json_text = response_text
        
        # Intento 1: Buscar entre ```json y ```
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            if json_end != -1:
                json_text = response_text[json_start:json_end].strip()
        
        # Intento 2: Buscar entre { y } más externo
        elif '{' in response_text and '}' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_text = response_text[start:end]
        
        # Intento 3: Limpiar caracteres problemáticos
        json_text = json_text.strip()
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as je:
            print(f"❌ Error parseando JSON: {je}")
            print(f"📄 JSON intentado: {json_text[:200]}...")
            return None
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error llamando a Claude: {e}")
        
        if "not_found_error" in error_msg and "model:" in error_msg:
            print("\n⚠️  El modelo de Claude especificado no está disponible.")
            print("Verifica tu API key en: https://console.anthropic.com/settings/keys")
            print("Verifica modelos disponibles en: https://console.anthropic.com/settings/plans")
            print("Modelos comunes: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307")
        
        return None

def apply_documentation_changes(doc_result, docs_base_path):
    """Aplica los cambios de documentación sugeridos por Claude"""
    if not doc_result or doc_result.get('action') == 'none':
        print("No hay cambios de documentación para aplicar")
        return False
    
    filename = doc_result.get('filename')
    title = doc_result.get('title', 'Documentation')
    description = doc_result.get('description', '')
    summary = doc_result.get('summary', '')
    
    if not filename:
        print("Respuesta inválida de Claude - falta filename")
        return False
    
    # Generar contenido MDX basado en los metadatos
    content = f"""---
title: "{title}"
description: "{description}"
---

# {title}

## Descripción

{description}

## Cambios Realizados

{summary}

---

*Documentación generada automáticamente por Claude AI*
*Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    filepath = Path(docs_base_path) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Documentación {'actualizada' if doc_result['action'] == 'update' else 'creada'}: {filename}")
        print(f"📝 Resumen: {summary}")
        return True
        
    except Exception as e:
        print(f"Error escribiendo documentación: {e}")
        return False

def main():
    """Función principal"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY no configurada")
        sys.exit(1)
    
    # Obtener argumentos
    if len(sys.argv) < 3:
        print("Uso: python claude-doc-generator.py <repo_name> <repo_path>")
        sys.exit(1)
    
    repo_name = sys.argv[1]
    repo_path = sys.argv[2]
    docs_base_path = os.getcwd()  # Asume que se ejecuta desde el repo docs
    
    print(f"🤖 Analizando cambios en {repo_name}...")
    
    # Inicializar cliente de Anthropic
    client = anthropic.Anthropic(api_key=api_key)
    
    # Obtener archivos cambiados
    changed_files = get_changed_files(repo_path)
    
    if not changed_files or changed_files == ['']:
        print("No hay archivos cambiados para analizar")
        sys.exit(0)
    
    print(f"📄 Archivos cambiados: {len(changed_files)}")
    
    # Analizar con Claude
    doc_result = analyze_changes_with_claude(client, repo_name, changed_files, repo_path)
    
    # Aplicar cambios
    if apply_documentation_changes(doc_result, docs_base_path):
        print("✅ Documentación actualizada exitosamente")
        sys.exit(0)
    else:
        print("ℹ️  No se realizaron cambios en la documentación")
        sys.exit(0)

if __name__ == '__main__':
    main()
