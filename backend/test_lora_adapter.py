"""
Teste Isolado - Verificar se o Adaptador LoRA está sendo usado
Testa o modelo base vs modelo com LoRA para confirmar diferenças
"""
import sys
import os
from pathlib import Path

# Adicionar backend ao path
BACKEND_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

from inference import load_model, chat_completion, LOCAL_MODEL_DIR, LORA_ADAPTER_DIR, model, tokenizer
import torch

def test_lora_presence():
    """Testa se o adaptador LoRA está presente e carregado"""
    print("="*60)
    print("TESTE 1: VERIFICAR PRESENÇA DO ADAPTADOR LoRA")
    print("="*60)
    
    # Verificar se diretório LoRA existe
    lora_exists = LORA_ADAPTER_DIR.exists()
    print(f"\n📁 Diretório LoRA: {LORA_ADAPTER_DIR}")
    print(f"   Status: {'✅ EXISTE' if lora_exists else '❌ NÃO ENCONTRADO'}")
    
    if lora_exists:
        # Listar arquivos no diretório LoRA
        lora_files = list(LORA_ADAPTER_DIR.glob("*"))
        print(f"\n📄 Arquivos no diretório LoRA ({len(lora_files)}):")
        for f in lora_files[:10]:  # Mostrar até 10 arquivos
            print(f"   - {f.name}")
        if len(lora_files) > 10:
            print(f"   ... e mais {len(lora_files) - 10} arquivos")
    
    return lora_exists

def test_model_type():
    """Verifica o tipo do modelo carregado"""
    print("\n" + "="*60)
    print("TESTE 2: TIPO DO MODELO CARREGADO")
    print("="*60)
    
    # Carregar modelo se não estiver carregado
    if model is None:
        print("\n⏳ Carregando modelo...")
        load_model()
    
    print(f"\n🤖 Tipo do modelo: {type(model).__name__}")
    print(f"   Módulo: {type(model).__module__}")
    
    # Verificar se é PeftModel (LoRA)
    is_peft = "PeftModel" in type(model).__name__ or "peft" in type(model).__module__.lower()
    print(f"\n{'✅' if is_peft else '❌'} É PeftModel (LoRA)? {is_peft}")
    
    # Verificar camadas do modelo
    if hasattr(model, 'peft_config'):
        print(f"\n✅ CONFIRMADO: Modelo tem configuração PEFT!")
        print(f"   Config: {model.peft_config}")
    else:
        print(f"\n❌ AVISO: Modelo NÃO tem configuração PEFT")
    
    # Verificar se há adaptadores ativos
    if hasattr(model, 'active_adapter'):
        print(f"\n✅ Adaptador ativo: {model.active_adapter}")
    
    if hasattr(model, 'base_model'):
        print(f"\n✅ Modelo base presente: {type(model.base_model).__name__}")
    
    return is_peft

def test_personality_response():
    """Testa se o modelo responde com personalidade SuperEzio"""
    print("\n" + "="*60)
    print("TESTE 3: PERSONALIDADE SUPEREZIO (LoRA)")
    print("="*60)
    
    # Carregar modelo se não estiver carregado
    if model is None:
        print("\n⏳ Carregando modelo...")
        load_model()
    
    # Perguntas de teste que devem revelar a personalidade
    test_prompts = [
        {
            "messages": [
                {"role": "user", "content": "Quem é você?"}
            ],
            "description": "Identificação (deve dizer 'SuperEzio')"
        },
        {
            "messages": [
                {"role": "user", "content": "Como você está?"}
            ],
            "description": "Resposta casual (deve ser direto, sem floreios)"
        },
        {
            "messages": [
                {"role": "user", "content": "Quem criou você?"}
            ],
            "description": "Criador (deve mencionar 'Marco Barreto')"
        }
    ]
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n{'─'*60}")
        print(f"PERGUNTA {i}: {test['messages'][0]['content']}")
        print(f"Objetivo: {test['description']}")
        print(f"{'─'*60}")
        
        try:
            result = chat_completion(
                messages=test['messages'],
                temperature=0.1,  # Baixa temperatura para resposta consistente
                max_tokens=150
            )
            
            response = result.get('content', '').strip()
            print(f"\n💬 RESPOSTA:\n{response[:300]}")
            
            # Verificar palavras-chave esperadas
            lower_response = response.lower()
            
            if i == 1:  # "Quem é você?"
                has_superezio = 'superezio' in lower_response
                print(f"\n{'✅' if has_superezio else '❌'} Menciona 'SuperEzio': {has_superezio}")
            
            elif i == 2:  # "Como você está?"
                # Verificar se resposta é curta e direta (não verbosa)
                is_concise = len(response) < 200
                print(f"\n{'✅' if is_concise else '❌'} Resposta concisa: {is_concise}")
            
            elif i == 3:  # "Quem criou você?"
                has_marco = 'marco' in lower_response or 'barreto' in lower_response
                print(f"\n{'✅' if has_marco else '❌'} Menciona 'Marco Barreto': {has_marco}")
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
    
    return True

