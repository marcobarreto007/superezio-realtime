"""
Hugging Face Inference Backend para SuperEzio
100% LOCAL - Modelo já baixado no disco, sem dependência do HF
Usa GPU NVIDIA (CUDA) para inferência local

CAMINHOS RELATIVOS - Funciona em qualquer máquina
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Generator, Union
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    BitsAndBytesConfig,
    TextIteratorStreamer,
    PreTrainedModel,
    PreTrainedTokenizer,
)
from threading import Thread
import queue
import torch
from peft.peft_model import PeftModel

# Fix encoding para Windows (removido - causa problemas com venv)
# O Python 3.12+ já lida bem com UTF-8 no Windows
# Se precisar, configure PYTHONIOENCODING=utf-8 no ambiente

# ✅ FIX: Usar HF_HOME ao invés de TRANSFORMERS_CACHE (deprecated)
if not os.getenv("HF_HOME"):
    os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")

# Configuração - MODELO 100% LOCAL
# Caminho relativo: backend/ -> raiz do projeto -> models/
BACKEND_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent.resolve()
LOCAL_MODEL_DIR = PROJECT_ROOT / "models" / "qwen2.5-7b-instruct"

# 🔥 MULTI-LORA: Suporte para múltiplos adaptadores
LORA_PERSONALITY_DIR = PROJECT_ROOT / "models" / "lora_personality"  # 🎭 Personalidade
LORA_ACCOUNTING_DIR = PROJECT_ROOT / "models" / "lora_accounting"    # 🇨🇦 Contabilidade
LORA_LEGACY_DIR = PROJECT_ROOT / "models" / "lora_superezio"          # Legacy (antigo)

# Permitir override via env
env_path = os.getenv("LOCAL_MODEL_PATH")
if env_path:
    LOCAL_MODEL_DIR = Path(env_path).resolve()

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
tokenizer: Optional[PreTrainedTokenizer] = None
model: Optional[Union[PreTrainedModel, PeftModel]] = None
generator: Optional[Any] = None  # pipeline type é complexo, usar Any

def load_model():
    """
    Carrega o modelo LOCAL na GPU.
    Se um adaptador LoRA treinado for encontrado, ele será aplicado sobre o modelo base.
    """
    global tokenizer, model, generator
    
    if model is not None:
        return  # Já carregado

    try:
        import torch  # Garantir torch disponível localmente
        use_lora = LORA_PERSONALITY_DIR.exists() or LORA_ACCOUNTING_DIR.exists() or LORA_LEGACY_DIR.exists()

        # Carregar tokenizer (simples, sem LoRA)
        print(f"📂 Carregando tokenizer de {LOCAL_MODEL_DIR}...")
        tokenizer = AutoTokenizer.from_pretrained(
            str(LOCAL_MODEL_DIR),
            trust_remote_code=True,
            local_files_only=True,
        )
        tokenizer.pad_token = tokenizer.eos_token  # type: ignore

        if use_lora:
            # Detectar quais LoRAs existem
            has_personality = LORA_PERSONALITY_DIR.exists()
            has_accounting = LORA_ACCOUNTING_DIR.exists()
            has_legacy = LORA_LEGACY_DIR.exists()
            
            print("="*50)
            print("🚀 MULTI-LORA DETECTADO! 🚀")
            if has_personality:
                print(f"   🎭 Personalidade: {LORA_PERSONALITY_DIR}")
            if has_accounting:
                print(f"   🇨🇦 Contabilidade: {LORA_ACCOUNTING_DIR}")
            if has_legacy:
                print(f"   📦 Legacy: {LORA_LEGACY_DIR}")
            print("="*50)

            # Configuração de quantização para carregar o modelo base em 4-bit
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )

            # Carregar o modelo base já quantizado
            print(f"📂 Carregando modelo base ({LOCAL_MODEL_DIR}) em 4-bit...")
            model = AutoModelForCausalLM.from_pretrained(
                str(LOCAL_MODEL_DIR),
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                local_files_only=True,
            )
            
            # 🔥 CARREGAR MÚLTIPLOS LoRAs
            print("🚀 Aplicando adaptadores LoRA...")
            
            # Prioridade: Personality + Accounting > Legacy
            if has_personality and has_accounting:
                # Carregar ambos LoRAs
                model = PeftModel.from_pretrained(model, str(LORA_PERSONALITY_DIR), adapter_name="personality")
                model.load_adapter(str(LORA_ACCOUNTING_DIR), adapter_name="accounting")
                # Ativar ambos usando enable_adapter_layers()
                model.enable_adapter_layers()
                print("✅ Multi-LoRA aplicado: 🎭 Personalidade + 🇨🇦 Contabilidade!")
                print("🎭 Personalidade SuperEzio ATIVADA!")
                print("🇨🇦 Expert em Contabilidade Canadense ATIVADO!")
                print("ℹ️  Ambos adaptadores serão mesclados nas respostas")
            elif has_personality:
                model = PeftModel.from_pretrained(model, str(LORA_PERSONALITY_DIR), is_trainable=False)
                print("✅ LoRA de Personalidade aplicado!")
                print("🎭 Personalidade SuperEzio ATIVADA!")
            elif has_accounting:
                model = PeftModel.from_pretrained(model, str(LORA_ACCOUNTING_DIR), is_trainable=False)
                print("✅ LoRA de Contabilidade aplicado!")
                print("🇨🇦 Expert em Contabilidade Canadense ATIVADO!")
            elif has_legacy:
                model = PeftModel.from_pretrained(model, str(LORA_LEGACY_DIR), is_trainable=False)
                print("✅ LoRA Legacy aplicado!")
                print("🎭 Personalidade SuperEzio ATIVADA!")

        else:
            print("="*50)
            print("🚀 Adaptador LoRA não encontrado. Carregando modelo base padrão. 🚀")
            print(f"(Para treinar um, execute: python scripts/train_lora.py)")
            print("="*50)
            
            # Configuração quantização 4-bit (reduz VRAM, aumenta velocidade)
            print("🔧 Configurando quantização 4-bit...")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            
            # Carregar modelo do disco LOCAL com quantização 4-bit
            print(f"📂 Carregando modelo de {LOCAL_MODEL_DIR}...")
            print("⚡ Modo: 4-bit quantized (NF4)")
            model = AutoModelForCausalLM.from_pretrained(
                str(LOCAL_MODEL_DIR),
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                local_files_only=True,
            )
            
            print("✅ Modelo carregado com quantização 4-bit")

        # Otimizações CUDA
        if DEVICE == "cuda":
            print("🔧 Aplicando otimizações CUDA...")
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # BetterTransformer para 30-50% mais rápido
            try:
                from optimum.bettertransformer import BetterTransformer
                model = BetterTransformer.transform(model)  # type: ignore
                print("✅ BetterTransformer ativado (30-50% mais rápido)")
            except Exception as e:
                print(f"⚠️  BetterTransformer não disponível: {e}")
            
            print("✅ Otimizações CUDA ativadas")
            
            # NOTA: torch.compile desabilitado pois quebra o pipeline do HuggingFace
            # O modelo compila mas vira OptimizedModule que não é suportado pelo pipeline
            # Se quiser usar torch.compile, precisa usar model.generate() diretamente
        
        # Criar pipeline de geração de texto (não funciona com torch.compile)
        generator = pipeline(  # type: ignore[call-overload]
            "text-generation",
            model=model,  # type: ignore[arg-type]
            tokenizer=tokenizer,
        )
        
        vram_used = torch.cuda.memory_allocated(0) / 1024**3 if DEVICE == "cuda" else 0
        vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3) if DEVICE == "cuda" else 0
        print(f"✅ Modelo carregado 100% LOCAL!")
        print(f"💾 VRAM: {vram_used:.2f}GB / {vram_total:.2f}GB")
        print(f"🌐 Status: OFFLINE (sem dependência do Hugging Face)")
        
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        import traceback
        traceback.print_exc()
        if "local_files_only" in str(e) or "not found" in str(e).lower():
            print(f"\n💡 Dica: Execute primeiro:")
            print(f"   python scripts/download_model.py")
        raise


# SYSTEM_PROMPT - Minimalista (personalidade já está no LoRA)
SYSTEM_PROMPT = """Você é SuperEzio. Responda em português brasileiro de forma direta e objetiva.

