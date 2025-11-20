"""
Tests for HF Curator expert routing
Ensures HuggingFace/model queries are correctly routed to code_hf_curator
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expert_router import ExpertRouter


def test_hf_query_basic():
    """Query with 'HuggingFace' should route to code_hf_curator"""
    router = ExpertRouter()
    messages = [
        {"role": "user", "content": "Qual o melhor modelo de código no HuggingFace para Python hoje?"}
    ]
    
    decision = router.route(messages)
    
    assert decision.expert_id == "code_hf_curator", \
        f"Expected code_hf_curator, got {decision.expert_id}"
    assert "hf_models_code" in decision.rag_domains or "hf_datasets_code" in decision.rag_domains, \
        f"Expected HF RAG domains, got {decision.rag_domains}"
    print(f"✅ test_hf_query_basic: {decision.expert_id} (reason: {decision.reason})")


def test_hf_bigcode_stack():
    """Query with 'bigcode/the-stack' should route to code_hf_curator"""
    router = ExpertRouter()
    messages = [
        {"role": "user", "content": "Quero baixar o modelo bigcode/the-stack do Hugging Face e integrar no meu projeto"}
    ]
    
    decision = router.route(messages)
    
    assert decision.expert_id == "code_hf_curator", \
        f"Expected code_hf_curator, got {decision.expert_id}"
    print(f"✅ test_hf_bigcode_stack: {decision.expert_id} (reason: {decision.reason})")


def test_normal_python_query():
    """Query without HF triggers should NOT route to code_hf_curator"""
    router = ExpertRouter()
    messages = [
        {"role": "user", "content": "Me mostra um exemplo de código Python com asyncio para consumir uma API REST"}
    ]
    
    decision = router.route(messages)
    
    # Should NOT be code_hf_curator (likely code_python or code_api)
    assert decision.expert_id != "code_hf_curator", \
        f"Should NOT route to code_hf_curator for normal Python query, got {decision.expert_id}"
    print(f"✅ test_normal_python_query: {decision.expert_id} (reason: {decision.reason})")


def test_explicit_mode_override():
    """explicit_mode should override HF triggers"""
    router = ExpertRouter()
    messages = [
        {"role": "user", "content": "Como usar huggingface transformers em Python?"}
    ]
    
    # Force code_python even though query has "huggingface"
    decision = router.route(messages, explicit_mode="code_python")
    
    assert decision.expert_id == "code_python", \
        f"explicit_mode should override HF triggers, got {decision.expert_id}"
    print(f"✅ test_explicit_mode_override: {decision.expert_id} (reason: {decision.reason})")


def test_model_comparison_query():
    """Model comparison queries should route to code_hf_curator"""
    router = ExpertRouter()
    messages = [
        {"role": "user", "content": "Compare CodeLlama vs StarCoder para geração de código"}
    ]
    
    decision = router.route(messages)
    
    assert decision.expert_id == "code_hf_curator", \
        f"Expected code_hf_curator for model comparison, got {decision.expert_id}"
    print(f"✅ test_model_comparison_query: {decision.expert_id} (reason: {decision.reason})")


def test_qwen_llama_keywords():
    """Queries with Qwen/LLaMA keywords should route to code_hf_curator"""
    router = ExpertRouter()
    
    test_cases = [
        "Qual a diferença entre Qwen2.5 e Qwen 2 para código?",
        "Devo usar LLaMA 3 ou Mistral para code generation?",
        "WizardCoder é melhor que DeepSeek-Coder?"
    ]
    
    for query in test_cases:
        messages = [{"role": "user", "content": query}]
        decision = router.route(messages)
        
        assert decision.expert_id == "code_hf_curator", \
            f"Query '{query}' should route to code_hf_curator, got {decision.expert_id}"
        print(f"✅ test_qwen_llama_keywords: '{query[:50]}...' → {decision.expert_id}")


def test_model_selection_queries():
    """Model selection queries should route to code_hf_curator"""
    router = ExpertRouter()
    
    test_cases = [
        "Qual modelo usar para code completion?",
        "Me recomende um modelo open-source para Python",
        "Which model is better for TypeScript code generation?",
        "Escolher modelo de código para meu projeto"
    ]
    
    for query in test_cases:
        messages = [{"role": "user", "content": query}]
        decision = router.route(messages)
        
        assert decision.expert_id == "code_hf_curator", \
            f"Query '{query}' should route to code_hf_curator, got {decision.expert_id}"
        print(f"✅ test_model_selection_queries: '{query[:50]}...' → {decision.expert_id}")


def test_weights_checkpoint_keywords():
    """Queries about weights/checkpoints should route to code_hf_curator"""
    router = ExpertRouter()
    
    test_cases = [
        "Como baixar os weights do StarCoder?",
        "Onde encontro o checkpoint do modelo?",
        "Converter safetensors para GGUF"
    ]
    
    for query in test_cases:
        messages = [{"role": "user", "content": query}]
        decision = router.route(messages)
        
        assert decision.expert_id == "code_hf_curator", \
            f"Query '{query}' should route to code_hf_curator, got {decision.expert_id}"
        print(f"✅ test_weights_checkpoint_keywords: '{query[:50]}...' → {decision.expert_id}")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*70)
    print("  TESTING HF CURATOR ROUTING")
    print("="*70 + "\n")
    
    tests = [
        test_hf_query_basic,
        test_hf_bigcode_stack,
        test_normal_python_query,
        test_explicit_mode_override,
        test_model_comparison_query,
        test_qwen_llama_keywords,
        test_model_selection_queries,
        test_weights_checkpoint_keywords
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
