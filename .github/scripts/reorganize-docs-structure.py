#!/usr/bin/env python3
"""
Documentation Structure Reorganizer with Claude AI
Analiza y reorganiza la estructura de docs.json de manera inteligente
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from json_repair import repair_json

def load_docs_json(docs_path):
    """Carga el archivo docs.json"""
    docs_file = Path(docs_path) / "docs.json"
    if not docs_file.exists():
        print(f"❌ No se encontró docs.json en {docs_path}")
        return None
    
    with open(docs_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_docs_json(docs_path, docs_data):
    """Guarda el archivo docs.json con formato bonito"""
    docs_file = Path(docs_path) / "docs.json"
    with open(docs_file, 'w', encoding='utf-8') as f:
        json.dump(docs_data, f, indent=2, ensure_ascii=False)
    print(f"✅ docs.json actualizado")

def analyze_structure_with_claude(client, current_structure):
    """Analiza la estructura actual y propone reorganización"""
    
    prompt = f"""Eres un experto en arquitectura de información y documentación técnica. Analiza la estructura actual de navegación de la documentación y propón una reorganización óptima.

**IMPORTANTE: TODO el contenido debe estar en español de España (castellano).**

## Estructura Actual de Navegación:

```json
{json.dumps(current_structure, indent=2, ensure_ascii=False)}
```

## Tareas:

1. **Analizar la organización actual**: ¿Tiene sentido la agrupación? ¿Hay redundancias?
2. **Proponer reorganización**: Grupos lógicos, orden jerárquico, numeración apropiada
3. **Recomendar nuevos grupos**: Si faltan secciones importantes
4. **Optimizar nombres**: Títulos claros y concisos en español de España

## Principios de Reorganización:

- **Orden lógico**: De lo general a lo específico (Introducción → Conceptos → Implementación → Referencia)
- **Agrupación semántica**: Relacionar conceptos similares
- **Jerarquía clara**: Máximo 3 niveles de profundidad
- **Nomenclatura consistente**: Usar números para orden jerárquico cuando sea apropiado
- **Numeración de grupos consecutiva**: Los NOMBRES de grupos deben numerarse 1, 2, 3, 4, 5... sin saltos
- **NO subnumerar nombres de grupos**: Los nombres de grupos son "1. Nombre", "2. Nombre" (NUNCA "7.1 Subgrupo" o "8.2 Otro")
- **Páginas sin numeración**: Los arrays de pages no llevan números en sus nombres, solo rutas de archivo
- **Eliminar redundancias**: Consolidar páginas duplicadas

## Formato de Respuesta:

