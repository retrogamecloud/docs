#!/usr/bin/env python3
"""
AST Code Analyzer
Analiza código fuente con AST para detectar APIs no documentadas
"""
import os
import sys
import ast
import json
from pathlib import Path
from typing import List, Dict, Set, Optional


class PythonAPIAnalyzer(ast.NodeVisitor):
    """Analiza código Python con AST"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.apis: List[Dict] = []
        self.current_class: Optional[str] = None
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visita definiciones de funciones"""
        # Ignorar funciones privadas (_func)
        if node.name.startswith('_') and not node.name.startswith('__'):
            self.generic_visit(node)
            return
        
        # Extraer docstring
        docstring = ast.get_docstring(node)
        
        # Extraer decoradores
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        # Detectar si es endpoint (Flask/FastAPI)
        is_endpoint = any(dec in ['route', 'get', 'post', 'put', 'delete', 'patch'] 
                         for dec in decorators)
        
        # Extraer parámetros
        params = []
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls':
                params.append(arg.arg)
        
        # Determinar contexto
        context = self.current_class if self.current_class else 'module'
        
        api_info = {
            'type': 'endpoint' if is_endpoint else 'function',
            'name': node.name,
            'context': context,
            'file': str(self.filepath),
            'line': node.lineno,
            'decorators': decorators,
            'parameters': params,
            'has_docstring': docstring is not None,
            'docstring': docstring[:200] if docstring else None,
            'is_public': not node.name.startswith('_')
        }
        
        self.apis.append(api_info)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visita funciones async"""
        # Ignorar funciones privadas
        if node.name.startswith('_') and not node.name.startswith('__'):
            self.generic_visit(node)
            return
        
        # Extraer docstring
        docstring = ast.get_docstring(node)
        
        # Extraer decoradores
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        # Detectar si es endpoint
        is_endpoint = any(dec in ['route', 'get', 'post', 'put', 'delete', 'patch'] 
                         for dec in decorators)
        
        # Extraer parámetros
        params = []
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls':
                params.append(arg.arg)
        
        # Determinar contexto
        context = self.current_class if self.current_class else 'module'
        
        api_info = {
            'type': 'endpoint' if is_endpoint else 'function',
            'name': node.name,
            'context': context,
            'file': str(self.filepath),
            'line': node.lineno,
            'decorators': decorators,
            'parameters': params,
            'has_docstring': docstring is not None,
            'docstring': docstring[:200] if docstring else None,
            'is_public': not node.name.startswith('_')
        }
        
        self.apis.append(api_info)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visita definiciones de clases"""
        # Guardar clase actual para contexto
        old_class = self.current_class
        self.current_class = node.name
        
        # Extraer docstring de clase
        docstring = ast.get_docstring(node)
        
        class_info = {
            'type': 'class',
            'name': node.name,
            'file': str(self.filepath),
            'line': node.lineno,
            'has_docstring': docstring is not None,
            'docstring': docstring[:200] if docstring else None,
            'is_public': not node.name.startswith('_')
        }
        
        self.apis.append(class_info)
        
        # Visitar métodos de la clase
        self.generic_visit(node)
        
        # Restaurar clase anterior
        self.current_class = old_class
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extrae nombre de un decorador"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return 'unknown'


