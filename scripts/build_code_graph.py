import os
import ast
import networkx as nx
from pathlib import Path
import json

def parse_python_file(file_path: Path, graph: nx.DiGraph):
    """Parses a Python file and adds its structure to the graph."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
            
            graph.add_node(str(file_path), type='file', language='python')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        graph.add_node(alias.name, type='module')
                        graph.add_edge(str(file_path), alias.name, type='imports')
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        graph.add_node(node.module, type='module')
                        graph.add_edge(str(file_path), node.module, type='imports_from')
                elif isinstance(node, ast.FunctionDef):
                    graph.add_node(node.name, type='function', file=str(file_path))
                    graph.add_edge(str(file_path), node.name, type='defines_function')
                elif isinstance(node, ast.ClassDef):
                    graph.add_node(node.name, type='class', file=str(file_path))
                    graph.add_edge(str(file_path), node.name, type='defines_class')
    except Exception as e:
        print(f"  - Could not parse Python file {file_path}: {e}")

def parse_typescript_file(file_path: Path, graph: nx.DiGraph):
    """(Simplified) Parses a TypeScript file for imports and exports."""
    try:
        graph.add_node(str(file_path), type='file', language='typescript')
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("import"):
                    parts = line.split(" from ")
                    if len(parts) == 2:
                        module = parts[1].strip().replace("'", "").replace('"', "").replace(';', '')
                        graph.add_node(module, type='module')
                        graph.add_edge(str(file_path), module, type='imports')
                elif "export function" in line or "export const" in line:
                    # Simplified export parsing
                    try:
                        name = line.split(" ")[2].split("(")[0]
                        graph.add_node(name, type='function', file=str(file_path))
                        graph.add_edge(str(file_path), name, type='defines_function')
                    except:
                        pass
    except Exception as e:
        print(f"  - Could not parse TypeScript file {file_path}: {e}")

def build_code_graph(root_dir: str) -> nx.DiGraph:
    """Builds a code graph from the specified root directory."""
    graph = nx.DiGraph()
    root_path = Path(root_dir)
    
    print(f"🔍 Starting code graph build in: {root_path}")
    
    ignore_dirs = {'.venv', 'node_modules', 'dist', '__pycache__', '.git'}
    
    for file_path in root_path.rglob('*'):
        if any(part in ignore_dirs for part in file_path.parts):
            continue

        if file_path.is_file():
            if file_path.suffix == '.py':
                print(f"  - Parsing Python file: {file_path.relative_to(root_path)}")
                parse_python_file(file_path, graph)
            elif file_path.suffix in ['.ts', '.tsx']:
                print(f"  - Parsing TypeScript file: {file_path.relative_to(root_path)}")
                parse_typescript_file(file_path, graph)

    print(f"✅ Graph built with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
    return graph

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    code_graph = build_code_graph(project_root)
    
    # Save the graph
    graph_data_path = Path(project_root) / "data" / "code_graph.graphml"
    nx.write_graphml(code_graph, graph_data_path)
    
    print(f"\n🚀 Code graph saved to: {graph_data_path}")
