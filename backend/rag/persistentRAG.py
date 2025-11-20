"""
Persistent RAG with Namespace Support
Armazena informações permanentemente organizadas por namespaces
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class PersistentRAG:
    def __init__(self, storage_dir: str = "data/rag"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache em memória por namespace
        self.memory: Dict[str, List[Dict[str, Any]]] = {}
        
        print(f"💾 [RAG] Inicializado em {self.storage_dir}")
    
    def _get_file_path(self, namespace: str) -> Path:
        """Retorna caminho do arquivo para um namespace"""
        return self.storage_dir / f"{namespace}.json"
    
    def _load_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        """Carrega namespace do disco"""
        if namespace in self.memory:
            return self.memory[namespace]
        
        file_path = self._get_file_path(namespace)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory[namespace] = data
                    print(f"✅ [RAG] Namespace '{namespace}': {len(data)} entradas carregadas")
                    return data
            except Exception as e:
                print(f"❌ [RAG] Erro ao carregar '{namespace}': {e}")
                self.memory[namespace] = []
                return []
        else:
            self.memory[namespace] = []
            return []
    
    def _save_namespace(self, namespace: str):
        """Salva namespace no disco"""
        file_path = self._get_file_path(namespace)
        try:
            data = self.memory.get(namespace, [])
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 [RAG] Namespace '{namespace}': {len(data)} entradas salvas")
        except Exception as e:
            print(f"❌ [RAG] Erro ao salvar '{namespace}': {e}")
    
    def add(self, namespace: str, text: str, tags: List[str] = None, metadata: Dict = None) -> str:
        """
        Adiciona informação a um namespace
        
        Args:
            namespace: Nome do namespace
            text: Conteúdo da informação
            tags: Tags opcionais
            metadata: Metadados opcionais
        
        Returns:
            str: ID da entrada criada
        """
        self._load_namespace(namespace)
        
        entry_id = f"{namespace}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.memory[namespace])}"
        
        entry = {
            "id": entry_id,
            "text": text,
            "tags": tags or [],
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "namespace": namespace
        }
        
        self.memory[namespace].append(entry)
        self._save_namespace(namespace)
        
        print(f"✅ [RAG] Adicionado em '{namespace}': {text[:80]}...")
        return entry_id
    
    def search(self, namespace: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca informações em um namespace
        
        Args:
            namespace: Nome do namespace
            query: Texto de busca
            limit: Número máximo de resultados
        
        Returns:
            List[Dict]: Lista de entradas relevantes
        """
        entries = self._load_namespace(namespace)
        
        if not entries:
            return []
        
        query_lower = query.lower()
        query_words = [w for w in query_lower.split() if len(w) > 2]
        
        # Calcular relevância
        scored_entries = []
        for entry in entries:
            text_lower = entry["text"].lower()
            
            # Contar palavras que aparecem
            matches = sum(1 for word in query_words if word in text_lower)
            relevance = matches / len(query_words) if query_words else 0
            
            if relevance > 0:
                entry_copy = entry.copy()
                entry_copy["relevance"] = relevance
                scored_entries.append(entry_copy)
        
        # Ordenar por relevância
        scored_entries.sort(key=lambda x: x["relevance"], reverse=True)
        
        results = scored_entries[:limit]
        print(f"🔍 [RAG] Busca em '{namespace}': {len(results)} resultados para '{query[:50]}'")
        
        return results
    
    def delete(self, namespace: str, entry_id: str) -> bool:
        """Remove uma entrada por ID"""
        entries = self._load_namespace(namespace)
        
        original_len = len(entries)
        self.memory[namespace] = [e for e in entries if e["id"] != entry_id]
        
        if len(self.memory[namespace]) < original_len:
            self._save_namespace(namespace)
            print(f"🗑️  [RAG] Removido de '{namespace}': {entry_id}")
            return True
        
        return False
    
    def list(self, namespace: str) -> List[Dict[str, Any]]:
        """Lista todas as entradas de um namespace"""
        entries = self._load_namespace(namespace)
        print(f"📋 [RAG] Listando '{namespace}': {len(entries)} entradas")
        return entries
    
    def list_namespaces(self) -> List[str]:
        """Lista todos os namespaces disponíveis"""
        namespaces = []
        for file_path in self.storage_dir.glob("*.json"):
            namespaces.append(file_path.stem)
        return namespaces
    
    def get_stats(self, namespace: str) -> Dict[str, Any]:
        """Retorna estatísticas de um namespace"""
        entries = self._load_namespace(namespace)
        
        return {
            "namespace": namespace,
            "total_entries": len(entries),
            "total_tags": len(set(tag for e in entries for tag in e.get("tags", []))),
            "file_path": str(self._get_file_path(namespace))
        }
    
    def build_context(self, namespace: str, query: str, limit: int = 3) -> str:
        """
        Constrói contexto RAG formatado para o modelo
        
        Args:
            namespace: Namespace para buscar
            query: Pergunta do usuário
            limit: Número de entradas
        
        Returns:
            str: Contexto formatado ou string vazia
        """
        results = self.search(namespace, query, limit)
        
        if not results:
            return ""
        
        context_parts = ["[RAG CONTEXT - Informações Relevantes]\n"]
        
        for idx, entry in enumerate(results, 1):
            relevance = entry.get("relevance", 0) * 100
            context_parts.append(f"[{idx}] (Relevância: {relevance:.0f}%)")
            context_parts.append(entry["text"])
            context_parts.append("")
        
        context_parts.append("[FIM DO CONTEXTO RAG]")
        
        return "\n".join(context_parts)


# Singleton global
_rag_instance = None

def get_rag_instance(storage_dir: str = "data/rag") -> PersistentRAG:
    """Retorna instância singleton do RAG"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = PersistentRAG(storage_dir)
    return _rag_instance


if __name__ == "__main__":
    # Teste rápido
    rag = PersistentRAG("data/rag_test")
    
    print("\n" + "="*80)
    print("🧪 TESTE PERSISTENT RAG")
    print("="*80)
    
    # Adicionar dados de teste
    rag.add("familia", "Rapha estuda na UdeM em Montreal", ["rapha", "educacao"])
    rag.add("familia", "Ana Paula é a mãe do Rapha", ["ana", "familia"])
    rag.add("contabilidade", "ICMS é um imposto estadual sobre circulação de mercadorias", ["icms", "impostos"])
    
    # Buscar
    print("\n🔍 Buscando 'Rapha':")
    results = rag.search("familia", "Rapha universidade", 2)
    for r in results:
        print(f"   - {r['text']} (relevância: {r.get('relevance', 0):.2f})")
    
    # Contexto
    print("\n📋 Contexto RAG:")
    context = rag.build_context("familia", "Onde o Rapha estuda?", 2)
    print(context)
    
    # Stats
    print("\n📊 Estatísticas:")
    stats = rag.get_stats("familia")
    print(f"   Namespace: {stats['namespace']}")
    print(f"   Entradas: {stats['total_entries']}")
    print(f"   Tags: {stats['total_tags']}")
    
    print("\n" + "="*80)
