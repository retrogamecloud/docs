#!/usr/bin/env python3
"""
Incremental Analysis with Cache
Analiza solo archivos modificados usando cache SHA256
"""
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional


class AnalysisCache:
    def __init__(self, cache_path: str):
        self.cache_path = Path(cache_path)
        self.cache_file = self.cache_path / '.analysis-cache.json'
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Carga cache desde archivo"""
        if not self.cache_file.exists():
            return {
                'version': '1.0',
                'last_full_analysis': None,
                'files': {},
                'analysis_results': {}
            }
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error cargando cache: {e}")
            return {
                'version': '1.0',
                'last_full_analysis': None,
                'files': {},
                'analysis_results': {}
            }
    
    def _save_cache(self):
        """Guarda cache a archivo"""
        try:
            self.cache_path.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2)
            print(f"✅ Cache guardado: {self.cache_file}")
        except Exception as e:
            print(f"⚠️  Error guardando cache: {e}")
    
    def compute_file_hash(self, filepath: Path) -> str:
        """Calcula SHA256 de un archivo"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def get_modified_files(self, files: List[Path]) -> List[Path]:
        """Detecta archivos modificados comparando con cache"""
        modified = []
        
        for filepath in files:
            rel_path = str(filepath)
            current_hash = self.compute_file_hash(filepath)
            
            if not current_hash:
                continue
            
            cached_hash = self.cache_data['files'].get(rel_path, {}).get('hash')
            
            if current_hash != cached_hash:
                modified.append(filepath)
        
        return modified
    
    def update_file_cache(self, filepath: Path, analysis_result: Optional[Dict] = None):
        """Actualiza cache para un archivo"""
        rel_path = str(filepath)
        file_hash = self.compute_file_hash(filepath)
        
        self.cache_data['files'][rel_path] = {
            'hash': file_hash,
            'last_analyzed': datetime.now().isoformat(),
            'size': filepath.stat().st_size if filepath.exists() else 0
        }
        
        if analysis_result:
            self.cache_data['analysis_results'][rel_path] = analysis_result
    
    def needs_full_analysis(self, force_interval_days: int = 7) -> bool:
        """Determina si se necesita análisis completo"""
        last_full = self.cache_data.get('last_full_analysis')
        
        if not last_full:
            return True
        
        try:
            last_date = datetime.fromisoformat(last_full)
            days_since = (datetime.now() - last_date).days
            
            return days_since >= force_interval_days
        except Exception:
            return True
    
    def mark_full_analysis(self):
        """Marca que se hizo análisis completo"""
        self.cache_data['last_full_analysis'] = datetime.now().isoformat()
    
    def save(self):
        """Guarda cambios al cache"""
        self._save_cache()
    
    def get_cached_result(self, filepath: Path) -> Optional[Dict]:
        """Obtiene resultado cacheado de análisis anterior"""
        rel_path = str(filepath)
        return self.cache_data['analysis_results'].get(rel_path)
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del cache"""
        total_files = len(self.cache_data['files'])
        last_full = self.cache_data.get('last_full_analysis', 'Nunca')
        
        return {
            'total_files_cached': total_files,
            'last_full_analysis': last_full,
            'cache_size_kb': self.cache_file.stat().st_size // 1024 if self.cache_file.exists() else 0
        }


def get_changed_files_from_git(repo_path: Path) -> Set[str]:
    """Obtiene archivos modificados desde último commit usando git"""
    import subprocess
    
    try:
        # Archivos modificados en working directory
        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        modified = set(result.stdout.strip().split('\n'))
        
        # Archivos en staging
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        staged = set(result.stdout.strip().split('\n'))
        
        # Archivos no tracked
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        untracked = set(result.stdout.strip().split('\n'))
        
        all_changed = modified | staged | untracked
        all_changed.discard('')  # Eliminar vacíos
        
        return all_changed
    except Exception as e:
        print(f"⚠️  Error obteniendo cambios de git: {e}")
        return set()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis incremental con cache')
    parser.add_argument('--docs-path', required=True, help='Path al repo de docs')
    parser.add_argument('--force-full', action='store_true', help='Forzar análisis completo')
    parser.add_argument('--full-interval-days', type=int, default=7, help='Días entre análisis completos')
    parser.add_argument('--output', default='incremental-analysis.json', help='Archivo de output')
    
    args = parser.parse_args()
    
    docs_path = Path(args.docs_path)
    
    print("🔄 Iniciando análisis incremental...")
    
    # Inicializar cache
    cache = AnalysisCache(str(docs_path))
    stats = cache.get_stats()
    
    print(f"📊 Cache stats:")
    print(f"   - Archivos cacheados: {stats['total_files_cached']}")
    print(f"   - Último análisis completo: {stats['last_full_analysis']}")
    print(f"   - Tamaño cache: {stats['cache_size_kb']} KB")
    
    # Determinar tipo de análisis
    needs_full = cache.needs_full_analysis(args.full_interval_days) or args.force_full
    
    if needs_full:
        print("\n🔍 Análisis COMPLETO requerido")
        print(f"   Razón: {'Forzado por usuario' if args.force_full else f'Han pasado >{args.full_interval_days} días'}")
    else:
        print("\n⚡ Análisis INCREMENTAL")
    
    # Escanear archivos
    all_files = list(docs_path.rglob('*.mdx')) + list(docs_path.rglob('*.md'))
    all_files = [f for f in all_files if not any(
        part.startswith('.') for part in f.parts
    )]
    
    print(f"\n📂 Total de archivos: {len(all_files)}")
    
    if needs_full:
        # Análisis completo
        files_to_analyze = all_files
        cache.mark_full_analysis()
    else:
        # Análisis incremental
        # 1. Detectar cambios por git
        git_changed = get_changed_files_from_git(docs_path)
        git_changed_paths = [docs_path / f for f in git_changed if f.endswith(('.mdx', '.md'))]
        
        # 2. Detectar cambios por hash
        hash_changed = cache.get_modified_files(all_files)
        
        # Unir ambos
        files_to_analyze = list(set(git_changed_paths) | set(hash_changed))
        
        print(f"   📝 Cambios detectados por git: {len(git_changed_paths)}")
        print(f"   🔒 Cambios detectados por hash: {len(hash_changed)}")
        print(f"   ⚡ Total a analizar: {len(files_to_analyze)}")
    
    # Simular análisis (en producción llamaría a intelligent-doc-analyzer.py)
    results = {
        'analysis_type': 'full' if needs_full else 'incremental',
        'timestamp': datetime.now().isoformat(),
        'files_analyzed': len(files_to_analyze),
        'files_skipped': len(all_files) - len(files_to_analyze),
        'files': []
    }
    
    for filepath in files_to_analyze:
        rel_path = filepath.relative_to(docs_path)
        
        # Actualizar cache
        cache.update_file_cache(filepath, {'analyzed': True})
        
        results['files'].append(str(rel_path))
        print(f"   ✓ {rel_path}")
    
    # Guardar resultados
    output_path = docs_path / args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Resultados guardados: {args.output}")
    
    # Guardar cache
    cache.save()
    
    # Resumen
    saved_percentage = 100 * (1 - len(files_to_analyze) / max(len(all_files), 1))
    print(f"\n✅ Análisis completado")
    print(f"   📊 Archivos analizados: {len(files_to_analyze)}/{len(all_files)}")
    print(f"   💰 Ahorro estimado: {saved_percentage:.1f}% (tokens/costos)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
