"""
Graph RAG Implementation com NetworkX para Código e Conhecimento Semântico
"""
import json
import networkx as nx
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import os
import re

# Caminho para o grafo de código pré-construído
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CODE_GRAPH_PATH = PROJECT_ROOT / "data" / "code_graph.graphml"
SEMANTIC_GRAPH_PATH = PROJECT_ROOT / "data" / "semantic_graph.json"


class GraphRAG:
    """
    Graph RAG - Retrieval usando grafo de conhecimento (código + semântico)
    """
    
    def __init__(self):
        self.code_graph: Optional[nx.DiGraph] = None
        self.semantic_graph: Optional[nx.DiGraph] = None # Para informações semânticas como família
        self._load_graphs()
        
    def _load_graphs(self):
        """Carrega os grafos de código e semântico"""
        # Carregar grafo de código NetworkX
        if CODE_GRAPH_PATH.exists():
            print(f"Loading code graph from {CODE_GRAPH_PATH}...")
            self.code_graph = nx.read_graphml(CODE_GRAPH_PATH)
            print(f"Code graph loaded: {self.code_graph.number_of_nodes()} nodes, {self.code_graph.number_of_edges()} edges")
        else:
            print(f"WARNING: Code graph not found at {CODE_GRAPH_PATH}. Please run scripts/build_code_graph.py")
            self.code_graph = nx.DiGraph() # Iniciar vazio
            
        # Carregar grafo semântico (se existir)
        if SEMANTIC_GRAPH_PATH.exists():
            print(f"Loading semantic graph from {SEMANTIC_GRAPH_PATH}...")
            with open(SEMANTIC_GRAPH_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.semantic_graph = nx.json_graph.node_link_graph(data)
            print(f"Semantic graph loaded: {self.semantic_graph.number_of_nodes()} nodes, {self.semantic_graph.number_of_edges()} edges")
        else:
            print(f"Semantic graph not found at {SEMANTIC_GRAPH_PATH}. Initializing empty.")
            self.semantic_graph = nx.DiGraph()
            

    def ingest_semantic_data(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> None:
        """
        Ingere dados semânticos (ex: informações de família) no grafo semântico.
        """
        if not self.semantic_graph:
            self.semantic_graph = nx.DiGraph()

        for entity_data in entities:
            # Garante que 'id' exista
            entity_id = entity_data.get('id')
            if not entity_id:
                continue
            
            # Adiciona todos os atributos como atributos do nó
            self.semantic_graph.add_node(entity_id, **entity_data)
            
        for rel_data in relationships:
            source_id = rel_data.get('source_id')
            target_id = rel_data.get('target_id')
            relation_type = rel_data.get('relation_type')
            
            if source_id in self.semantic_graph and target_id in self.semantic_graph:
                self.semantic_graph.add_edge(source_id, target_id, type=relation_type, **rel_data)
        
        # Salvar o grafo semântico
        SEMANTIC_GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SEMANTIC_GRAPH_PATH, 'w', encoding='utf-8') as f:
            data = nx.json_graph.node_link_data(self.semantic_graph)
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Semantic graph updated and saved to {SEMANTIC_GRAPH_PATH}")


    def query_graph(
        self,
        query: str,
        max_results: int = 5,
        max_depth: int = 2,
        domains: Optional[List[str]] = None # 'code' ou 'semantic'
    ) -> List[Dict[str, Any]]:
        """
        Consulta os grafos de conhecimento (código e semântico) para encontrar contexto.
        Retorna contexto rico com entidades e relações.
        """
        results = []
        
        # === Consultar Grafo de Código ===
        if self.code_graph and (not domains or 'code' in domains):
            # Tentar encontrar nós que correspondam à query (case-insensitive)
            query_lower = query.lower()
            relevant_nodes = []
            
            # Busca por nome exato (função, classe, arquivo)
            for node_id, data in self.code_graph.nodes(data=True):
                if query_lower in node_id.lower() or query_lower in data.get('label', '').lower():
                    relevant_nodes.append(node_id)
            
            # Se não encontrou, tentar extrair termos-chave e buscar
            if not relevant_nodes:
                # Exemplo simples de extração de termos. Em produção, usaria LLM ou mais NLP.
                keywords = set(re.findall(r'\b\w+\b', query_lower))
                for node_id, data in self.code_graph.nodes(data=True):
                    if any(keyword in node_id.lower() for keyword in keywords):
                        relevant_nodes.append(node_id)
            
            seen_nodes = set()
            for start_node in relevant_nodes[:max_results]: # Limitar busca inicial
                if start_node in seen_nodes:
                    continue
                seen_nodes.add(start_node)

                # Coletar vizinhos e atributos do nó
                node_context = {
                    "entity": self.code_graph.nodes[start_node],
                    "id": start_node,
                    "related_entities": [],
                    "relationships": []
                }
                
                for neighbor in nx.neighbors(self.code_graph, start_node):
                    if neighbor not in seen_nodes:
                        seen_nodes.add(neighbor)
                        node_context["related_entities"].append(self.code_graph.nodes[neighbor])
                        edge_data = self.code_graph.get_edge_data(start_node, neighbor)
                        if edge_data:
                            node_context["relationships"].append({
                                "source": start_node,
                                "target": neighbor,
                                "type": edge_data.get('type', 'unknown')
                            })
                results.append(node_context)
                if len(results) >= max_results:
                    break

        # === Consultar Grafo Semântico ===
        if self.semantic_graph and (not domains or 'semantic' in domains):
            # Lógica similar de busca e extração de contexto do grafo semântico
            # Por simplicidade, faremos uma busca por nome de entidade
            query_lower = query.lower()
            semantic_entities = []
            for node_id, data in self.semantic_graph.nodes(data=True):
                if query_lower in str(node_id).lower() or query_lower in data.get('name', '').lower():
                    semantic_entities.append(node_id)
            
            for start_node in semantic_entities[:max_results]:
                if start_node in seen_nodes: # Evitar duplicatas se IDs se sobrepõem
                    continue
                seen_nodes.add(start_node)

                node_context = {
                    "entity": self.semantic_graph.nodes[start_node],
                    "id": start_node,
                    "related_entities": [],
                    "relationships": []
                }
                
                for neighbor in nx.neighbors(self.semantic_graph, start_node):
                    if neighbor not in seen_nodes:
                        seen_nodes.add(neighbor)
                        node_context["related_entities"].append(self.semantic_graph.nodes[neighbor])
                        edge_data = self.semantic_graph.get_edge_data(start_node, neighbor)
                        if edge_data:
                            node_context["relationships"].append({
                                "source": start_node,
                                "target": neighbor,
                                "type": edge_data.get('type', 'unknown')
                            })
                results.append(node_context)
                if len(results) >= max_results:
                    break


        return results[:max_results]
    
    def build_context_from_graph(
        self,
        query: str,
        max_entities: int = 5,
        domains: Optional[List[str]] = None
    ) -> str:
        """
        Constrói contexto formatado a partir do grafo
        """
        graph_results = self.query_graph(query, max_results=max_entities, domains=domains)
        
        if not graph_results:
            return ""
        
        context_parts = [
            "[GRAPH RAG CONTEXT - KNOWLEDGE GRAPH]",
            "",
            "The following information is extracted from the knowledge graph:",
            ""
        ]
        
        for idx, result in enumerate(graph_results, 1):
            entity = result["entity"]
            entity_id = result["id"] # Usar o ID do nó que é sempre string
            
            # Adiciona informações do nó
            context_parts.append(f"{idx}. Entity: {entity_id} (Type: {entity.get('type', 'unknown')})")
            
            for prop_key, prop_value in entity.items():
                if prop_key not in ['id', 'label', 'type', 'file', 'language'] and isinstance(prop_value, (str, int, float, bool)):
                    context_parts.append(f"   - {prop_key.replace('_', ' ').capitalize()}: {prop_value}")
            
            # Se for um arquivo de código, tentar incluir o conteúdo (simplificado)
            if entity.get('type') == 'file' and entity.get('language') in ['python', 'typescript']:
                file_path = Path(entity_id)
                if file_path.exists() and file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content_preview = f.read(200) + "..." # Primeiros 200 chars
                        context_parts.append(f"   Content Preview: ```{content_preview}```")
                    except Exception as e:
                        context_parts.append(f"   Could not read file content: {e}")
            
            if result["related_entities"]:
                context_parts.append(f"   Related entities:")
                for rel_entity_data in result["related_entities"][:3]:
                    rel_entity_id = rel_entity_data.get('id', 'unknown')
                    rel_entity_type = rel_entity_data.get('type', 'unknown')
                    # Tentar encontrar o tipo de relação
                    relation_type = 'unknown'
                    for edge_src, edge_dst, edge_data in self.code_graph.edges(data=True):
                        if (edge_src == entity_id and edge_dst == rel_entity_id) or \
                           (edge_dst == entity_id and edge_src == rel_entity_id):
                            relation_type = edge_data.get('type', 'unknown')
                            break
                    context_parts.append(f"     • {rel_entity_id} (Type: {rel_entity_type}, Relation: {relation_type})")
            
            context_parts.append("")
        
        context_parts.append("[END GRAPH RAG CONTEXT]")
        
        return "\n".join(context_parts)
    

# Instância global
graph_rag = GraphRAG()