Responde SOLO con JSON puro (sin markdown, sin bloques ```):

{{
  "proposed_structure": {{
    "tabs": [
      {{
        "tab": "Nombre del Tab EN ESPAÑOL",
        "groups": [
          {{
            "group": "1. Nombre del Grupo EN ESPAÑOL",
            "pages": ["page1", "page2"],
            "description": "Qué contiene este grupo"
          }}
        ]
      }}
    ]
  }},
  "changes_summary": "Resumen de cambios realizados EN ESPAÑOL",
  "rationale": "Por qué esta organización es mejor EN ESPAÑOL",
  "new_groups_needed": [
    {{
      "name": "Nombre del grupo EN ESPAÑOL",
      "reason": "Por qué se necesita",
      "suggested_pages": ["page1.mdx", "page2.mdx"]
    }}
  ],
  "pages_to_consolidate": [
    {{
      "pages": ["page1", "page2"],
      "reason": "Por qué consolidar",
      "new_page_name": "consolidated-page"
    }}
  ]
}}

RECUERDA:
- Los GRUPOS (group) se numeran: "1. Nombre", "2. Otro", "3. Más" (números consecutivos 1, 2, 3...)
- Los nombres de GRUPOS NO llevan subnumeración: NUNCA uses "7.1 Subgrupo" o "8.2 Otro" como nombre de grupo
- Las PÁGINAS (pages) NO se numeran en sus nombres, solo son rutas: ["page1", "page2", "page3"]
- Si hay 7 grupos, deben numerarse del 1 al 7. Si añades uno nuevo, será el 8
- TODO en español de España
- Responde SOLO JSON sin markdown
- Mantén los nombres de archivos (pages) tal cual están, solo reorganiza grupos y orden
"""

    try:
        import anthropic
        
        print("🤖 Analizando estructura con Claude Sonnet 4.5...")
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        print(f"✅ Respuesta recibida ({len(response_text)} chars)")
        
        # Limpiar markdown code blocks si existen
        json_text = response_text
        if "```json" in json_text:
            print("🔍 Detectado bloque de código markdown ```json, extrayendo...")
            json_start = json_text.find("```json") + 7
            json_end = json_text.find("```", json_start)
            if json_end == -1:
                json_end = len(json_text)
            json_text = json_text[json_start:json_end].strip()
        elif "```" in json_text:
            json_start = json_text.find("```") + 3
            json_end = json_text.find("```", json_start)
            if json_end == -1:
                json_end = len(json_text)
            json_text = json_text[json_start:json_end].strip()
        
        # Intentar parsear
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parseando JSON: {e}")
            # Intentar reparar el JSON
            try:
                print("🔧 Intentando reparar JSON...")
                repaired = repair_json(json_text)
                result = json.loads(repaired)
                print("✅ JSON reparado exitosamente")
                return result
            except Exception as repair_error:
                print(f"❌ No se pudo reparar: {repair_error}")
                return None
    
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return None

def apply_reorganization(docs_data, proposed_structure):
    """Aplica la reorganización propuesta al docs.json"""
    
    if not proposed_structure or 'proposed_structure' not in proposed_structure:
        print("❌ No hay estructura propuesta válida")
        return docs_data
    
    # Mantener todo excepto navigation
    new_docs = {k: v for k, v in docs_data.items() if k != 'navigation'}
    
    # Aplicar nueva estructura de navegación
    new_navigation = proposed_structure['proposed_structure']
    
    # Renumerar grupos automáticamente para asegurar consecutividad
    import re
    for tab in new_navigation.get('tabs', []):
        for group_idx, group in enumerate(tab.get('groups', []), start=1):
            group_name = group.get('group', '')
            # Eliminar numeración existente del GRUPO (ej: "7. ", "8. ", "10. ")
            # IMPORTANTE: Solo eliminar numeración de nivel 1 (X.), NO subnumeración de páginas (X.Y)
            clean_name = re.sub(r'^\d+\.\s+', '', group_name)
            # Aplicar numeración consecutiva correcta al grupo
            group['group'] = f"{group_idx}. {clean_name}"
            print(f"  📝 Grupo renumerado: '{group_name}' → '{group['group']}'")
            
            # Renumerar frontmatters de páginas dentro del grupo
            pages = group.get('pages', [])
            for page_idx, page_path in enumerate(pages, start=1):
                update_page_frontmatter(page_path, group_idx, page_idx)
    
    # Mantener global anchors si existen
    if 'navigation' in docs_data and 'global' in docs_data['navigation']:
        new_navigation['global'] = docs_data['navigation']['global']
    
    new_docs['navigation'] = new_navigation
    
    print("✅ Reorganización aplicada con numeración consecutiva de grupos")
    return new_docs

def update_page_frontmatter(page_path, group_number, page_number):
    """Actualiza el frontmatter de una página con numeración correcta"""
    import re
    from pathlib import Path
    
    # Construir ruta al archivo MDX
    docs_root = Path(__file__).parent.parent.parent
    mdx_file = docs_root / "docs" / f"{page_path}.mdx"
    
    if not mdx_file.exists():
        # Intentar en raíz si no está en docs/
        mdx_file = docs_root / f"{page_path}.mdx"
    
    if not mdx_file.exists():
        print(f"    ⚠️  Archivo no encontrado: {page_path}.mdx")
        return
    
    try:
        with open(mdx_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not frontmatter_match:
            print(f"    ⚠️  Sin frontmatter: {page_path}.mdx")
            return
        
        frontmatter = frontmatter_match.group(1)
        
        # Actualizar title con numeración correcta
        expected_number = f"{group_number}.{page_number}"
        
        # Buscar si ya tiene numeración en el título
        title_match = re.search(r'^title:\s*["\'](.+?)["\']', frontmatter, re.MULTILINE)
        if title_match:
            current_title = title_match.group(1)
            # Eliminar numeración existente (X.Y. al inicio)
            clean_title = re.sub(r'^\d+\.\d+\.\s*', '', current_title)
            new_title = f"{expected_number}. {clean_title}"
            
            # Reemplazar en frontmatter
            new_frontmatter = re.sub(
                r'^title:\s*["\'].+?["\']',
                f'title: "{new_title}"',
                frontmatter,
                flags=re.MULTILINE
            )
            
            # Asegurar que tiene icono
            if 'icon:' not in new_frontmatter:
                # Añadir icono genérico si no tiene
                new_frontmatter += '\nicon: "file-lines"'
                print(f"    ✨ Añadido icono a: {page_path}.mdx")
            
            # Reconstruir contenido
            new_content = f"---\n{new_frontmatter}\n---\n" + content[frontmatter_match.end():]
            
            # Solo escribir si cambió
            if new_content != content:
                with open(mdx_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"    ✅ Actualizado: {page_path}.mdx → {new_title}")
        
    except Exception as e:
        print(f"    ❌ Error actualizando {page_path}.mdx: {e}")

def generate_changelog(changes_summary, rationale):
    """Genera un changelog de los cambios estructurales"""
    
    changelog = f"""# 📋 Reorganización de Estructura de Documentación

**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Generado por**: Claude Sonnet 4.5

## 📊 Resumen de Cambios

{changes_summary}

## 🎯 Justificación

{rationale}

---

*Reorganización automática generada por el sistema inteligente de documentación*
"""
    
    return changelog

def main():
    parser = argparse.ArgumentParser(description='Reorganizar estructura de docs.json con Claude AI')
    parser.add_argument('--docs-path', required=True, help='Path al directorio de documentación')
    parser.add_argument('--output-changelog', default='STRUCTURE_CHANGELOG.md', help='Archivo de changelog')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin aplicar cambios')
    
    args = parser.parse_args()
    
    # Verificar API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY no configurada")
        sys.exit(1)
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        print("❌ Librería anthropic no instalada")
        sys.exit(1)
    
    print("📊 Cargando estructura actual...")
    docs_data = load_docs_json(args.docs_path)
    if not docs_data:
        sys.exit(1)
    
    current_structure = docs_data.get('navigation', {})
    
    print("🤖 Analizando y reorganizando estructura...")
    analysis_result = analyze_structure_with_claude(client, current_structure)
    
    if not analysis_result:
        print("❌ No se pudo obtener propuesta de reorganización")
        sys.exit(1)
    
    print(f"\n📋 Resumen: {analysis_result.get('changes_summary', 'N/A')}")
    
    if args.dry_run:
        print("\n🔍 Modo DRY RUN - No se aplicarán cambios")
        print("\n📄 Estructura propuesta:")
        print(json.dumps(analysis_result.get('proposed_structure'), indent=2, ensure_ascii=False))
    else:
        print("\n✏️  Aplicando reorganización...")
        new_docs_data = apply_reorganization(docs_data, analysis_result)
        save_docs_json(args.docs_path, new_docs_data)
        
        # Generar changelog
        changelog = generate_changelog(
            analysis_result.get('changes_summary', ''),
            analysis_result.get('rationale', '')
        )
        
        changelog_path = Path(args.docs_path) / args.output_changelog
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(changelog)
        print(f"✅ Changelog generado: {args.output_changelog}")
        
        # Mostrar nuevos grupos recomendados
        if 'new_groups_needed' in analysis_result and analysis_result['new_groups_needed']:
            print("\n💡 Nuevos grupos recomendados:")
            for group in analysis_result['new_groups_needed']:
                print(f"  - {group['name']}: {group['reason']}")
        
        # Mostrar páginas a consolidar
        if 'pages_to_consolidate' in analysis_result and analysis_result['pages_to_consolidate']:
            print("\n🔗 Páginas sugeridas para consolidar:")
            for consolidation in analysis_result['pages_to_consolidate']:
                print(f"  - {', '.join(consolidation['pages'])} → {consolidation['new_page_name']}")
                print(f"    Razón: {consolidation['reason']}")
    
    print("\n✅ Reorganización completada")

if __name__ == "__main__":
    main()
