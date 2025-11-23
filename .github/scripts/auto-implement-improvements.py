#!/usr/bin/env python3
"""
Auto-implement Improvements
Implementa automáticamente las mejoras propuestas en IMPROVEMENTS.md
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import anthropic


class ImprovementImplementer:
    def __init__(self, docs_path: str, repos_path: str):
        self.docs_path = Path(docs_path)
        self.repos_path = Path(repos_path)
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.implemented: List[Dict] = []
        
    def load_improvements(self) -> Optional[Dict]:
        """Carga el archivo analysis-results.json"""
        analysis_file = self.docs_path / 'analysis-results.json'
        
        if not analysis_file.exists():
            print("⚠️  No se encontró analysis-results.json")
            return None
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando analysis: {e}")
            return None
    
    def filter_implementable_improvements(self, improvements: List[Dict]) -> List[Dict]:
        """Filtra mejoras que se pueden implementar automáticamente"""
        implementable = []
        
        for imp in improvements:
            category = imp.get('category', '')
            priority = imp.get('priority', '')
            
            # Solo implementar automáticamente:
            # - High priority
            # - Categorías: new_section, diagrams, content
            # - Con archivos específicos a crear
            
            if priority != 'high':
                continue
            
            if category not in ['new_section', 'diagrams', 'content']:
                continue
            
            files_to_create = imp.get('files_to_create', [])
            if not files_to_create:
                continue
            
            implementable.append(imp)
        
        return implementable
    
    def generate_file_content_with_claude(self, improvement: Dict, context: str) -> Optional[str]:
        """Usa Claude para generar contenido de archivo completo"""
        if not self.client:
            return None
        
        title = improvement.get('title', '')
        description = improvement.get('description', '')
        proposed_content = improvement.get('proposed_content', '')
        mermaid_diagram = improvement.get('mermaid_diagram', '')
        
        prompt = f"""Eres un experto en documentación técnica. Genera contenido COMPLETO en formato MDX para Mintlify.

## Mejora a Implementar

**Título**: {title}
**Descripción**: {description}

## Contenido Base Propuesto

{proposed_content}

## Diagrama (si aplica)

{mermaid_diagram if mermaid_diagram else 'N/A'}

## Contexto del Proyecto

{context}

## Requisitos

1. Genera un archivo MDX COMPLETO y funcional
2. Incluye frontmatter con title, description, icon apropiado
3. Usa componentes de Mintlify: <Note>, <Warning>, <Tabs>, <Card>, etc.
4. Incluye diagramas Mermaid si es apropiado
5. Estructura clara con encabezados jerárquicos
6. Ejemplos de código cuando sea relevante
7. TODO en español de España (castellano)

## Formato de Respuesta

