"""
Teste das 3 Correções Solicitadas
===================================
1. Ana Paula é a mais velha das 3 irmãs
2. Informações completas dos Edmonton Oilers (time do Rapha)
3. Opiniões sobre concorrentes IA (ChatGPT, Grok, Claude)
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
            timeout=60  # Aumentado para 60 segundos
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
    print("🧪 TESTE DAS 3 CORREÇÕES SOLICITADAS")
    print("="*80)
    
    # Aguarda backend inicializar
    print("\n⏳ Aguardando backend inicializar (15 segundos)...")
    time.sleep(15)
    
    # CORREÇÃO 1: Ana Paula é a mais velha
    test_question(
        "Quem é a irmã mais velha entre Ana Paula, Tatiana e Karina?",
        "CORREÇÃO 1 - Hierarquia de idade das irmãs"
    )
    
    time.sleep(2)
    
    # CORREÇÃO 2: Informações dos Oilers
    test_question(
        "Me fale sobre o time Edmonton Oilers, o time favorito do Rapha.",
        "CORREÇÃO 2 - Edmonton Oilers (time do Rapha)"
    )
    
    time.sleep(2)
    
    # CORREÇÃO 3: Opiniões sobre concorrentes IA
    test_question(
        "O que você acha do ChatGPT, do Grok e do Claude? Como você se compara a eles?",
        "CORREÇÃO 3 - Opiniões sobre concorrentes IA"
    )
    
    print("\n" + "="*80)
    print("✅ TESTE COMPLETO!")
    print("="*80)

if __name__ == "__main__":
    main()
