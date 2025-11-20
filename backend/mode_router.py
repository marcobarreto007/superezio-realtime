"""
Router automático de modo LoRA baseado em análise de conteúdo
Detecta automaticamente quando usar mode="familia" baseado em palavras-chave
"""
from typing import Optional, List, Dict

# Palavras-chave que indicam conversa sobre família
FAMILY_KEYWORDS = [
    # Nomes da família
    "rapha", "rafa", "raphael",
    "ana paula", "ana paula", "ap",
    "alice",
    "matheus",
    "mike",
    "marco barreto", "marco",
    "barreto",
    
    # Relacionamentos familiares
    "família", "familia", "family",
    "meu filho", "minha filha",
    "meu marido", "minha esposa",
    "meu irmão", "minha irmã",
    "pai", "mãe", "mama", "papai",
    
    # Contexto familiar
    "casa", "casa da família",
    "montreal", "canadá", "canada",
    "edmonton oilers", "mcdavid",
    "udeM", "universidade",
    "saxofone", "hello kitty",
    "ritual 20:00",
]

def auto_route_mode(
    messages: List[Dict[str, str]], 
    explicit_mode: Optional[str] = None
) -> Optional[str]:
    """
    Roteia automaticamente o modo LoRA baseado no conteúdo das mensagens.
    
    Args:
        messages: Lista de mensagens (formato OpenAI: [{"role": "user", "content": "..."}])
        explicit_mode: Modo explicitamente passado pelo cliente (tem prioridade)
        
    Returns:
        "familia" se detectar keywords de família, None caso contrário
    """
    # Se o cliente passou mode explicitamente, respeitar
    if explicit_mode is not None:
        print(f"[ROUTER] Modo explícito recebido: {explicit_mode}")
        return explicit_mode
    
    # Extrair todo o texto das mensagens do usuário
    user_messages = [
        msg.get("content", "").lower() 
        for msg in messages 
        if msg.get("role") == "user"
    ]
    
    if not user_messages:
        print("[ROUTER] Nenhuma mensagem do usuário encontrada, usando modelo base")
        return None
    
    # Concatenar todas as mensagens do usuário
    full_text = " ".join(user_messages)
    
    # Verificar se alguma keyword de família aparece
    detected_keywords = []
    for keyword in FAMILY_KEYWORDS:
        if keyword.lower() in full_text:
            detected_keywords.append(keyword)
    
    if detected_keywords:
        print(f"[ROUTER] Keywords de família detectadas: {detected_keywords}")
        print(f"[ROUTER] explicit_mode=None → resolved_mode='familia'")
        return "familia"
    
    print(f"[ROUTER] Nenhuma keyword de família detectada")
    print(f"[ROUTER] explicit_mode=None → resolved_mode=None (modelo base)")
    return None

