"""
Teste Completo do Sistema SuperEzio v2.1.0
Valida todas as melhorias implementadas
"""
import requests
import time
import json
from typing import Dict, Any, List
from datetime import datetime


BASE_URL = "http://localhost:8000"
TEST_RESULTS: List[Dict[str, Any]] = []


def log_test(name: str, status: str, details: str = "", duration: float = 0):
    """Log resultado do teste"""
    result = {
        "test": name,
        "status": status,
        "details": details,
        "duration": round(duration, 3),
        "timestamp": datetime.now().isoformat()
    }
    TEST_RESULTS.append(result)
    
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} [{status}] {name}")
    if details:
        print(f"   {details}")
    if duration > 0:
        print(f"   Tempo: {duration:.3f}s")
    print()


def test_health_check():
    """Teste 1: Health Check Básico"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Health Check Básico",
                "PASS",
                f"Status: {data.get('status')}, GPU: {data.get('gpu_available')}",
                duration
            )
            return True
        else:
            log_test("Health Check Básico", "FAIL", f"Status code: {response.status_code}", duration)
            return False
    except Exception as e:
        log_test("Health Check Básico", "FAIL", str(e), time.time() - start)
        return False


def test_health_detailed():
    """Teste 2: Health Check Detalhado"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health/detailed", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            components = data.get("components", {})
            
            log_test(
                "Health Check Detalhado",
                "PASS",
                f"Status geral: {status}, Componentes: {len(components)}",
                duration
            )
            return True
        else:
            log_test("Health Check Detalhado", "FAIL", f"Status code: {response.status_code}", duration)
            return False
    except Exception as e:
        log_test("Health Check Detalhado", "FAIL", str(e), time.time() - start)
        return False