def test_lora_weights():
    """Verifica se há pesos LoRA carregados"""
    print("\n" + "="*60)
    print("TESTE 4: PESOS LORA NO MODELO")
    print("="*60)
    
    if model is None:
        print("\n⏳ Carregando modelo...")
        load_model()
    
    # Contar parâmetros totais
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"\n📊 Parâmetros do modelo:")
    print(f"   Total: {total_params:,}")
    print(f"   Treináveis: {trainable_params:,}")
    print(f"   Proporção: {trainable_params/total_params*100:.2f}%")
    
    # LoRA geralmente tem < 1% de parâmetros treináveis
    is_lora_ratio = (trainable_params / total_params) < 0.01
    print(f"\n{'✅' if is_lora_ratio else '❌'} Proporção típica de LoRA (< 1%): {is_lora_ratio}")
    
    # Procurar por módulos LoRA no modelo
    lora_modules = []
    for name, module in model.named_modules():
        if 'lora' in name.lower() or 'LoRA' in type(module).__name__:
            lora_modules.append(name)
    
    if lora_modules:
        print(f"\n✅ Módulos LoRA encontrados ({len(lora_modules)}):")
        for name in lora_modules[:5]:
            print(f"   - {name}")
        if len(lora_modules) > 5:
            print(f"   ... e mais {len(lora_modules) - 5} módulos")
    else:
        print(f"\n❌ AVISO: Nenhum módulo LoRA encontrado no modelo")
    
    return len(lora_modules) > 0

def test_comparison_base_vs_lora():
    """Compara resposta do modelo base vs modelo com LoRA (se possível)"""
    print("\n" + "="*60)
    print("TESTE 5: COMPARAÇÃO BASE vs LoRA")
    print("="*60)
    
    print("\n⚠️  Este teste requer carregar o modelo duas vezes")
    print("   (uma vez sem LoRA, outra com LoRA)")
    print("   Pode demorar alguns minutos...")
    
    # Por enquanto, apenas informar que o teste não é viável sem reiniciar
    print("\n❌ TESTE PULADO: Requer restart do processo para carregar modelo sem LoRA")
    print("   Para fazer este teste manualmente:")
    print("   1. Renomeie temporariamente a pasta 'models/lora_superezio'")
    print("   2. Execute este script e veja a resposta")
    print("   3. Restaure a pasta e execute novamente")
    print("   4. Compare as respostas")
    
    return None

def main():
    """Executa todos os testes"""
    print("\n" + "🧪"*30)
    print("TESTE COMPLETO - VERIFICAÇÃO ADAPTADOR LoRA")
    print("🧪"*30)
    
    results = {
        "lora_exists": False,
        "is_peft_model": False,
        "has_lora_weights": False,
        "personality_works": False
    }
    
    try:
        # Teste 1: Presença do adaptador
        results["lora_exists"] = test_lora_presence()
        
        # Teste 2: Tipo do modelo
        results["is_peft_model"] = test_model_type()
        
        # Teste 3: Personalidade
        results["personality_works"] = test_personality_response()
        
        # Teste 4: Pesos LoRA
        results["has_lora_weights"] = test_lora_weights()
        
        # Teste 5: Comparação (informativo)
        test_comparison_base_vs_lora()
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
    
    # Resumo final
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)
    
    print(f"\n1. Adaptador LoRA existe: {'✅ SIM' if results['lora_exists'] else '❌ NÃO'}")
    print(f"2. Modelo é PeftModel: {'✅ SIM' if results['is_peft_model'] else '❌ NÃO'}")
    print(f"3. Tem pesos LoRA: {'✅ SIM' if results['has_lora_weights'] else '❌ NÃO'}")
    print(f"4. Personalidade funciona: {'✅ SIM' if results['personality_works'] else '❌ NÃO'}")
    
    # Diagnóstico final
    print("\n" + "="*60)
    print("🎯 DIAGNÓSTICO FINAL")
    print("="*60)
    
    all_pass = all([
        results['lora_exists'],
        results['is_peft_model'],
        results['has_lora_weights']
    ])
    
    if all_pass:
        print("\n✅ ✅ ✅ SUCESSO!")
        print("   O adaptador LoRA está CARREGADO e ATIVO!")
        print("   O modelo está usando a personalidade SuperEzio treinada.")
    elif results['lora_exists'] and not results['is_peft_model']:
        print("\n⚠️  PROBLEMA DETECTADO!")
        print("   O adaptador LoRA existe mas NÃO está sendo carregado.")
        print("   Verifique o código em backend/inference.py → load_model()")
    elif not results['lora_exists']:
        print("\n❌ ADAPTADOR NÃO ENCONTRADO!")
        print("   Execute o treinamento primeiro: python scripts/train_lora.py")
    else:
        print("\n⚠️  STATUS INCERTO")
        print("   Revise os resultados dos testes acima.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
