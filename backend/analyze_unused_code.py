"""
Script para analisar código não usado no backend
Identifica módulos, funções e arquivos que não são importados/usados
"""
import ast
import os
from pathlib import Path
from typing import Set, Dict, List
from collections import defaultdict

# Arquivos principais que são entry points
ENTRY_POINTS = {
    "api.py",
    "inference.py",
    "expert_router.py",
    "mode_router.py",
    "rag_client.py",
    "tool_executor.py",
}

# Módulos que devem ser ignorados (são usados dinamicamente)
IGNORE_MODULES = {
    "__pycache__",
    "venv",
    "models",
    "data",
    "tests",
    "test_*.py",
}

def get_all_python_files(directory: Path) -> List[Path]:
    """Retorna todos os arquivos Python no diretório"""
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Ignorar diretórios
        dirs[:] = [d for d in dirs if d not in IGNORE_MODULES]
        
        for filename in filenames:
            if filename.endswith('.py') and not filename.startswith('test_'):
                files.append(Path(root) / filename)
    return files

def extract_imports(file_path: Path) -> Set[str]:
    """Extrai todos os imports de um arquivo Python"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception as e:
        print(f"Erro ao analisar {file_path}: {e}")
    
    return imports

def get_module_name(file_path: Path, base_dir: Path) -> str:
    """Converte caminho de arquivo para nome de módulo"""
    relative = file_path.relative_to(base_dir)
    parts = relative.parts[:-1] + (relative.stem,)
    return '.'.join(parts).replace('\\', '.')

def analyze_unused_code():
    """Analisa código não usado"""
    backend_dir = Path(__file__).parent
    all_files = get_all_python_files(backend_dir)
    
    # Mapear módulos para arquivos
    module_to_file: Dict[str, Path] = {}
    for file_path in all_files:
        module_name = get_module_name(file_path, backend_dir)
        module_to_file[module_name] = file_path
    
    # Coletar todos os imports de arquivos principais
    all_imports: Set[str] = set()
    imported_modules: Set[str] = set()
    
    for file_path in all_files:
        if file_path.name in ENTRY_POINTS or 'api.py' in str(file_path) or 'inference.py' in str(file_path):
            imports = extract_imports(file_path)
            all_imports.update(imports)
            
            # Adicionar módulos locais importados
            for imp in imports:
                if imp in module_to_file:
                    imported_modules.add(imp)
    
    # Encontrar módulos não importados
    all_modules = set(module_to_file.keys())
    unused_modules = all_modules - imported_modules - set(ENTRY_POINTS)
    
    # Filtrar módulos que são parte de pacotes usados
    used_packages = set()
    for imp in all_imports:
        parts = imp.split('.')
        if len(parts) > 1:
            used_packages.add(parts[0])
    
    # Remover módulos que são parte de pacotes usados
    final_unused = []
    for module in unused_modules:
        parts = module.split('.')
        if parts[0] not in used_packages and parts[0] not in ['utils', 'middleware', 'optimization', 'rag']:
            final_unused.append(module)
    
    print("="*80)
    print("ANÁLISE DE CÓDIGO NÃO USADO")
    print("="*80)
    print(f"\n📊 Total de arquivos Python: {len(all_files)}")
    print(f"📦 Módulos importados: {len(imported_modules)}")
    print(f"🗑️  Módulos potencialmente não usados: {len(final_unused)}")
    print("\n" + "="*80)
    print("MÓDULOS POTENCIALMENTE NÃO USADOS:")
    print("="*80)
    
    for module in sorted(final_unused):
        file_path = module_to_file.get(module)
        if file_path:
            print(f"  ❌ {module}")
            print(f"     📁 {file_path.relative_to(backend_dir)}")
    
    # Listar arquivos de teste
    test_files = [f for f in all_files if 'test' in f.name.lower()]
    print("\n" + "="*80)
    print(f"ARQUIVOS DE TESTE ({len(test_files)}):")
    print("="*80)
    for test_file in sorted(test_files):
        print(f"  🧪 {test_file.relative_to(backend_dir)}")
    
    return final_unused, module_to_file

if __name__ == "__main__":
    unused, modules = analyze_unused_code()

