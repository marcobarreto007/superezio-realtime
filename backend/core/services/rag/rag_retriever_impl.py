"""
RAG Retriever Implementation
Implementa Retriever protocol usando código existente de rag_client.py
"""
import os
from typing import List, Optional
from core.services.rag.retriever import Retriever
from infrastructure.config.settings import get_settings

# Importar código existente
from rag_client import query_rag, build_rag_system_message


class RAGRetrieverImpl:
    """
    Implementação do Retriever protocol.
    Usa Graph RAG + Enhanced RAG do código existente.
    """
    
    def __init__(self, use_enhanced: bool = True):
        """
        Args:
            use_enhanced: Se True, usa Enhanced RAG com técnicas avançadas
        """
        self.use_enhanced = use_enhanced
        self.settings = get_settings()
    
    def retrieve(
        self,
        domains: List[str],
        query: str,
        top_k: int = 6
    ) -> Optional[str]:
        """
        Recupera contexto relevante para a query.
        
        Args:
            domains: Lista de domínios RAG para buscar
            query: Query do usuário
            top_k: Número de chunks a retornar
            
        Returns:
            Contexto RAG formatado ou None
        """
        if not domains or not query:
            return None
        
        try:
            # Usar função existente query_rag
            chunks = query_rag(
                domains=domains,
                query=query,
                top_k=top_k,
                use_enhanced=self.use_enhanced
            )
            
            # Converter chunks para system message
            if chunks:
                return build_rag_system_message(chunks)
            
            return None
            
        except Exception as e:
            # Log erro mas não quebrar o fluxo
            if os.getenv("DEBUG_RAG", "true").lower() == "true":
                print(f"[RAG Retriever] Erro ao recuperar: {e}")
            return None


# Factory function
def create_rag_retriever(use_enhanced: bool = True) -> Retriever:
    """Factory para criar instância do RAG retriever"""
    return RAGRetrieverImpl(use_enhanced=use_enhanced)