def test_metrics():
    """Teste 3: Endpoint de Métricas"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            counters = data.get("counters", {})
            histograms = data.get("histograms", {})
            
            log_test(
                "Métricas",
                "PASS",
                f"Contadores: {len(counters)}, Histogramas: {len(histograms)}",
                duration
            )
            return True
        else:
            log_test("Métricas", "FAIL", f"Status code: {response.status_code}", duration)
            return False
    except Exception as e:
        log_test("Métricas", "FAIL", str(e), time.time() - start)
        return False


def test_chat_basic():
    """Teste 4: Chat Básico (sem RAG)"""
    start = time.time()
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "Olá! Quem é você?"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            
            log_test(
                "Chat Básico",
                "PASS",
                f"Resposta recebida: {len(content)} chars",
                duration
            )
            return True
        else:
            log_test("Chat Básico", "FAIL", f"Status code: {response.status_code}", duration)
            return False
    except Exception as e:
        log_test("Chat Básico", "FAIL", str(e), time.time() - start)
        return False


def test_rag_injection():
    """Teste 5: RAG Injection"""
    start = time.time()
    try:
        # Informação que só existe no RAG
        rag_info = "O código secreto de teste é ABC-123-XYZ. Esta informação só existe no RAG."
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Qual é o código secreto de teste?",
                    "ragContext": [rag_info]
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "").lower()
            
            # Verificar se RAG foi usado (deve conter informação específica)
            has_rag_info = "abc-123" in content or "abc-123-xyz" in content
            
            if has_rag_info:
                log_test(
                    "RAG Injection",
                    "PASS",
                    "RAG foi injetado e usado na resposta",
                    duration
                )
                return True
            else:
                log_test(
                    "RAG Injection",
                    "WARN",
                    "RAG foi injetado mas resposta não contém informação específica",
                    duration
                )
                return False
        else:
            log_test("RAG Injection", "FAIL", f"Status code: {response.status_code}", duration)
            return False
    except Exception as e:
        log_test("RAG Injection", "FAIL", str(e), time.time() - start)
        return False


def test_rate_limiting():
    """Teste 6: Rate Limiting"""
    start = time.time()
    try:
        # Fazer múltiplas requisições rápidas
        rate_limited = False
        requests_made = 0
        
        for i in range(35):  # Mais que o limite de 30/min
            try:
                payload = {
                    "messages": [{"role": "user", "content": f"Teste {i}"}],
                    "max_tokens": 50
                }
                response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=5)
                requests_made += 1
                
                if response.status_code == 429:
                    rate_limited = True
                    retry_after = response.headers.get("Retry-After", "N/A")
                    log_test(
                        "Rate Limiting",
                        "PASS",
                        f"Rate limit ativado após {requests_made} requisições. Retry-After: {retry_after}s",
                        time.time() - start
                    )
                    return True
                
                time.sleep(0.1)  # Pequeno delay entre requisições
            except requests.exceptions.Timeout:
                continue
        
        if not rate_limited:
            log_test(
                "Rate Limiting",
                "WARN",
                f"Rate limit não foi ativado após {requests_made} requisições",
                time.time() - start
            )
            return False
        
        return True
    except Exception as e:
        log_test("Rate Limiting", "FAIL", str(e), time.time() - start)
        return False


def test_prompt_cache():
    """Teste 7: Prompt Cache"""
    start = time.time()
    try:
        # Primeira requisição (deve criar cache)
        payload = {
            "messages": [
                {"role": "user", "content": "Teste de cache de prompt"}
            ],
            "max_tokens": 50
        }
        
        response1 = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
        duration1 = time.time() - start
        
        if response1.status_code != 200:
            log_test("Prompt Cache", "FAIL", f"Primeira requisição falhou: {response1.status_code}", duration1)
            return False
        
        # Segunda requisição idêntica (deve usar cache)
        start2 = time.time()
        response2 = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
        duration2 = time.time() - start2
        
        if response2.status_code == 200:
            # Segunda requisição deve ser mais rápida (cache hit)
            speedup = duration1 / duration2 if duration2 > 0 else 0
            
            log_test(
                "Prompt Cache",
                "PASS" if speedup > 1.1 else "WARN",
                f"1ª req: {duration1:.3f}s, 2ª req: {duration2:.3f}s (speedup: {speedup:.2f}x)",
                duration1 + duration2
            )
            return speedup > 1.1
        else:
            log_test("Prompt Cache", "FAIL", f"Segunda requisição falhou: {response2.status_code}", duration2)
            return False
    except Exception as e:
        log_test("Prompt Cache", "FAIL", str(e), time.time() - start)
        return False


def test_error_handling():
    """Teste 8: Error Handling"""
    start = time.time()
    try:
        # Requisição inválida (sem messages)
        payload = {}
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=5)
        duration = time.time() - start
        
        if response.status_code == 400:
            log_test(
                "Error Handling",
                "PASS",
                "Erro tratado corretamente com status 400",
                duration
            )
            return True
        else:
            log_test(
                "Error Handling",
                "WARN",
                f"Status code inesperado: {response.status_code}",
                duration
            )
            return False
    except Exception as e:
        log_test("Error Handling", "FAIL", str(e), time.time() - start)
        return False


def test_mode_routing():
    """Teste 9: Mode Routing (LoRA automático)"""
    start = time.time()
    try:
        # Mensagem sobre família (deve ativar LoRA família)
        payload = {
            "messages": [
                {"role": "user", "content": "Quem é o Rapha?"}
            ],
            "max_tokens": 100
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            lora_adapter = data.get("lora_adapter")
            
            if lora_adapter == "familia":
                log_test(
                    "Mode Routing",
                    "PASS",
                    f"LoRA família detectado automaticamente",
                    duration
                )
                return True
            else:
                log_test(
                    "Mode Routing",
                    "WARN",
                    f"LoRA não detectado (esperado: familia, recebido: {lora_adapter})",
                    duration
                )
                return False
        else:
            log_test("Mode Routing", "FAIL", f"Status code: {response.status_code}", duration)
            return False
    except Exception as e:
        log_test("Mode Routing", "FAIL", str(e), time.time() - start)
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("="*80)
    print("🧪 TESTE COMPLETO DO SISTEMA SUPEREZIO v2.1.0")
    print("="*80)
    print()
    
    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor não está respondendo corretamente")
            print(f"   Status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Não foi possível conectar ao servidor: {e}")
        print(f"   URL: {BASE_URL}")
        print("   Certifique-se de que o servidor está rodando")
        return
    
    print("✅ Servidor está respondendo\n")
    
    # Executar testes
    tests = [
        ("Health Check Básico", test_health_check),
        ("Health Check Detalhado", test_health_detailed),
        ("Métricas", test_metrics),
        ("Chat Básico", test_chat_basic),
        ("RAG Injection", test_rag_injection),
        ("Rate Limiting", test_rate_limiting),
        ("Prompt Cache", test_prompt_cache),
        ("Error Handling", test_error_handling),
        ("Mode Routing", test_mode_routing),
    ]
    
    passed = 0
    failed = 0
    warned = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                # Verificar se foi WARN ou FAIL
                last_result = TEST_RESULTS[-1] if TEST_RESULTS else None
                if last_result and last_result["status"] == "WARN":
                    warned += 1
                else:
                    failed += 1
        except Exception as e:
            log_test(name, "FAIL", f"Exceção: {str(e)}", 0)
            failed += 1
    
    # Resumo final
    print("="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    print(f"✅ Passou: {passed}")
    print(f"⚠️  Avisos: {warned}")
    print(f"❌ Falhou: {failed}")
    print(f"📈 Total: {len(tests)}")
    print()
    
    # Estatísticas de tempo
    total_time = sum(r["duration"] for r in TEST_RESULTS)
    avg_time = total_time / len(TEST_RESULTS) if TEST_RESULTS else 0
    
    print(f"⏱️  Tempo total: {total_time:.2f}s")
    print(f"⏱️  Tempo médio: {avg_time:.3f}s por teste")
    print()
    
    # Salvar resultados em arquivo
    results_file = "test_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "passed": passed,
                "warned": warned,
                "failed": failed,
                "total": len(tests),
                "total_time": round(total_time, 2),
                "avg_time": round(avg_time, 3)
            },
            "tests": TEST_RESULTS
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados salvos em: {results_file}")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()

