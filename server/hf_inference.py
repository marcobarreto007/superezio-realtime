"""
Hugging Face Inference Backend para SuperEzio
100% LOCAL - Modelo já baixado no disco, sem dependência do HF
Usa GPU NVIDIA (CUDA) para inferência local
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline
)
import torch

# Configuração - MODELO 100% LOCAL
# Caminho padrão: mesmo disco do projeto (C:)
# Para usar disco D:, defina LOCAL_MODEL_PATH no .env.local
LOCAL_MODEL_DIR = Path(os.getenv("LOCAL_MODEL_PATH", "./models/qwen2.5-7b-instruct")).resolve()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Verificar se modelo existe localmente
if not LOCAL_MODEL_DIR.exists():
    raise FileNotFoundError(
        f"❌ Modelo não encontrado em {LOCAL_MODEL_DIR}\n"
        f"📥 Execute primeiro: python scripts/download_model.py\n"
        f"   Isso vai baixar o modelo UMA VEZ do Hugging Face.\n"
        f"   Depois disso, funciona 100% offline!"
    )

# Carregar modelo (uma vez, reutilizar)
print(f"🚀 Carregando modelo 100% LOCAL de {LOCAL_MODEL_DIR}")
print(f"🎮 Dispositivo: {DEVICE}")
tokenizer = None
model = None
generator = None

def load_model():
    """Carrega o modelo LOCAL na GPU (100% offline, sem internet)"""
    global tokenizer, model, generator
    
    if model is not None:
        return  # Já carregado
    
    try:
        # Carregar tokenizer do disco LOCAL
        print(f"📂 Carregando tokenizer de {LOCAL_MODEL_DIR}...")
        tokenizer = AutoTokenizer.from_pretrained(
            str(LOCAL_MODEL_DIR),
            trust_remote_code=True,
            local_files_only=True,  # ✅ CRÍTICO: Só usar arquivos locais, sem internet
        )
        
        # Carregar modelo do disco LOCAL
        print(f"📂 Carregando modelo de {LOCAL_MODEL_DIR}...")
        model = AutoModelForCausalLM.from_pretrained(
            str(LOCAL_MODEL_DIR),
            torch_dtype=torch.float16,  # Half precision para economizar VRAM
            device_map="auto",  # Auto-detecta GPU
            trust_remote_code=True,
            local_files_only=True,  # ✅ CRÍTICO: Sem internet, só arquivos locais
        )
        
        # Criar pipeline
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if DEVICE == "cuda" else -1,
        )
        
        vram_used = torch.cuda.memory_allocated(0) / 1024**3 if DEVICE == "cuda" else 0
        print(f"✅ Modelo carregado 100% LOCAL!")
        print(f"💾 VRAM usada: {vram_used:.2f} GB")
        print(f"🌐 Status: OFFLINE (sem dependência do Hugging Face)")
        
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        if "local_files_only" in str(e) or "not found" in str(e).lower():
            print(f"\n💡 Dica: Execute primeiro:")
            print(f"   python scripts/download_model.py")
        raise

def format_messages(messages: List[Dict[str, str]]) -> str:
    """Formata mensagens para o formato do modelo"""
    # Usar chat template do modelo
    if tokenizer and hasattr(tokenizer, 'apply_chat_template'):
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    
    # Fallback: formato simples
    formatted = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            formatted += f"System: {content}\n\n"
        elif role == "user":
            formatted += f"User: {content}\n\n"
        elif role == "assistant":
            formatted += f"Assistant: {content}\n\n"
    
    formatted += "Assistant: "
    return formatted

def chat_completion(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> Dict[str, Any]:
    """
    Gera resposta do modelo com suporte a function calling
    
    Args:
        messages: Lista de mensagens (formato OpenAI)
        tools: Lista de tools disponíveis (function calling)
        temperature: Temperatura para geração
        max_tokens: Máximo de tokens a gerar
    
    Returns:
        Dict com 'content' e opcionalmente 'tool_calls'
    """
    global generator
    
    if generator is None:
        load_model()
    
    # Formatar prompt
    prompt = format_messages(messages)
    
    # Se há tools, adicionar ao prompt (function calling)
    if tools:
        tools_json = json.dumps(tools, indent=2)
        prompt += f"\n\n[AVAILABLE_TOOLS]\n{tools_json}\n\n"
        prompt += "Você pode chamar essas ferramentas quando necessário. Responda em JSON com 'content' e 'tool_calls'.\n"
    
    try:
        # Gerar resposta
        outputs = generator(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            top_k=40,
            do_sample=True,
            return_full_text=False,
        )
        
        response_text = outputs[0]["generated_text"]
        
        # Tentar parsear JSON se houver tool calls
        result = {"content": response_text, "tool_calls": None}
        
        if tools and "tool_calls" in response_text.lower():
            try:
                # Tentar extrair JSON da resposta
                json_match = response_text.find("{")
                if json_match != -1:
                    json_str = response_text[json_match:]
                    parsed = json.loads(json_str)
                    if "tool_calls" in parsed:
                        result["tool_calls"] = parsed["tool_calls"]
                        result["content"] = parsed.get("content", response_text)
            except:
                pass  # Se não conseguir parsear, retorna texto normal
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "content": f"Erro ao gerar resposta: {e}"
        }

# Teste básico
if __name__ == "__main__":
    load_model()
    
    test_messages = [
        {"role": "system", "content": "Você é SuperEzio, um assistente direto e objetivo."},
        {"role": "user", "content": "Oi, como você está?"}
    ]
    
    result = chat_completion(test_messages)
    print("\n📝 Resposta:")
    print(result["content"])

