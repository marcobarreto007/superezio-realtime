"""
RAG Retriever Protocol (Interface)
Define contrato para retrievers de RAG
"""
from typing import Protocol, List, Optional


class Retriever(Protocol):
    """Protocolo para retrievers de RAG"""
    
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
        ...

