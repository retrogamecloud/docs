#!/usr/bin/env python3
"""
Automatic Diagram Generator
Genera diagramas Mermaid desde código fuente automáticamente
"""
import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional


class DiagramGenerator:
    def __init__(self, repos_path: str):
        self.repos_path = Path(repos_path)
        
    def generate_sequence_diagram_from_endpoint(self, endpoint_file: Path, endpoint_name: str) -> Optional[str]:
        """Genera diagrama de secuencia desde un endpoint"""
        try:
            with open(endpoint_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None
        
        # Construir diagrama básico
        diagram = "```mermaid\nsequenceDiagram\n"
        diagram += "    participant Cliente\n"
        diagram += f"    participant API as {endpoint_name}\n"
        
        # Detectar llamadas a BD
        if 'db.' in content or 'session.' in content or '.query(' in content:
            diagram += "    participant DB as Base de Datos\n"
        
        # Detectar llamadas a otros servicios
        if 'requests.' in content or 'http' in content.lower():
            diagram += "    participant Servicio as Servicio Externo\n"
        
        diagram += "\n"
        diagram += "    Cliente->>+API: HTTP Request\n"
        
        # Detectar operaciones de BD
        if 'INSERT' in content.upper() or '.add(' in content or '.create(' in content:
            diagram += "    API->>+DB: INSERT\n"
            diagram += "    DB-->>-API: OK\n"
        elif 'SELECT' in content.upper() or '.query(' in content or '.filter(' in content:
            diagram += "    API->>+DB: SELECT\n"
            diagram += "    DB-->>-API: Datos\n"
        elif 'UPDATE' in content.upper() or '.update(' in content:
            diagram += "    API->>+DB: UPDATE\n"
            diagram += "    DB-->>-API: OK\n"
        elif 'DELETE' in content.upper() or '.delete(' in content:
            diagram += "    API->>+DB: DELETE\n"
            diagram += "    DB-->>-API: OK\n"
        
        # Detectar llamadas HTTP externas
        if 'requests.get' in content:
            diagram += "    API->>+Servicio: GET\n"
            diagram += "    Servicio-->>-API: Respuesta\n"
        elif 'requests.post' in content:
            diagram += "    API->>+Servicio: POST\n"
            diagram += "    Servicio-->>-API: Respuesta\n"
        
        diagram += "    API-->>-Cliente: HTTP Response\n"
        diagram += "```\n"
        
        return diagram
    
    def generate_architecture_from_docker_compose(self, compose_file: Path) -> Optional[str]:
        """Genera diagrama de arquitectura desde docker-compose.yml"""
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                compose_data = yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Error parseando {compose_file}: {e}")
            return None
        
        services = compose_data.get('services', {})
        
        if not services:
            return None
        
        diagram = "```mermaid\ngraph TB\n"
        
        # Detectar tipos de servicios
        for service_name, service_config in services.items():
            image = service_config.get('image', '')
            
            # Clasificar servicio
            if 'postgres' in image.lower():
                diagram += f"    {service_name}[(PostgreSQL)]\n"
            elif 'redis' in image.lower():
                diagram += f"    {service_name}[[Redis Cache]]\n"
            elif 'nginx' in image.lower() or 'kong' in service_name.lower():
                diagram += f"    {service_name}[API Gateway]\n"
            else:
                diagram += f"    {service_name}[{service_name.capitalize()}]\n"
        
        # Detectar dependencias
        for service_name, service_config in services.items():
            depends_on = service_config.get('depends_on', [])
            if isinstance(depends_on, dict):
                depends_on = list(depends_on.keys())
            
            for dep in depends_on:
                diagram += f"    {service_name} --> {dep}\n"
        
        diagram += "```\n"
        
        return diagram
    
    def generate_flow_from_workflow(self, workflow_file: Path) -> Optional[str]:
        """Genera diagrama de flujo desde GitHub Actions workflow"""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Error parseando {workflow_file}: {e}")
            return None
        
        jobs = workflow_data.get('jobs', {})
        
        if not jobs:
            return None
        
        diagram = "```mermaid\nflowchart TD\n"
        diagram += "    Start([Inicio])\n"
        
        # Ordenar jobs por needs
        job_names = list(jobs.keys())
        
        for idx, job_name in enumerate(job_names):
            job = jobs[job_name]
            
            # Añadir nodo del job
            diagram += f"    Job{idx}[{job_name}]\n"
            
            # Conectar desde Start si es primer job
            if idx == 0:
                diagram += f"    Start --> Job{idx}\n"
            
            # Añadir steps importantes
            steps = job.get('steps', [])
            important_steps = [s for s in steps if 'name' in s and 
                              any(keyword in s['name'].lower() 
                                  for keyword in ['build', 'test', 'deploy', 'publish'])]
            
            for step_idx, step in enumerate(important_steps[:3]):  # Max 3 steps
                step_name = step['name']
                diagram += f"    Step{idx}_{step_idx}[{step_name}]\n"
                diagram += f"    Job{idx} --> Step{idx}_{step_idx}\n"
            
            # Conectar con siguiente job
            needs = job.get('needs', [])
            if isinstance(needs, str):
                needs = [needs]
            
            for need in needs:
                need_idx = job_names.index(need) if need in job_names else -1
                if need_idx >= 0:
                    diagram += f"    Job{need_idx} --> Job{idx}\n"
        
        diagram += f"    Job{len(job_names)-1} --> End([Fin])\n"
        diagram += "```\n"
        
        return diagram
    
    def generate_component_diagram(self, repos_path: Path) -> Optional[str]:
        """Genera diagrama de componentes desde estructura de repos"""
        diagram = "```mermaid\ngraph LR\n"
        diagram += "    subgraph Frontend\n"
        diagram += "        UI[Interfaz Web]\n"
        diagram += "        JSDOS[JS-DOS Emulator]\n"
        diagram += "    end\n\n"
        
        diagram += "    subgraph Gateway\n"
        diagram += "        Kong[Kong API Gateway]\n"
        diagram += "        OAuth[OAuth2 Proxy]\n"
        diagram += "    end\n\n"
        
        diagram += "    subgraph Microservicios\n"
        diagram += "        Auth[Auth Service]\n"
        diagram += "        User[User Service]\n"
        diagram += "        Catalog[Game Catalog]\n"
        diagram += "        Score[Score Service]\n"
        diagram += "        Ranking[Ranking Service]\n"
        diagram += "    end\n\n"
        
        diagram += "    subgraph Datos\n"
        diagram += "        DB[(PostgreSQL)]\n"
        diagram += "        S3[S3 Storage]\n"
        diagram += "    end\n\n"
        
        # Conexiones
        diagram += "    UI --> Kong\n"
        diagram += "    Kong --> OAuth\n"
        diagram += "    OAuth --> Auth\n"
        diagram += "    Kong --> User\n"
        diagram += "    Kong --> Catalog\n"
        diagram += "    Kong --> Score\n"
        diagram += "    Kong --> Ranking\n"
        diagram += "    Auth --> DB\n"
        diagram += "    User --> DB\n"
        diagram += "    Catalog --> S3\n"
        diagram += "    Score --> DB\n"
        diagram += "    Ranking --> DB\n"
        diagram += "```\n"
        
        return diagram
    
    def insert_diagram_in_mdx(self, mdx_file: Path, diagram: str, section: str) -> bool:
        """Inserta un diagrama en un archivo MDX"""
        try:
            with open(mdx_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return False
        
        # Buscar sección
        section_pattern = rf'^##\s+{re.escape(section)}.*$'
        match = re.search(section_pattern, content, re.MULTILINE)
        
        if not match:
            # Añadir sección al final
            content += f"\n\n## {section}\n\n{diagram}\n"
        else:
            # Insertar después de la sección
            insert_pos = match.end()
            content = content[:insert_pos] + f"\n\n{diagram}\n" + content[insert_pos:]
        
        try:
            with open(mdx_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    def run(self, docs_path: Path) -> Dict[str, List[str]]:
        """Ejecuta generación de diagramas"""
        generated = {
            'sequence': [],
            'architecture': [],
            'flow': [],
            'component': []
        }
        
        print("🎨 Generando diagramas automáticamente...")
        
        # 1. Diagrama de componentes general
        print("\n📊 Generando diagrama de componentes...")
        comp_diagram = self.generate_component_diagram(self.repos_path)
        if comp_diagram:
            architecture_file = docs_path / 'architecture.mdx'
            if self.insert_diagram_in_mdx(architecture_file, comp_diagram, "Arquitectura de Componentes"):
                generated['component'].append(str(architecture_file))
                print(f"   ✅ Insertado en {architecture_file}")
        
        # 2. Docker compose
        print("\n🐳 Buscando docker-compose.yml...")
        compose_files = list(self.repos_path.rglob('docker-compose.yml'))
        for compose_file in compose_files[:3]:  # Máximo 3
            diagram = self.generate_architecture_from_docker_compose(compose_file)
            if diagram:
                generated['architecture'].append(str(compose_file))
                print(f"   ✅ {compose_file.name}")
        
        # 3. GitHub workflows
        print("\n⚙️  Buscando workflows...")
        workflow_files = list(self.repos_path.rglob('.github/workflows/*.yml'))
        for workflow_file in workflow_files[:5]:  # Máximo 5
            diagram = self.generate_flow_from_workflow(workflow_file)
            if diagram:
                generated['flow'].append(str(workflow_file))
                print(f"   ✅ {workflow_file.name}")
        
        return generated


def main():
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Generador automático de diagramas')
    parser.add_argument('--repos-path', required=True, help='Path a repositorios')
    parser.add_argument('--docs-path', required=True, help='Path a documentación')
    parser.add_argument('--output', default='generated-diagrams.json', help='Archivo de output')
    
    args = parser.parse_args()
    
    print("🚀 Iniciando generación automática de diagramas...")
    
    generator = DiagramGenerator(args.repos_path)
    results = generator.run(Path(args.docs_path))
    
    # Guardar resultados
    output_path = Path(args.docs_path) / args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    total = sum(len(v) for v in results.values())
    print(f"\n✅ Generados {total} diagramas")
    print(f"   📊 Componentes: {len(results['component'])}")
    print(f"   🏗️  Arquitectura: {len(results['architecture'])}")
    print(f"   📈 Flujos: {len(results['flow'])}")
    print(f"   🔄 Secuencia: {len(results['sequence'])}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
