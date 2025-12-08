#!/usr/bin/env python3
"""
Auto-fix Quick Wins
Aplica automáticamente correcciones simples sin necesidad de review
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import yaml


class QuickFixApplier:
    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.fixes_applied: List[Dict] = []
        
    def scan_mdx_files(self) -> List[Path]:
        """Encuentra todos los archivos .mdx y .md"""
        files = []
        for ext in ['*.mdx', '*.md']:
            files.extend(self.docs_path.rglob(ext))
        
        # Filtrar archivos ocultos y changelog/improvements
        files = [f for f in files if not any(
            part.startswith('.') or part.upper() in ['CHANGELOG.MD', 'IMPROVEMENTS.MD', 'STRUCTURE_CHANGELOG.MD']
            for part in f.parts
        )]
        
        return files
    
    def parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extrae frontmatter y contenido"""
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not match:
            return {}, content
        
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2)
            return frontmatter or {}, body
        except yaml.YAMLError:
            return {}, content
    
    def fix_missing_icon(self, frontmatter: Dict, filepath: Path) -> bool:
        """Añade icono si falta"""
        if 'icon' in frontmatter:
            return False
        
        # Mapeo de rutas a iconos apropiados
        icon_mapping = {
            'api-reference': 'code',
            'api': 'plug',
            'auth': 'lock',
            'infrastructure': 'server',
            'cicd': 'arrows-spin',
            'deployment': 'rocket',
            'services': 'microchip',
            'frontend': 'palette',
            'quickstart': 'bolt',
            'troubleshooting': 'wrench',
        }
        
        # Detectar icono apropiado basado en ruta
        path_str = str(filepath).lower()
        icon = 'file-lines'  # Default
        
        for key, value in icon_mapping.items():
            if key in path_str:
                icon = value
                break
        
        frontmatter['icon'] = icon
        return True
    
    def fix_missing_description(self, frontmatter: Dict) -> bool:
        """Añade description si falta (basada en título)"""
        if 'description' in frontmatter and frontmatter['description']:
            return False
        
        if 'title' not in frontmatter:
            return False
        
        title = frontmatter['title']
        # Generar descripción simple
        frontmatter['description'] = f"Documentación sobre {title}"
        return True
    
    def standardize_title_format(self, frontmatter: Dict) -> bool:
        """Estandariza formato de títulos"""
        if 'title' not in frontmatter:
            return False
        
        title = frontmatter['title']
        changed = False
        
        # Eliminar espacios extra
        new_title = re.sub(r'\s+', ' ', title).strip()
        
        # Capitalizar apropiadamente (excepto palabras técnicas)
        # No tocar si tiene numeración (X.Y. Título)
        if not re.match(r'^\d+\.\d+\.', new_title):
            # Lista de palabras que no capitalizar
            lowercase_words = {'de', 'y', 'o', 'en', 'con', 'para', 'por', 'a', 'el', 'la', 'los', 'las'}
            words = new_title.split()
            
            # Capitalizar primera palabra siempre
            if words:
                words[0] = words[0].capitalize()
                
                # Resto según reglas
                for i in range(1, len(words)):
                    if words[i].lower() not in lowercase_words and not words[i].isupper():
                        # Si no es acrónimo y no es palabra corta, capitalizar
                        if len(words[i]) > 3:
                            words[i] = words[i].capitalize()
                
                capitalized = ' '.join(words)
                if capitalized != title:
                    new_title = capitalized
                    changed = True
        
        if new_title != title:
            frontmatter['title'] = new_title
            return True
        
        return changed
    
    def fix_code_block_formatting(self, body: str) -> Tuple[str, bool]:
        """Estandariza formato de bloques de código"""
        changed = False
        original = body
        
        # Asegurar línea en blanco antes de bloques de código
        body = re.sub(r'([^\n])\n```', r'\1\n\n```', body)
        
        # Asegurar línea en blanco después de bloques de código
        body = re.sub(r'```\n([^\n])', r'```\n\n\1', body)
        
        # Estandarizar language tags (bash, yaml, python, etc)
        body = re.sub(r'```shell\n', '```bash\n', body)
        body = re.sub(r'```yml\n', '```yaml\n', body)
        body = re.sub(r'```js\n', '```javascript\n', body)
        body = re.sub(r'```ts\n', '```typescript\n', body)
        
        changed = (body != original)
        return body, changed
    
    def fix_heading_spacing(self, body: str) -> Tuple[str, bool]:
        """Estandariza espaciado alrededor de encabezados"""
        changed = False
        original = body
        
        # Asegurar línea en blanco antes de encabezados (excepto al inicio)
        body = re.sub(r'([^\n])\n(#{1,6} )', r'\1\n\n\2', body)
        
        # Eliminar espacios múltiples después de #
        body = re.sub(r'^(#{1,6})\s+', r'\1 ', body, flags=re.MULTILINE)
        
        changed = (body != original)
        return body, changed
    
    def fix_list_formatting(self, body: str) -> Tuple[str, bool]:
        """Estandariza formato de listas"""
        changed = False
        original = body
        
        # Asegurar espacio después de - o * en listas
        body = re.sub(r'^([\-\*])\s*([^\s])', r'\1 \2', body, flags=re.MULTILINE)
        
        # Asegurar línea en blanco antes de listas (si no está indentada)
        body = re.sub(r'([^\n])\n([\-\*] )', r'\1\n\n\2', body)
        
        changed = (body != original)
        return body, changed
    
    def fix_trailing_whitespace(self, content: str) -> Tuple[str, bool]:
        """Elimina espacios en blanco al final de líneas"""
        lines = content.split('\n')
        new_lines = [line.rstrip() for line in lines]
        changed = any(old != new for old, new in zip(lines, new_lines))
        return '\n'.join(new_lines), changed
    
    def apply_fixes_to_file(self, filepath: Path) -> Dict:
        """Aplica todas las correcciones a un archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'file': str(filepath.relative_to(self.docs_path)),
                'error': str(e),
                'fixes': []
            }
        
        original_content = content
        fixes = []
        
        # Parsear frontmatter
        frontmatter, body = self.parse_frontmatter(content)
        frontmatter_changed = False
        
        # Aplicar fixes al frontmatter
        if self.fix_missing_icon(frontmatter, filepath):
            fixes.append('icon_added')
            frontmatter_changed = True
        
        if self.fix_missing_description(frontmatter):
            fixes.append('description_added')
            frontmatter_changed = True
        
        if self.standardize_title_format(frontmatter):
            fixes.append('title_standardized')
            frontmatter_changed = True
        
        # Aplicar fixes al body
        body, changed = self.fix_code_block_formatting(body)
        if changed:
            fixes.append('code_blocks_formatted')
        
        body, changed = self.fix_heading_spacing(body)
        if changed:
            fixes.append('heading_spacing_fixed')
        
        body, changed = self.fix_list_formatting(body)
        if changed:
            fixes.append('lists_formatted')
        
        # Reconstruir contenido
        if frontmatter_changed or fixes:
            if frontmatter:
                # Serializar frontmatter
                frontmatter_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
                new_content = f"---\n{frontmatter_yaml}---\n{body}"
            else:
                new_content = body
            
            # Fix trailing whitespace
            new_content, changed = self.fix_trailing_whitespace(new_content)
            if changed:
                fixes.append('trailing_whitespace_removed')
            
            # Escribir si cambió
            if new_content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return {
                    'file': str(filepath.relative_to(self.docs_path)),
                    'fixes': fixes,
                    'success': True
                }
        
        return {}
    
    def run(self) -> List[Dict]:
        """Ejecuta todas las correcciones"""
        print("🔧 Buscando archivos MDX/MD...")
        files = self.scan_mdx_files()
        print(f"   Encontrados: {len(files)} archivos")
        
        print("\n⚡ Aplicando quick fixes...")
        results = []
        
        for filepath in files:
            result = self.apply_fixes_to_file(filepath)
            if result:
                results.append(result)
                rel_path = result['file']
                fixes_str = ', '.join(result['fixes'])
                print(f"   ✅ {rel_path}: {fixes_str}")
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Genera reporte de correcciones aplicadas"""
        if not results:
            return "No se aplicaron correcciones automáticas."
        
        report = f"# 🔧 Auto-fix Quick Wins Report\n\n"
        report += f"**Total de archivos modificados**: {len(results)}\n\n"
        
        # Contar tipos de fixes
        fix_counts = {}
        for result in results:
            for fix in result.get('fixes', []):
                fix_counts[fix] = fix_counts.get(fix, 0) + 1
        
        report += "## Correcciones Aplicadas\n\n"
        fix_labels = {
            'icon_added': 'Iconos añadidos en frontmatter',
            'description_added': 'Descripciones generadas',
            'title_standardized': 'Títulos estandarizados',
            'code_blocks_formatted': 'Bloques de código formateados',
            'heading_spacing_fixed': 'Espaciado de encabezados corregido',
            'lists_formatted': 'Listas formateadas',
            'trailing_whitespace_removed': 'Espacios en blanco eliminados'
        }
        
        for fix_type, count in sorted(fix_counts.items(), key=lambda x: -x[1]):
            label = fix_labels.get(fix_type, fix_type)
            report += f"- **{label}**: {count} archivos\n"
        
        report += f"\n## Archivos Modificados\n\n"
        for result in results:
            report += f"- `{result['file']}`: {', '.join(result['fixes'])}\n"
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-fix quick wins en documentación')
    parser.add_argument('--docs-path', required=True, help='Path al directorio de docs')
    parser.add_argument('--report-output', default='AUTO_FIXES_REPORT.md', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    print("🚀 Iniciando Auto-fix Quick Wins...")
    
    fixer = QuickFixApplier(args.docs_path)
    results = fixer.run()
    
    if results:
        print(f"\n✅ Correcciones aplicadas a {len(results)} archivos")
        
        # Generar reporte
        report = fixer.generate_report(results)
        report_path = Path(args.docs_path) / args.report_output
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Reporte generado: {args.report_output}")
    else:
        print("\n✨ No se necesitaron correcciones")
    
    return 0 if results else 0  # Siempre éxito


if __name__ == '__main__':
    sys.exit(main())
