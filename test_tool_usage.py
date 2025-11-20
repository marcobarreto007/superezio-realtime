"""Teste específico: verificar se modelo REALMENTE executa ferramentas"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*70)
print("🔍 TESTE: Modelo usa ferramentas OU apenas simula?")
print("="*70)

tools = [{
    "name": "list_directory",
    "description": "Lista arquivos de um diretório",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho do diretório"}
        },
        "required": ["path"]
    }
}]

payload = {
    "messages": [
        {"role": "user", "content": "Liste TODOS os arquivos do meu Desktop. Use a ferramenta list_directory com path='Desktop'."}
    ],
    "tools": tools,
    "temperature": 0.1,  # Baixa temperatura para ser mais determinístico
    "max_tokens": 1024
}

print("\n📤 Enviando requisição com ferramenta list_directory...")
print(f"   Pergunta: {payload['messages'][0]['content']}")

try:
    resp = requests.post(f"{BASE_URL}/chat", json=payload, timeout=90)
    result = resp.json()
    
    print("\n📥 Resposta recebida:")
    print(f"   Status Code: {resp.status_code}")
    
    # Verificar se tem tool_calls na resposta
    if "tool_calls" in result and result["tool_calls"]:
        print(f"\n✅ TOOL CALLS DETECTADOS!")
        print(f"   Quantidade: {len(result['tool_calls'])}")
        for i, tc in enumerate(result['tool_calls'], 1):
            print(f"   {i}. {tc.get('name', 'unknown')} - Params: {tc.get('parameters', {})}")
        
        # Verificar se tem tool_results (ferramentas executadas)
        if "tool_results" in result and result["tool_results"]:
            print(f"\n✅ FERRAMENTAS EXECUTADAS!")
            print(f"   Resultados: {len(result['tool_results'])}")
            for i, tr in enumerate(result['tool_results'], 1):
                tool_name = tr.get('tool', 'unknown')
                success = tr.get('result', {}).get('success', False)
                print(f"   {i}. {tool_name} - {'✅ Sucesso' if success else '❌ Falhou'}")
                
                # Se list_directory teve sucesso, mostrar quantos itens retornou
                if tool_name == "list_directory" and success:
                    items = tr.get('result', {}).get('result', {}).get('items', [])
                    print(f"      📁 {len(items)} arquivos/pastas encontrados")
        else:
            print(f"\n⚠️  TOOL CALLS DETECTADOS MAS NÃO EXECUTADOS")
            print(f"   O modelo sugeriu ferramentas mas não há tool_results")
    else:
        print(f"\n❌ NENHUM TOOL CALL DETECTADO")
        print(f"   O modelo NÃO tentou usar ferramentas")
    
    # Mostrar conteúdo da resposta
    print(f"\n📝 Conteúdo da resposta:")
    content = result.get('content', '')
    print(f"   {content[:300]}{'...' if len(content) > 300 else ''}")
    
    # Verificar se resposta tem JSON cru (sinal de que modelo está retornando formato errado)
    if '{"content":' in content or '"tool_calls"' in content:
        print(f"\n⚠️  AVISO: Resposta contém JSON cru!")
        print(f"   O modelo está retornando JSON ao invés de usar o formato correto")
    
    # CONCLUSÃO
    print("\n" + "="*70)
    has_tool_calls = "tool_calls" in result and result["tool_calls"]
    has_tool_results = "tool_results" in result and result["tool_results"]
    
    if has_tool_calls and has_tool_results:
        print("✅ CONCLUSÃO: Modelo USA ferramentas corretamente!")
    elif has_tool_calls and not has_tool_results:
        print("⚠️  CONCLUSÃO: Modelo detecta ferramentas mas não executa")
    else:
        print("❌ CONCLUSÃO: Modelo NÃO usa ferramentas (apenas simula)")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