class JavaScriptAPIAnalyzer:
    """Analiza código JavaScript/TypeScript (simple regex-based)"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.apis: List[Dict] = []
    
    def analyze(self, content: str):
        """Analiza contenido JS/TS"""
        import re
        
        # Detectar exports
        # export function name(...) o export const name = (...) =>
        function_pattern = r'export\s+(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
        arrow_pattern = r'export\s+const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>'
        
        # Funciones normales
        for match in re.finditer(function_pattern, content):
            name = match.group(1)
            params = match.group(2)
            
            # Buscar JSDoc antes de la función
            jsdoc = self._extract_jsdoc(content, match.start())
            
            self.apis.append({
                'type': 'function',
                'name': name,
                'file': str(self.filepath),
                'parameters': [p.strip() for p in params.split(',') if p.strip()],
                'has_docstring': jsdoc is not None,
                'docstring': jsdoc,
                'is_public': True
            })
        
        # Arrow functions exportadas
        for match in re.finditer(arrow_pattern, content):
            name = match.group(1)
            jsdoc = self._extract_jsdoc(content, match.start())
            
            self.apis.append({
                'type': 'function',
                'name': name,
                'file': str(self.filepath),
                'has_docstring': jsdoc is not None,
                'docstring': jsdoc,
                'is_public': True
            })
        
        # Detectar endpoints Express/Fastify
        endpoint_pattern = r'(?:app|router)\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]'
        for match in re.finditer(endpoint_pattern, content):
            method = match.group(1).upper()
            route = match.group(2)
            
            self.apis.append({
                'type': 'endpoint',
                'name': f"{method} {route}",
                'file': str(self.filepath),
                'is_public': True
            })
        
        return self.apis
    
    def _extract_jsdoc(self, content: str, pos: int) -> Optional[str]:
        """Extrae JSDoc antes de una posición"""
        import re
        
        # Buscar hacia atrás hasta encontrar /**
        before = content[:pos]
        match = re.search(r'/\*\*(.*?)\*/', before[::-1], re.DOTALL)
        
        if match:
            jsdoc = match.group(1)[::-1]
            return jsdoc.strip()[:200]
        
        return None


class CodeAnalyzer:
    def __init__(self, repos_path: str):
        self.repos_path = Path(repos_path)
        self.all_apis: List[Dict] = []
        
    def analyze_python_file(self, filepath: Path) -> List[Dict]:
        """Analiza un archivo Python"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(filepath))
            analyzer = PythonAPIAnalyzer(filepath)
            analyzer.visit(tree)
            
            return analyzer.apis
        except SyntaxError as e:
            print(f"⚠️  Syntax error en {filepath}: {e}")
            return []
        except Exception as e:
            print(f"⚠️  Error analizando {filepath}: {e}")
            return []
    
    def analyze_javascript_file(self, filepath: Path) -> List[Dict]:
        """Analiza un archivo JavaScript/TypeScript"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analyzer = JavaScriptAPIAnalyzer(filepath)
            return analyzer.analyze(content)
        except Exception as e:
            print(f"⚠️  Error analizando {filepath}: {e}")
            return []
    
    def scan_repositories(self) -> List[Dict]:
        """Escanea todos los repositorios"""
        print("📂 Escaneando repositorios...")
        
        # Buscar archivos Python
        py_files = list(self.repos_path.rglob('*.py'))
        py_files = [f for f in py_files if not any(
            part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', 'env']
            for part in f.parts
        )]
        
        print(f"   Python: {len(py_files)} archivos")
        
        for pyfile in py_files:
            apis = self.analyze_python_file(pyfile)
            self.all_apis.extend(apis)
        
        # Buscar archivos JS/TS
        js_files = list(self.repos_path.rglob('*.js')) + list(self.repos_path.rglob('*.ts'))
        js_files = [f for f in js_files if not any(
            part.startswith('.') or part in ['node_modules', 'dist', 'build']
            for part in f.parts
        )]
        
        print(f"   JavaScript/TypeScript: {len(js_files)} archivos")
        
        for jsfile in js_files:
            apis = self.analyze_javascript_file(jsfile)
            self.all_apis.extend(apis)
        
        return self.all_apis
    
    def find_undocumented(self) -> List[Dict]:
        """Encuentra APIs públicas sin documentación"""
        undocumented = []
        
        for api in self.all_apis:
            if api.get('is_public') and not api.get('has_docstring'):
                undocumented.append(api)
        
        return undocumented
    
    def generate_report(self, undocumented: List[Dict]) -> str:
        """Genera reporte de APIs sin documentar"""
        report = f"# 📝 APIs Sin Documentar\n\n"
        report += f"**Total de APIs públicas sin docstring**: {len(undocumented)}\n\n"
        
        # Agrupar por tipo
        by_type = {}
        for api in undocumented:
            api_type = api['type']
            if api_type not in by_type:
                by_type[api_type] = []
            by_type[api_type].append(api)
        
        for api_type, items in by_type.items():
            report += f"\n## {api_type.capitalize()}s ({len(items)})\n\n"
            
            for item in items:
                report += f"### `{item['name']}`\n\n"
                report += f"- **Archivo**: `{item['file']}`\n"
                if 'line' in item:
                    report += f"- **Línea**: {item['line']}\n"
                if 'parameters' in item:
                    report += f"- **Parámetros**: {', '.join(item['parameters'])}\n"
                report += "\n"
        
        # Estadísticas
        total_apis = len(self.all_apis)
        documented = total_apis - len(undocumented)
        coverage = 100 * documented / max(total_apis, 1)
        
        report += f"\n## 📊 Cobertura de Documentación\n\n"
        report += f"- APIs públicas totales: {total_apis}\n"
        report += f"- APIs documentadas: {documented}\n"
        report += f"- APIs sin documentar: {len(undocumented)}\n"
        report += f"- **Cobertura**: {coverage:.1f}%\n"
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analizador de código con AST')
    parser.add_argument('--repos-path', required=True, help='Path a repositorios clonados')
    parser.add_argument('--output', default='undocumented-apis.json', help='Archivo de output')
    parser.add_argument('--report', default='UNDOCUMENTED_APIS_REPORT.md', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    print("🚀 Iniciando análisis de código con AST...")
    
    analyzer = CodeAnalyzer(args.repos_path)
    all_apis = analyzer.scan_repositories()
    
    print(f"\n✅ Encontradas {len(all_apis)} APIs públicas")
    
    # Encontrar APIs sin documentar
    undocumented = analyzer.find_undocumented()
    
    if undocumented:
        print(f"⚠️  {len(undocumented)} APIs sin docstring/JSDoc")
        
        # Guardar JSON
        output_path = Path(args.repos_path).parent / 'docs' / args.output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(undocumented, f, indent=2)
        
        # Guardar reporte
        report = analyzer.generate_report(undocumented)
        report_path = Path(args.repos_path).parent / 'docs' / args.report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Resultados guardados: {args.output}")
        print(f"📄 Reporte generado: {args.report}")
    else:
        print("✅ Todas las APIs públicas están documentadas")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
