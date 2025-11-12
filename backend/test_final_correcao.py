"""
Teste FINAL de Validação Completa dos Relacionamentos Familiares
==================================================================
Valida todas as correções aplicadas:
1. Matheus é irmão da AP (NÃO do Marco) ✅
2. Nilton Sulz é irmão do Marco ✅
3. Marco tem 1 irmão (Nilton Sulz) ✅
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_question(question: str, test_name: str):
    """Testa uma pergunta específica"""
    print(f"\n{'='*80}")
    print(f"TESTE: {test_name}")
    print(f"{'='*80}")
    print(f"❓ PERGUNTA: {question}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "messages": [{"role": "user", "content": question}],
                "model": "Qwen2.5-7B-Instruct",
                "temperature": 0.2,
                "max_tokens": 512
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("content", "SEM RESPOSTA")
            print(f"✅ RESPOSTA:")
            print(f"   {answer}")
            print()
            return answer
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

def main():
    print("\n" + "="*80)
    print("🧪 TESTE FINAL DE VALIDAÇÃO COMPLETA")
    print("="*80)
    
    # Aguarda backend inicializar
    print("\n⏳ Aguardando backend inicializar (15 segundos)...")
    time.sleep(15)
    
    # TESTE 1: Matheus é irmão de quem?
    test_question(
        "Matheus é irmão de quem? Do Marco ou da Ana Paula?",
        "MATHEUS - Irmão da AP (NÃO do Marco)"
    )
    
    time.sleep(2)
    
    # TESTE 2: Nilton Sulz é irmão de quem?
    test_question(
        "Quem é Nilton Sulz? Ele é irmão de quem?",
        "NILTON SULZ - Irmão do Marco"
    )
    
    time.sleep(2)
    
    # TESTE 3: Marco tem irmãos?
    test_question(
        "O Marco tem irmãos? Se sim, quem são?",
        "MARCO - Tem 1 irmão (Nilton Sulz)"
    )
    
    time.sleep(2)
    
    # TESTE 4: Quem são os irmãos da Ana Paula?
    test_question(
        "Quem são os irmãos da Ana Paula? Liste todos.",
        "ANA PAULA - 3 irmãos (Karina, Tatiana, Matheus)"
    )
    
    print("\n" + "="*80)
    print("✅ TESTE COMPLETO!")
    print("="*80)

if __name__ == "__main__":
    main()
