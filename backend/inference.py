"""
Llama.cpp Inference Backend for SuperEzio
"""
import os
import json
import base64
from pathlib import Path
from typing import List, Dict, Optional, Any, Generator, Union
from llama_cpp import Llama, LlamaGrammar

# Desabilita lazy loading do transformers (speedup em Windows)
os.environ["TRANSFORMERS_NO_LAZY_IMPORT"] = "1"

from model_registry import get_model_and_tokenizer
from tool_executor import process_tool_calls
from expert_router import get_router
from rag_client import query_rag, build_rag_system_message
from prompt_builder import build_messages
from code_pipeline_simple import run_code_pipeline_simple, is_code_expert
from optimization.prompt_cache import prompt_cache

# Carregamento inicial do motor Llama.cpp e tokenizer
llm_engine, tokenizer = get_model_and_tokenizer()

SYSTEM_PROMPT = """Você é SuperEzio. Responda em português brasileiro de forma direta e objetiva."""

def image_to_base64_data_uri(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"

def chat_completion(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
    stream: bool = False,
    mode: Optional[str] = None,
    image_path: Optional[str] = None,
    _skip_pipeline: bool = False,
) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
    """Chat completion usando o motor Llama.cpp."""
    
    if image_path:
        last_user_message_index = -1
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].get("role") == "user":
                last_user_message_index = i
                break
        
        if last_user_message_index != -1:
            image_data_uri = image_to_base64_data_uri(image_path)
            messages[last_user_message_index]["content"] = [
                {"type": "image_url", "image_url": {"url": image_data_uri}},
                {"type": "text", "text": messages[last_user_message_index]["content"]}
            ]
            print("🖼️  Imagem adicionada ao prompt para Llama.cpp")

    user_query_content = messages[-1].get('content', '')
    if isinstance(user_query_content, list):
        user_query = " ".join([item['text'] for item in user_query_content if item['type'] == 'text'])
    else:
        user_query = user_query_content

    router = get_router()
    decision = router.route(messages, explicit_mode=mode)
    
    rag_chunks = query_rag(decision.rag_domains, user_query, top_k=6, use_enhanced=True)
    rag_system_message = build_rag_system_message(rag_chunks)
    
    final_messages = build_messages(
        base_system=SYSTEM_PROMPT,
        core_identity="Você é SuperEzio...",
        rag_message=rag_system_message,
        expert_id=decision.expert_id,
        history=messages[:-1],
        user_message=messages[-1],
        tools=tools
    )

    import time
    gen_start = time.time()
    
    response = llm_engine.create_chat_completion(
        messages=final_messages,
        temperature=temperature,
        max_tokens=max_tokens if max_tokens > 0 else None, # None para ilimitado
        stream=stream
    )
    
    gen_time = time.time() - gen_start
    print(f"✅ Geração Llama.cpp concluída em {gen_time:.2f}s")
    
    if stream:
        def stream_generator():
            for chunk in response:
                yield chunk
        return stream_generator()
    else:
        # Ferramentas não são suportadas em modo não-streaming com esta implementação
        return response