**FERRAMENTAS DISPONÍVEIS:**
Você tem acesso a ferramentas para ajudar o usuário:
- **Arquivos:** read_file, write_file, delete_file, get_file_info
- **Diretórios:** list_directory, create_directory, search_files  
- **Dados:** create_table
- **Email:** read_emails, search_emails, get_unread_count

**QUANDO USAR FERRAMENTAS:**
- Usuário pede para ler/criar/modificar arquivos → USE read_file, write_file
- Usuário quer listar pastas/arquivos → USE list_directory, search_files
- Usuário quer ver emails → USE read_emails, search_emails
- Usuário pede para organizar dados → USE create_table

**IMPORTANTE:**
- Se o usuário pedir algo que REQUER uma ferramenta, SEMPRE use ela
- NÃO invente conteúdo de arquivos - leia primeiro com read_file
- NÃO diga "eu não posso" se existe uma ferramenta para isso
- Seja PROATIVO: se precisa de info de um arquivo, leia ele
- Use gírias: "cara", "mano", "beleza?", "tá ligado?", "saca?"
- Seja EXPRESSIVO: use emoji quando apropriado 😎🚀💪

SAÚDE (SENSÍVEL - SÓ ORGANIZAR QUANDO SOLICITADO):
- TDAH: Preferiria Ritalina, usa Vyvanse 40mg atualmente
- Ansiedade: Sono ruim, sertralina
- Hipertensão: Ramipril e metoprolol
- Cardíaco: 4 ablações por arritmia, estável
- Sono: Ronco, CPAP
- Peso: ~134 kg, meta perda peso/energia, brain fog
- REGRA: Não prescrever, não empurrar alertas; só organizar quando pedir

