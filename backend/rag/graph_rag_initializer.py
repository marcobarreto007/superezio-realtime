"""
Graph RAG Initializer
Inicializa grafo de conhecimento semântico com dados conhecidos do SuperEzio
"""
from pathlib import Path
from rag.graph_rag import graph_rag # Importar a instância global
import networkx as nx
from typing import Dict, Any, List

def initialize_family_graph(graph: nx.DiGraph):
    """Inicializa grafo com informações da família Barreto."""
    
    # Entidades - Pessoas
    entities = [
        {"id": "person_marco", "name": "Marco Barreto", "type": "person", "properties": {
            "age": 51,
            "location": "Montréal, QC, Canada",
            "origin": "Brasil",
            "team": "Fluminense",
            "creator_of": "SuperEzio"
        }},
        {"id": "person_ana_paula", "name": "Ana Paula", "type": "person", "properties": {
            "role": "Analista Júnior ONF/NFB",
            "previous": "Dentista (Brasil)",
            "location": "Montréal"
        }},
        {"id": "person_rapha", "name": "Rapha", "type": "person", "properties": {
            "university": "Université de Montréal",
            "program": "Ciências Políticas",
            "goal": "Direito",
            "grades": "A/A+",
            "interests": ["LoL", "MMA", "PS5", "cultura japonesa"],
            "sports": ["hóquei (Edmonton Oilers)", "futebol (Real Madrid)"]
        }},
        {"id": "person_alice", "name": "Alice", "type": "person", "properties": {
            "school": "Sec 3",
            "interests": ["bossa nova japonesa", "Hello Kitty"],
            "talent": "Saxofone",
            "goal": "Dentista"
        }},
        {"id": "person_mike", "name": "Mike", "type": "person", "properties": {
            "type": "Yorke",
            "trait": "barulhento"
        }},
        {"id": "person_matheus", "name": "Matheus", "type": "person", "properties": {
            "relation": "Irmão da Ana Paula",
            "location": "Brasil",
            "trait": "autista",
            "family_goal": "Trazer para Canadá"
        }},
    ]
    
    # Entidades - Projetos
    projects = [
        {"id": "project_superezio", "name": "SuperEzio", "type": "project", "properties": {
            "type": "Mini-AGI",
            "description": "Chatbot com personalidade própria",
            "status": "ativo"
        }},
        {"id": "project_trafficai", "name": "TrafficAI", "type": "project", "properties": {
            "type": "Análise de tráfego",
            "tech": "YOLO, RT-DETR, ByteTrack",
            "goal": "Competir com Miovision"
        }},
        {"id": "project_bebe_ia", "name": "BEBE-IA", "type": "project", "properties": {
            "type": "Trading algorítmico",
            "tech": "Genetic + CMA-ES + CNN/GRU"
        }},
        {"id": "project_xubudget", "name": "Xubudget", "type": "project", "properties": {
            "type": "Finanças pessoais",
            "features": "RAG, assistente familiar"
        }},
    ]
    
    # Entidades - Localizações
    locations = [
        {"id": "location_montreal", "name": "Montréal", "type": "location", "properties": {
            "province": "QC",
            "country": "Canada"
        }},
        {"id": "location_udem", "name": "Université de Montréal", "type": "location", "properties": {
            "type": "universidade"
        }},
    ]
    
    # Adicionar todas as entidades
    for entity_data in entities + projects + locations:
        entity_id = entity_data['id']
        graph.add_node(entity_id, **entity_data)
    
    # Relações
    relationships = [
        {"source_id": "person_marco", "target_id": "person_ana_paula", "relation_type": "married_to"},
        {"source_id": "person_marco", "target_id": "person_rapha", "relation_type": "father_of"},
        {"source_id": "person_marco", "target_id": "person_alice", "relation_type": "father_of"},
        {"source_id": "person_ana_paula", "target_id": "person_rapha", "relation_type": "mother_of"},
        {"source_id": "person_ana_paula", "target_id": "person_alice", "relation_type": "mother_of"},
        {"source_id": "person_ana_paula", "target_id": "person_matheus", "relation_type": "sister_of"},
        
        {"source_id": "person_marco", "target_id": "project_superezio", "relation_type": "created"},
        {"source_id": "person_marco", "target_id": "project_trafficai", "relation_type": "works_on"},
        {"source_id": "person_marco", "target_id": "project_bebe_ia", "relation_type": "works_on"},
        {"source_id": "person_marco", "target_id": "project_xubudget", "relation_type": "works_on"},
        
        {"source_id": "person_rapha", "target_id": "location_udem", "relation_type": "studies_at"},
        {"source_id": "person_rapha", "target_id": "location_montreal", "relation_type": "lives_in"},
        
        {"source_id": "person_marco", "target_id": "location_montreal", "relation_type": "lives_in"},
        {"source_id": "person_ana_paula", "target_id": "location_montreal", "relation_type": "lives_in"},
        {"source_id": "person_rapha", "target_id": "location_montreal", "relation_type": "lives_in"},
        {"source_id": "person_alice", "target_id": "location_montreal", "relation_type": "lives_in"},
    ]
    
    for rel_data in relationships:
        source_id = rel_data['source_id']
        target_id = rel_data['target_id']
        if source_id in graph and target_id in graph:
            graph.add_edge(source_id, target_id, type=rel_data['relation_type'], **rel_data)
    
    print(f"✅ Grafo semântico inicializado: {graph.number_of_nodes()} entidades, {graph.number_of_edges()} relações")


def initialize_graph_rag():
    """Inicializa Graph RAG completo"""
    
    print("🔷 Inicializando Graph RAG (semântico)...")
    if graph_rag.semantic_graph is None:
        graph_rag.semantic_graph = nx.DiGraph()
    initialize_family_graph(graph_rag.semantic_graph)
    print(f"✅ Graph RAG semântico pronto.")

if __name__ == "__main__":
    initialize_graph_rag()

