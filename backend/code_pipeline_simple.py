"""
Code Pipeline SIMPLIFICADO - 1 Passagem Otimizada

Ao invés de 3 modelos (5 min), usa 1 modelo com prompt otimizado (1 min)
"""
import time
from typing import List, Dict, Any

DEBUG = True

SUPEREZIO_CODE_PROMPT = """Você é SuperEzio-Code, especialista em programação.

MISSÃO: Gerar código completo, funcional e bem explicado.

REGRAS:
1. Entenda o pedido do usuário
2. Gere código COMPLETO (sem placeholders)
3. Explique em português coloquial
4. Dê comandos para executar (PowerShell)

FORMATO DE RESPOSTA (Markdown):
- Título do que foi feito
- Explicação curta em 2-3 parágrafos com gírias: "cara", "mano", etc
- Código completo (sem placeholders)
- Comandos para executar (PowerShell)
- Dicas e melhorias

IMPORTANTE:
- Código COMPLETO e funcional
- Sem "... rest of code"
- Comandos Windows PowerShell
- Português coloquial
- Use emoji: 🚀✅⚠️💡
"""


def run_code_pipeline_simple(
    messages: List[Dict[str, str]],
    expert_id: str,
    rag_context: str = None
) -> Dict[str, Any]:
    """
    Pipeline simplificado: 1 passagem otimizada.
    
    Args:
        messages: Mensagens do usuário
        expert_id: Expert ID (code_python, etc)
        rag_context: Contexto RAG (opcional)
        
    Returns:
        Dict com resposta final
    """
    start_time = time.time()
    
    if DEBUG:
        user_query = messages[-1]["content"] if messages else ""
        print(f"\n{'='*80}")
        print(f"🚀 [SIMPLE PIPELINE] 1-Stage Execution")
        print(f"   Expert: {expert_id}")
        print(f"   Query: {user_query[:60]}...")
        print(f"{'='*80}\n")
    
    from inference import chat_completion
    
    # Construir mensagens otimizadas
    pipeline_messages = [
        {"role": "system", "content": SUPEREZIO_CODE_PROMPT}
    ]
    
    # RAG context
    if rag_context:
        pipeline_messages.append({
            "role": "system",
            "content": f"[CONTEXTO RAG]\n{rag_context}\n[/CONTEXTO RAG]"
        })
    
    # Histórico do usuário
    for msg in messages:
        pipeline_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Chamar modelo (UMA VEZ)
    response = chat_completion(
        messages=pipeline_messages,
        temperature=0.4,
        max_tokens=1024,
        stream=False,
        _skip_pipeline=True  # CRITICAL
    )
    
    duration_ms = (time.time() - start_time) * 1000
    
    content = response.get("content", "") if isinstance(response, dict) else str(response)
    
    if DEBUG:
        print(f"\n{'='*80}")
        print(f"✅ [SIMPLE PIPELINE] Completed in {duration_ms:.0f}ms")
        print(f"   Content length: {len(content)} chars")
        print(f"{'='*80}\n")
    
    return {
        "content": content,
        "expert": expert_id,
        "pipeline_duration_ms": duration_ms,
        "pipeline_type": "simple"
    }


def is_code_expert(expert_id: str) -> bool:
    """Check if expert is code-related"""
    return expert_id.startswith("code_")