Responde SOLO con el contenido MDX completo, sin explicaciones adicionales.
Comienza directamente con el frontmatter (---).
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text.strip()
            
            # Limpiar markdown code blocks si los añadió
            if content.startswith('```'):
                lines = content.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines[-1].startswith('```'):
                    lines = lines[:-1]
                content = '\n'.join(lines)
            
            return content
        
        except Exception as e:
            print(f"❌ Error generando contenido: {e}")
            return None
    
    def create_file(self, filepath: Path, content: str) -> bool:
        """Crea un archivo con contenido"""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Creado: {filepath.relative_to(self.docs_path)}")
            return True
        
        except Exception as e:
            print(f"   ❌ Error creando {filepath}: {e}")
            return False
    
    def generate_context_summary(self) -> str:
        """Genera resumen del contexto del proyecto"""
        context = """
# Proyecto: RetroGameCloud

Plataforma de juegos retro con:
- Microservicios: auth, user, game-catalog, score, ranking
- Frontend: React con JS-DOS emulator
- Infraestructura: AWS EKS, PostgreSQL, S3, CloudFront
- API Gateway: Kong con OAuth2
- CI/CD: GitHub Actions + ArgoCD GitOps
- Monitoreo: Prometheus + Grafana
"""
        return context
    
    def implement_improvement(self, improvement: Dict) -> bool:
        """Implementa una mejora específica"""
        title = improvement.get('title', 'Sin título')
        files_to_create = improvement.get('files_to_create', [])
        
        print(f"\n📝 Implementando: {title}")
        
        context = self.generate_context_summary()
        success_count = 0
        
        for file_path_str in files_to_create:
            # Convertir path relativo a absoluto
            file_path = self.docs_path / file_path_str
            
            # Si el archivo ya existe, skip
            if file_path.exists():
                print(f"   ⏭️  Ya existe: {file_path_str}")
                continue
            
            print(f"   🤖 Generando: {file_path_str}")
            
            # Generar contenido con Claude
            content = self.generate_file_content_with_claude(improvement, context)
            
            if not content:
                print(f"   ⚠️  No se pudo generar contenido")
                continue
            
            # Crear archivo
            if self.create_file(file_path, content):
                success_count += 1
                self.implemented.append({
                    'improvement': title,
                    'file': file_path_str,
                    'status': 'created'
                })
        
        return success_count > 0
    
    def run(self, max_improvements: int = 5) -> List[Dict]:
        """Ejecuta implementación de mejoras"""
        print("🚀 Iniciando implementación automática de mejoras...")
        
        # Cargar análisis
        analysis = self.load_improvements()
        if not analysis:
            return []
        
        improvements = analysis.get('improvements', [])
        print(f"📊 Total de mejoras propuestas: {len(improvements)}")
        
        # Filtrar implementables
        implementable = self.filter_implementable_improvements(improvements)
        print(f"⚡ Mejoras implementables automáticamente: {len(implementable)}")
        
        if not implementable:
            print("ℹ️  No hay mejoras de alta prioridad para implementar automáticamente")
            return []
        
        # Limitar cantidad
        to_implement = implementable[:max_improvements]
        print(f"🎯 Implementando top {len(to_implement)} mejoras...\n")
        
        # Implementar cada una
        for improvement in to_implement:
            try:
                self.implement_improvement(improvement)
            except Exception as e:
                print(f"❌ Error implementando mejora: {e}")
                continue
        
        return self.implemented
    
    def generate_report(self, implemented: List[Dict]) -> str:
        """Genera reporte de implementación"""
        if not implemented:
            return "No se implementaron mejoras automáticamente."
        
        report = f"# 🤖 Mejoras Implementadas Automáticamente\n\n"
        report += f"**Total de archivos creados**: {len(implemented)}\n\n"
        
        # Agrupar por mejora
        by_improvement = {}
        for item in implemented:
            imp_name = item['improvement']
            if imp_name not in by_improvement:
                by_improvement[imp_name] = []
            by_improvement[imp_name].append(item['file'])
        
        report += "## Archivos Creados\n\n"
        
        for improvement, files in by_improvement.items():
            report += f"### {improvement}\n\n"
            for file in files:
                report += f"- `{file}`\n"
            report += "\n"
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-implementar mejoras propuestas')
    parser.add_argument('--docs-path', required=True, help='Path a documentación')
    parser.add_argument('--repos-path', required=True, help='Path a repos clonados')
    parser.add_argument('--max-improvements', type=int, default=5, help='Máximo de mejoras a implementar')
    parser.add_argument('--report', default='AUTO_IMPLEMENTED_REPORT.md', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    # Verificar API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY no configurada")
        sys.exit(1)
    
    implementer = ImprovementImplementer(args.docs_path, args.repos_path)
    implemented = implementer.run(args.max_improvements)
    
    if implemented:
        print(f"\n✅ Implementadas {len(implemented)} mejoras")
        
        # Generar reporte
        report = implementer.generate_report(implemented)
        report_path = Path(args.docs_path) / args.report
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Reporte: {args.report}")
        
        # Listar archivos creados
        print("\n📁 Archivos creados:")
        for item in implemented:
            print(f"   - {item['file']}")
    else:
        print("\nℹ️  No se implementaron mejoras en esta ejecución")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
