"""
RAG Selector - Seleciona namespace correto para busca RAG
Mapeia especialista → namespace de memória RAG
"""

from typing import Optional


# Mapeamento de especialista para namespace RAG
EXPERT_TO_NAMESPACE = {
    "familia": "familia",
    "contabilidade": "contabilidade",
    "trafego": "trafego",
    "pessoal": "vida_pessoal",
    "geral": None  # Sem RAG para conhecimento geral
}


def get_rag_namespace(expert: str) -> Optional[str]:
    """
    Retorna o namespace RAG apropriado para um especialista
    
    Args:
        expert: Nome do especialista ('familia', 'contabilidade', etc.)
    
    Returns:
        str | None: Nome do namespace RAG ou None se não usar RAG
    """
    return EXPERT_TO_NAMESPACE.get(expert, None)


def list_namespaces() -> dict:
    """Retorna todos os namespaces disponíveis"""
    return {
        expert: namespace 
        for expert, namespace in EXPERT_TO_NAMESPACE.items() 
        if namespace is not None
    }


def validate_namespace(namespace: str) -> bool:
    """Verifica se um namespace é válido"""
    return namespace in EXPERT_TO_NAMESPACE.values() and namespace is not None


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🗂️  RAG NAMESPACES")
    print("="*80)
    
    for expert in ["familia", "contabilidade", "trafego", "pessoal", "geral"]:
        namespace = get_rag_namespace(expert)
        status = "✅" if namespace else "❌"
        print(f"{status} {expert:15} -> {namespace or 'None (sem RAG)'}")
    
    print("\n📦 Namespaces ativos:")
    for expert, ns in list_namespaces().items():
        print(f"   - {expert}: {ns}")
    print("="*80 + "\n")