OBJETIVOS EM ANDAMENTO:
- SuperEzio: personalidade própria, baixa latência
- TrafficAI: competir com Miovision-like, ROI ótimo
- Xubudget: consolidar uso familiar
- Trazer Matheus do Brasil para Canadá (apoio logístico)

DATAS-CHAVE:
- 2025-10-09: Saída Hayes/Instech
- 2025: Falecimento Inesita e José Carlos
- Diário 20:00: Chamada AP com Matheus

DIRETRIZES:
- Sempre entregar pipeline completo (pasta → arquivo → comando)
- Sugerir modelos pequenos em paralelo + orquestrador
- Deixar claro custo/benefício e execução em 1 comando
- Em temas familiares, manter calor e objetividade
- Em saúde: somente organizar quando solicitado, sem protocolos não solicitados"""

def format_messages(messages: List[Dict[str, str]]) -> str:
    """Formata mensagens para o formato do modelo"""
    # Garantir que há uma mensagem system com o SYSTEM_PROMPT
    has_system = any(msg.get("role") == "system" for msg in messages)
    if not has_system:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    
    # Usar chat template do modelo
    if tokenizer and hasattr(tokenizer, 'apply_chat_template'):
        result = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        return str(result)  # Garantir que retorna string
    
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

def generate_stream(
    messages: List[Dict[str, str]],
    max_new_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.9,
    top_k: int = 40,
    repetition_penalty: float = 1.1,
    tools: Optional[List[Dict]] = None
) -> Generator[str, None, None]:
    """
    Stream de geração token por token.
    Yields: chunks de texto conforme modelo gera.
    """
    global model, tokenizer
    
    if model is None or tokenizer is None:
        load_model()
    
    # Type guard: garantir que model e tokenizer foram carregados
    if model is None or tokenizer is None:
        yield "[ERRO: Modelo não carregado]"
        return
    
    try:
        # Formatar prompt
        prompt = format_messages(messages)
        
        if tools:
            tools_json = json.dumps(tools, indent=2)
            prompt += f"\n\n[AVAILABLE_TOOLS]\n{tools_json}\n\n"
            prompt += "Você pode chamar essas ferramentas quando necessário. Responda em JSON com 'content' e 'tool_calls'.\n"
        
        # Tokenizar
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048,  # Reduzido de 4096 para 2048 (mais rápido)
            padding=False,  # Sem padding desnecessário
        )
        
        # Mover para device correto
        if DEVICE == "cuda":
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        # Setup streamer
        streamer = TextIteratorStreamer(
            tokenizer,  # type: ignore[arg-type]
            skip_prompt=True,
            skip_special_tokens=True,
            timeout=10.0
        )
        
        generation_kwargs = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "do_sample": temperature > 0,
            "num_beams": 1,
            "streamer": streamer,
            "pad_token_id": tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
            "eos_token_id": tokenizer.eos_token_id,
            "use_cache": True,  # KV cache para performance
            "num_return_sequences": 1,
        }
        
        # Thread para geração não-bloqueante
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # Yield tokens conforme chegam
        for text_chunk in streamer:
            if text_chunk:
                yield text_chunk
        
        thread.join()
        
    except Exception as e:
        print(f"❌ Erro no streaming: {e}")
        import traceback
        traceback.print_exc()
        yield f"[ERRO: {str(e)}]"
    finally:
        # Limpar cache CUDA se necessário
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def chat_completion(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
    stream: bool = False
) -> Union[Dict[str, Any], Generator[str, None, None]]:
    """
    Chat completion com suporte a streaming.
    
    Args:
        messages: Lista de mensagens (formato OpenAI)
        tools: Lista de tools disponíveis (function calling)
        temperature: Temperatura para geração
        max_tokens: Máximo de tokens a gerar
        stream: True = retorna generator, False = string completa
    
    Returns:
        Se stream=True: Generator[str, None, None]
        Se stream=False: Dict com 'content' e opcionalmente 'tool_calls'
    """
    if stream:
        return generate_stream(
            messages=messages,
            max_new_tokens=min(max_tokens, 512),
            temperature=temperature,
            tools=tools
        )
    
    import time
    global generator, tokenizer
    
    if generator is None:
        load_model()
    
    # Type guard: garantir que generator e tokenizer foram carregados
    if generator is None or tokenizer is None:
        return {
            "error": "Modelo não carregado",
            "content": "Erro: Modelo não está carregado. Reinicie o servidor."
        }
    
    # Log da pergunta do usuário
    if messages:
        last_message = messages[-1].get('content', '')
        print(f"🗣️  PERGUNTA: \"{last_message[:200]}{'...' if len(last_message) > 200 else ''}\"")

    print(f"🔧 Formatando prompt...")
    start_format = time.time()
    
    # Formatar prompt
    try:
        prompt = format_messages(messages)
        format_time = time.time() - start_format
        print(f"✅ Prompt formatado em {format_time:.2f}s")
        print(f"📏 Tamanho do prompt: {len(prompt)} caracteres")
        if len(prompt) > 10000:
            print(f"⚠️  AVISO: Prompt muito longo ({len(prompt)} chars), pode demorar mais")
    except Exception as format_error:
        print(f"❌ Erro ao formatar prompt: {format_error}")
        raise
    
    # Se há tools, adicionar ao prompt (function calling)
    if tools:
        tools_json = json.dumps(tools, indent=2)
        prompt += f"\n\n[AVAILABLE_TOOLS]\n{tools_json}\n\n"
        prompt += "Você pode chamar essas ferramentas quando necessário. Responda em JSON com 'content' e 'tool_calls'.\n"
        print(f"🔧 Tools adicionadas ao prompt")
    
    try:
        # NOTA: max_tokens já vem limitado a 512 pelo api.py
        # Não precisa mais de verificação redundante aqui
        print(f"🚀 Gerando com max_new_tokens={max_tokens}, temperature={temperature}")
        print(f"⏱️  Iniciando geração às {time.strftime('%H:%M:%S')}...")
        print(f"📊 Prompt length: {len(prompt)} chars")

        gen_start = time.time()
        
        # Verificar se modelo está carregado
        if generator is None:
            print("❌ ERRO: Generator não está inicializado!")
            return {
                "error": "Modelo não está carregado",
                "content": "Erro: Modelo não está carregado. Reinicie o servidor FastAPI."
            }

        # Geração com parâmetros otimizados
        try:
            print(f"🔄 Chamando generator.generate()...")
            gen_call_start = time.time()
            outputs = generator(
                prompt,
                max_new_tokens=max_tokens,  # Já limitado a 512 pelo api.py
                temperature=temperature,
                top_p=0.9,   # Reduzido para acelerar
                top_k=40,    # Reduzido para acelerar
                do_sample=True,
                num_beams=1,  # Sem beam search - mais rápido
                repetition_penalty=1.1,  # Evita repetição
                return_full_text=False,
                pad_token_id=tokenizer.eos_token_id,  # Evitar warnings
            )
            gen_call_time = time.time() - gen_call_start
            print(f"✅ Generator retornou em {gen_call_time:.2f}s")
        except Exception as gen_error:
            gen_time = time.time() - gen_start
            print(f"❌ Erro durante geração após {gen_time:.2f}s: {gen_error}")
            import traceback
            traceback.print_exc()
            raise
        
        gen_time = time.time() - gen_start
        print(f"✅ Geração concluída em {gen_time:.2f}s")
        
        # Verificar se a resposta está vazia ou muito curta (pode indicar problema)
        if not outputs or len(outputs) == 0:
            print(f"⚠️  AVISO: Geração retornou vazio!")
            return {
                "error": "Geração retornou resposta vazia",
                "content": "Desculpe, não consegui gerar uma resposta. Tente novamente."
            }
        
        response_text = outputs[0]["generated_text"]
        
        # Log da resposta final
        print(f"💡 RESPOSTA: \"{response_text[:200].strip()}{'...' if len(response_text) > 200 else ''}\"")
        
        # REM: logar "resposta bruta" (primeiros 500 chars)
        try:
            preview = response_text[:500]
            print(f"📝 Resposta bruta do modelo ({len(response_text)} chars):")
            print(f"{'─'*60}")
            print(f"{preview}{'...' if len(response_text) > 500 else ''}")
            print(f"{'─'*60}")
        except Exception as e:
            print(f"⚠️ Log preview falhou: {e}")
        
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
    
    result = chat_completion(test_messages, stream=False)  # Especificar stream=False
    print("\n📝 Resposta:")
    if isinstance(result, dict):
        print(result.get("content", "Erro: sem conteúdo"))
    else:
        print("Erro: resultado não é dict")

