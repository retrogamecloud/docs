#!/usr/bin/env python3
"""
Link Validator
Verifica links internos, externos, imágenes y assets en documentación
"""
import os
import sys
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class LinkValidator:
    def __init__(self, docs_path: str, rate_limit: float = 0.5):
        self.docs_path = Path(docs_path)
        self.rate_limit = rate_limit  # Segundos entre requests externos
        self.broken_links: List[Dict] = []
        self.checked_external: Dict[str, bool] = {}  # Cache de URLs externas
        
    def extract_links_from_file(self, filepath: Path) -> Dict[str, List[str]]:
        """Extrae todos los links de un archivo MDX/MD"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'internal': [], 'external': [], 'images': [], 'assets': []}
        
        links = {
            'internal': [],
            'external': [],
            'images': [],
            'assets': []
        }
        
        # Markdown links: [text](url)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        for text, url in markdown_links:
            if url.startswith(('http://', 'https://')):
                links['external'].append(url)
            elif url.startswith('#'):
                # Anchor en misma página
                links['internal'].append((str(filepath), url))
            elif url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                links['images'].append(url)
            else:
                links['internal'].append(url)
        
        # HTML img tags: <img src="..." />
        img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        links['images'].extend(img_tags)
        
        # Links en HTML: <a href="...">
        html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', content)
        for url in html_links:
            if url.startswith(('http://', 'https://')):
                links['external'].append(url)
            else:
                links['internal'].append(url)
        
        # Assets (CSS, JS, etc)
        css_links = re.findall(r'<link[^>]+href=["\']([^"\']+\.css)["\']', content)
        js_links = re.findall(r'<script[^>]+src=["\']([^"\']+\.js)["\']', content)
        links['assets'].extend(css_links + js_links)
        
        return links
    
    def validate_internal_link(self, source_file: Path, link: str) -> Tuple[bool, str]:
        """Valida un link interno"""
        # Remover anchor (#section)
        link_without_anchor = link.split('#')[0]
        
        if not link_without_anchor:
            # Solo anchor en misma página - siempre válido por ahora
            return True, ""
        
        # Resolver path relativo
        if link_without_anchor.startswith('/'):
            # Link absoluto desde raíz
            target = self.docs_path / link_without_anchor.lstrip('/')
        else:
            # Link relativo desde archivo actual
            target = (source_file.parent / link_without_anchor).resolve()
        
        # Probar con y sin extensión
        possible_paths = [
            target,
            target.with_suffix('.mdx'),
            target.with_suffix('.md'),
            target / 'index.mdx',
            target / 'index.md'
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                return True, ""
        
        return False, f"Archivo no encontrado: {link}"
    
    def validate_external_link(self, url: str) -> Tuple[bool, str]:
        """Valida un link externo"""
        # Revisar cache
        if url in self.checked_external:
            return self.checked_external[url], ""
        
        # Rate limiting
        time.sleep(self.rate_limit)
        
        try:
            # HEAD request primero (más rápido)
            response = requests.head(
                url,
                timeout=10,
                allow_redirects=True,
                headers={'User-Agent': 'RetroGameCloud-DocsBot/1.0'}
            )
            
            # Si HEAD falla, intentar GET
            if response.status_code >= 400:
                response = requests.get(
                    url,
                    timeout=10,
                    allow_redirects=True,
                    headers={'User-Agent': 'RetroGameCloud-DocsBot/1.0'}
                )
            
            is_valid = response.status_code < 400
            self.checked_external[url] = is_valid
            
            return is_valid, "" if is_valid else f"HTTP {response.status_code}"
        
        except requests.exceptions.Timeout:
            self.checked_external[url] = False
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            self.checked_external[url] = False
            return False, "Connection error"
        except Exception as e:
            self.checked_external[url] = False
            return False, str(e)
    
    def validate_image(self, source_file: Path, image_path: str) -> Tuple[bool, str]:
        """Valida una imagen"""
        # Si es URL externa, validar como link externo
        if image_path.startswith(('http://', 'https://')):
            return self.validate_external_link(image_path)
        
        # Resolver path relativo
        if image_path.startswith('/'):
            target = self.docs_path / image_path.lstrip('/')
        else:
            target = (source_file.parent / image_path).resolve()
        
        if target.exists() and target.is_file():
            return True, ""
        
        return False, f"Imagen no encontrada: {image_path}"
    
    def validate_file(self, filepath: Path) -> List[Dict]:
        """Valida todos los links de un archivo"""
        broken = []
        rel_path = filepath.relative_to(self.docs_path)
        
        print(f"   🔍 {rel_path}")
        
        links = self.extract_links_from_file(filepath)
        
        # Validar links internos
        for link in links['internal']:
            if isinstance(link, tuple):
                # Link con anchor en misma página
                source, anchor = link
                # Por ahora, asumir válido (requeriría parsear contenido)
                continue
            
            is_valid, error = self.validate_internal_link(filepath, link)
            if not is_valid:
                broken.append({
                    'file': str(rel_path),
                    'type': 'internal_link',
                    'link': link,
                    'error': error
                })
        
        # Validar imágenes
        for image in links['images']:
            is_valid, error = self.validate_image(filepath, image)
            if not is_valid:
                broken.append({
                    'file': str(rel_path),
                    'type': 'image',
                    'link': image,
                    'error': error
                })
        
        # Validar links externos (con rate limiting)
        for url in set(links['external']):  # Deduplicar
            is_valid, error = self.validate_external_link(url)
            if not is_valid:
                broken.append({
                    'file': str(rel_path),
                    'type': 'external_link',
                    'link': url,
                    'error': error
                })
        
        return broken
    
    def run(self) -> List[Dict]:
        """Ejecuta validación en todos los archivos"""
        print("🔗 Buscando archivos MDX/MD...")
        files = list(self.docs_path.rglob('*.mdx')) + list(self.docs_path.rglob('*.md'))
        files = [f for f in files if not any(
            part.startswith('.') or part.upper() in ['CHANGELOG.MD', 'IMPROVEMENTS.MD']
            for part in f.parts
        )]
        
        print(f"   Encontrados: {len(files)} archivos")
        print(f"\n🔍 Validando links...")
        
        all_broken = []
        
        for filepath in files:
            broken = self.validate_file(filepath)
            all_broken.extend(broken)
        
        return all_broken
    
    def generate_report(self, broken_links: List[Dict]) -> str:
        """Genera reporte de links rotos"""
        if not broken_links:
            return "✅ No se encontraron links rotos"
        
        report = f"# 🔗 Reporte de Links Rotos\n\n"
        report += f"**Total de links rotos**: {len(broken_links)}\n\n"
        
        # Agrupar por tipo
        by_type = {}
        for link in broken_links:
            link_type = link['type']
            if link_type not in by_type:
                by_type[link_type] = []
            by_type[link_type].append(link)
        
        type_labels = {
            'internal_link': '📄 Links Internos Rotos',
            'external_link': '🌐 Links Externos Rotos',
            'image': '🖼️ Imágenes Rotas',
            'asset': '📦 Assets Rotos'
        }
        
        for link_type, items in by_type.items():
            label = type_labels.get(link_type, link_type)
            report += f"\n## {label} ({len(items)})\n\n"
            
            for item in items:
                report += f"### `{item['file']}`\n\n"
                report += f"- **Link**: `{item['link']}`\n"
                report += f"- **Error**: {item['error']}\n\n"
        
        # Resumen de links externos cacheados
        external_checked = len(self.checked_external)
        external_valid = sum(1 for v in self.checked_external.values() if v)
        
        report += f"\n## 📊 Estadísticas\n\n"
        report += f"- Links externos verificados: {external_checked}\n"
        report += f"- Links externos válidos: {external_valid}\n"
        report += f"- Links externos rotos: {external_checked - external_valid}\n"
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validador de links en documentación')
    parser.add_argument('--docs-path', required=True, help='Path al directorio de docs')
    parser.add_argument('--rate-limit', type=float, default=0.5, help='Segundos entre requests externos')
    parser.add_argument('--output', default='broken-links.json', help='Archivo de output JSON')
    parser.add_argument('--report', default='BROKEN_LINKS_REPORT.md', help='Archivo de reporte MD')
    
    args = parser.parse_args()
    
    print("🚀 Iniciando validación de links...")
    
    validator = LinkValidator(args.docs_path, args.rate_limit)
    broken_links = validator.run()
    
    if broken_links:
        print(f"\n⚠️  Se encontraron {len(broken_links)} links rotos")
        
        # Guardar JSON
        output_path = Path(args.docs_path) / args.output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(broken_links, f, indent=2)
        print(f"📄 Resultados guardados: {args.output}")
        
        # Guardar reporte
        report = validator.generate_report(broken_links)
        report_path = Path(args.docs_path) / args.report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Reporte generado: {args.report}")
        
        return 1  # Exit code 1 si hay links rotos
    else:
        print("\n✅ No se encontraron links rotos")
        return 0


if __name__ == '__main__':
    sys.exit(main())
