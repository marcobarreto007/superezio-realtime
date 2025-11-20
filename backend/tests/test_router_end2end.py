"""
Teste End-to-End do MoE Router
Valida todo o pipeline: Router → LoRA → RAG → Inferência
"""

import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from middleware.router_moe import infer_expert, get_expert_info
from middleware.rag_selector import get_rag_namespace
from middleware.lora_selector import select_lora
from rag.persistentRAG import PersistentRAG


def test_moe_pipeline():
    """Testa pipeline completo do MoE Router"""
    
    print("\n" + "="*80)
    print("🧪 TESTE END-TO-END - MOE ROUTER")
    print("="*80)
    
    # Casos de teste
    test_cases = [
        {
            "query": "Quem é a Ana Paula?",
            "expected_expert": "familia",
            "expected_lora": "familia",
            "expected_rag": "familia"
        },
        {
            "query": "Como faço minha declaração de ICMS?",
            "expected_expert": "contabilidade",
            "expected_lora": "contabilidade",
            "expected_rag": "contabilidade"
        },
        {
            "query": "Como funciona o sistema MIovision?",
            "expected_expert": "trafego",
            "expected_lora": "trafego",
            "expected_rag": "trafego"
        },
        {
            "query": "Estou me sentindo ansioso com o trabalho",
            "expected_expert": "pessoal",
            "expected_lora": None,
            "expected_rag": "vida_pessoal"
        },
        {
            "query": "Qual é a capital da França?",
            "expected_expert": "geral",
            "expected_lora": None,
            "expected_rag": None
        }
    ]
    
    passed = 0
    failed = 0
    
    for idx, case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"📝 TESTE {idx}: {case['query']}")
        print(f"{'─'*80}")
        
        # 1. Router detecta especialista
        expert = infer_expert(case['query'])
        expert_info = get_expert_info(expert)
        
        # 2. Seleciona LoRA
        lora = select_lora(expert)
        
        # 3. Seleciona namespace RAG
        rag_namespace = get_rag_namespace(expert)
        
        # Validação
        test_passed = True
        
        if expert != case['expected_expert']:
            print(f"❌ Expert: {expert} (esperado: {case['expected_expert']})")
            test_passed = False
        else:
            print(f"✅ Expert: {expert}")
        
        if lora != case['expected_lora']:
            print(f"❌ LoRA: {lora} (esperado: {case['expected_lora']})")
            test_passed = False
        else:
            print(f"✅ LoRA: {lora or 'Base Model'}")
        
        if rag_namespace != case['expected_rag']:
            print(f"❌ RAG: {rag_namespace} (esperado: {case['expected_rag']})")
            test_passed = False
        else:
            print(f"✅ RAG: {rag_namespace or 'None'}")
        
        # Info adicional
        print(f"\n📊 Info do Expert:")
        print(f"   Nome: {expert_info['name']}")
        print(f"   Descrição: {expert_info['description']}")
        
        if test_passed:
            passed += 1
            print(f"\n✅ TESTE {idx} PASSOU")
        else:
            failed += 1
            print(f"\n❌ TESTE {idx} FALHOU")
    
    # Resumo
    print("\n" + "="*80)
    print(f"📊 RESUMO DOS TESTES")
    print("="*80)
    print(f"✅ Passaram: {passed}/{len(test_cases)}")
    print(f"❌ Falharam: {failed}/{len(test_cases)}")
    
    accuracy = (passed / len(test_cases)) * 100
    print(f"🎯 Acurácia: {accuracy:.1f}%")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️  {failed} teste(s) falharam")
    
    print("="*80 + "\n")
    
    return failed == 0


def test_rag_integration():
    """Testa integração com RAG"""
    
    print("\n" + "="*80)
    print("🧪 TESTE RAG INTEGRATION")
    print("="*80)
    
    # Criar instância RAG de teste
    rag = PersistentRAG("data/rag_test")
    
    # Adicionar dados de teste
    print("\n📝 Adicionando dados de teste...")
    rag.add("familia", "Ana Paula é a mãe do Rapha", ["ana", "familia"])
    rag.add("familia", "Rapha estuda na UdeM em Montreal", ["rapha", "educacao"])
    rag.add("contabilidade", "ICMS é um imposto estadual brasileiro", ["icms", "impostos"])
    rag.add("trafego", "MIovision usa câmeras para detectar veículos", ["miovision", "camera"])
    
    # Testar buscas
    test_queries = [
        ("familia", "Quem é a Ana Paula?", 1),
        ("familia", "Onde o Rapha estuda?", 1),
        ("contabilidade", "O que é ICMS?", 1),
        ("trafego", "Como funciona MIovision?", 1)
    ]
    
    passed = 0
    
    for namespace, query, expected_min in test_queries:
        print(f"\n🔍 Buscando em '{namespace}': {query}")
        results = rag.search(namespace, query, limit=3)
        
        if len(results) >= expected_min:
            print(f"✅ Encontrou {len(results)} resultado(s)")
            for r in results[:2]:
                print(f"   - {r['text'][:60]}... (relevância: {r.get('relevance', 0):.2f})")
            passed += 1
        else:
            print(f"❌ Esperava pelo menos {expected_min}, encontrou {len(results)}")
    
    accuracy = (passed / len(test_queries)) * 100
    print(f"\n📊 Acurácia RAG: {accuracy:.1f}%")
    print("="*80 + "\n")
    
    return passed == len(test_queries)


def test_context_building():
    """Testa construção de contexto RAG"""
    
    print("\n" + "="*80)
    print("🧪 TESTE CONTEXT BUILDING")
    print("="*80)
    
    rag = PersistentRAG("data/rag_test")
    
    # Testar build_context
    query = "Quem é o Rapha?"
    context = rag.build_context("familia", query, limit=2)
    
    print(f"\n📋 Contexto gerado para: '{query}'")
    print(f"{'─'*80}")
    print(context)
    print(f"{'─'*80}")
    
    # Validar formato
    has_header = "[RAG CONTEXT" in context
    has_footer = "[FIM DO CONTEXTO RAG]" in context
    has_content = len(context) > 50
    
    if has_header and has_footer and has_content:
        print("\n✅ Contexto formatado corretamente")
        return True
    else:
        print("\n❌ Contexto com formato inválido")
        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 40)
    print("MOE ROUTER - TESTE COMPLETO END-TO-END")
    print("🚀" * 40)
    
    results = []
    
    # 1. Teste do pipeline MoE
    results.append(("MoE Pipeline", test_moe_pipeline()))
    
    # 2. Teste de integração RAG
    results.append(("RAG Integration", test_rag_integration()))
    
    # 3. Teste de construção de contexto
    results.append(("Context Building", test_context_building()))
    
    # Resumo final
    print("\n" + "="*80)
    print("📊 RESUMO FINAL")
    print("="*80)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n" + "🎉" * 40)
        print("TODOS OS TESTES PASSARAM!")
        print("MoE ROUTER √ Pronto para guerra.")
        print("🎉" * 40 + "\n")
        sys.exit(0)
    else:
        print("\n⚠️  Alguns testes falharam")
        sys.exit(1)
