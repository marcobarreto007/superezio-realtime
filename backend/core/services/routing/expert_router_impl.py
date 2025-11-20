"""
Expert Router Implementation
Consolida expert_router.py e mode_router.py em uma única implementação limpa
"""
import os
from typing import Dict, List, Optional
from core.services.routing.router import Router
from core.domain.expert import ExpertDecision
from expert_registry import EXPERTS, get_expert, resolve_from_hint


# Debug flag
DEBUG_ROUTER = os.getenv("DEBUG_ROUTER", "true").lower() == "true"


# HF Curator Override Triggers
HF_TRIGGERS = [
    "huggingface", "hugging face", "hf hub", "hf_hub", "hf token",
    "hf cache", "hf_models", "hf_datasets", "hf catalog", "hf harvester",
    "modelo do hf", "modelos do hf", "datasets do hf",
    "bigcode", "the stack", "the-stack", "starcoder", "starcoder2", "starcoder 2",
    "codellama", "code llama", "code-llama",
    "qwen2.5", "qwen 2.5", "qwen2", "qwen 2", "qwen code", "qwencoder",
    "mistral", "mixtral", "llama", "llama 2", "llama 3", "llama3", "llama2",
    "wizard coder", "wizardcoder", "deepseek", "deepseek-coder",
    "checkpoint", "weights", "safetensors", "gguf", "ggml",
    "open-source model", "open source model", "modelo open source",
    "modelo open-source", "opensource model",
    "melhor modelo de código", "best code model", "best model for code",
    "escolher modelo", "qual modelo usar", "which model should i use",
    "which model is better", "compare models", "model comparison",
    "recomendar modelo", "recommend model", "model recommendation",
    "model card", "pretrained model", "pre-trained model", "foundation model",
    "llm for code", "code llm", "coding model"
]


class ExpertRouterImpl:
    """
    Implementação do Router protocol.
    Routes chat requests to appropriate CODE expert.
    Consolida funcionalidade de expert_router.py e mode_router.py
    """
    
    def __init__(self):
        self.experts = EXPERTS
    
    def route(
        self,
        messages: List[Dict[str, str]],
        explicit_mode: Optional[str] = None
    ) -> ExpertDecision:
        """
        Route request to appropriate expert.
        
        Priority:
        1. explicit_mode (if provided) → HIGHEST PRIORITY
        2. HF_TRIGGERS detection → routes to code_hf_curator
        3. keyword-based routing → fallback
        
        Args:
            messages: Chat messages (format: [{"role": "user", "content": "..."}])
            explicit_mode: Optional explicit expert hint (e.g. "python", "code_python")
            
        Returns:
            ExpertDecision com expert_id, lora_adapter, rag_domains, reason
        """
        # PRIORITY 1: Explicit mode from client (ABSOLUTE PRIORITY)
        if explicit_mode:
            expert_id = self._resolve_explicit_mode(explicit_mode)
            expert_config = get_expert(expert_id)
            
            decision = ExpertDecision(
                expert_id=expert_id,
                lora_adapter=expert_config.get("lora_adapter"),
                rag_domains=expert_config.get("rag_domains", []),
                reason=f"Explicit mode: {explicit_mode}",
                expert_config=expert_config
            )
            
            if DEBUG_ROUTER:
                print(f"[ROUTER] explicit_mode={explicit_mode}")
                print(f"[ROUTER] → expert={decision.expert_id}")
                print(f"[ROUTER] → lora={decision.lora_adapter}")
                print(f"[ROUTER] → rag_domains={decision.rag_domains}")
                print(f"[ROUTER] → reason=\"{decision.reason}\"")
            
            return decision
        
        # PRIORITY 2: HF Curator Override
        user_text = self._extract_user_text(messages).lower()
        
        for trigger in HF_TRIGGERS:
            if trigger in user_text:
                expert_config = get_expert("code_hf_curator")
                if expert_config:
                    if DEBUG_ROUTER:
                        print(f"[ROUTER] HF override: trigger='{trigger}' → expert=code_hf_curator")
                    
                    decision = ExpertDecision(
                        expert_id="code_hf_curator",
                        lora_adapter=expert_config.get("lora_adapter"),
                        rag_domains=expert_config.get("rag_domains", []),
                        reason=f"HF override detected (trigger: '{trigger}')",
                        expert_config=expert_config
                    )
                    
                    if DEBUG_ROUTER:
                        print(f"[ROUTER] → expert={decision.expert_id}")
                        print(f"[ROUTER] → lora={decision.lora_adapter}")
                        print(f"[ROUTER] → rag_domains={decision.rag_domains}")
                        print(f"[ROUTER] → reason=\"{decision.reason}\"")
                    
                    return decision
        
        # PRIORITY 3: Keyword-based routing
        expert_id, reason = self._route_by_keywords(messages)
        expert_config = get_expert(expert_id)
        
        decision = ExpertDecision(
            expert_id=expert_id,
            lora_adapter=expert_config.get("lora_adapter"),
            rag_domains=expert_config.get("rag_domains", []),
            reason=reason,
            expert_config=expert_config
        )
        
        if DEBUG_ROUTER:
            print(f"[ROUTER] explicit_mode=None (keyword-based)")
            print(f"[ROUTER] → expert={decision.expert_id}")
            print(f"[ROUTER] → lora={decision.lora_adapter}")
            print(f"[ROUTER] → rag_domains={decision.rag_domains}")
            print(f"[ROUTER] → reason=\"{decision.reason}\"")
        
        return decision
    
    def _resolve_explicit_mode(self, mode: str) -> str:
        """Resolve explicit mode string to expert_id"""
        if mode in self.experts:
            return mode
        expert_id = resolve_from_hint(mode)
        return expert_id
    
    def _extract_user_text(self, messages: List[Dict[str, str]]) -> str:
        """Extract and concatenate all user messages"""
        user_messages = [
            msg.get("content", "")
            for msg in messages
            if msg.get("role") == "user"
        ]
        return " ".join(user_messages)
    
    def _route_by_keywords(self, messages: List[Dict[str, str]]) -> tuple[str, str]:
        """Route based on keyword analysis"""
        user_messages = [
            msg.get("content", "").lower()
            for msg in messages
            if msg.get("role") == "user"
        ]
        combined_text = " ".join(user_messages)
        
        # Score each expert based on keyword matches
        expert_scores: Dict[str, float] = {}
        
        for expert_id, config in self.experts.items():
            keywords = config.get("keywords", [])
            score = sum(1.0 for kw in keywords if kw.lower() in combined_text)
            
            # Normalize by keyword count
            if keywords:
                score = score / len(keywords)
            
            expert_scores[expert_id] = score
        
        # Find best match
        if not expert_scores or max(expert_scores.values()) == 0:
            # Default to general expert
            return "code_general", "No keywords matched, using default expert"
        
        best_expert = max(expert_scores.items(), key=lambda x: x[1])[0]
        best_score = expert_scores[best_expert]
        
        reason = f"Keyword match (score: {best_score:.2f})"
        return best_expert, reason


# Factory function
def create_router() -> Router:
    """Factory para criar instância do router"""
    return ExpertRouterImpl()

