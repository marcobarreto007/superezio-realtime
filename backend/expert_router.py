"""
Expert Router - Routes requests to appropriate CODE expert based on content analysis
Implements keyword-based routing with explicit mode support
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

from expert_registry import EXPERTS, get_expert, resolve_from_hint, ExpertConfig


# Debug flag
DEBUG_ROUTER = os.getenv("DEBUG_ROUTER", "true").lower() == "true"


# ============================================================================
# HF CURATOR OVERRIDE TRIGGERS
# ============================================================================
# Regra de override HF:
# Se a query mencionar explicitamente HuggingFace / modelos open-source / Qwen / LLaMA etc,
# o expert code_hf_curator é escolhido antes de qualquer outro, exceto quando explicit_mode é forçado.

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


@dataclass
class RouterDecision:
    """Result of routing decision"""
    expert_id: str
    lora_adapter: Optional[str]
    rag_domains: List[str]
    reason: str
    expert_config: ExpertConfig


class ExpertRouter:
    """
    Routes chat requests to appropriate CODE expert.
    Uses keyword analysis and explicit hints.
    """
    
    def __init__(self):
        self.experts = EXPERTS
    
    def route(
        self,
        messages: List[Dict[str, str]],
        explicit_mode: Optional[str] = None
    ) -> RouterDecision:
        """
        Route request to appropriate expert.
        
        Priority:
        1. explicit_mode (if provided) → HIGHEST PRIORITY (cannot be overridden)
        2. HF_TRIGGERS detection → routes to code_hf_curator if HF-related keywords found
        3. keyword-based routing → fallback
        
        Args:
            messages: Chat messages (format: [{"role": "user", "content": "..."}])
            explicit_mode: Optional explicit expert hint (e.g. "python", "code_python")
            
        Returns:
            RouterDecision with expert_id, lora_adapter, rag_domains, reason
        """
        # PRIORITY 1: Explicit mode from client (ABSOLUTE PRIORITY - cannot be overridden)
        if explicit_mode:
            expert_id = self._resolve_explicit_mode(explicit_mode)
            expert_config = get_expert(expert_id)
            
            decision = RouterDecision(
                expert_id=expert_id,
                lora_adapter=expert_config["lora_adapter"],
                rag_domains=expert_config["rag_domains"],
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
        
        # PRIORITY 2: HF Curator Override (only if no explicit_mode)
        user_text = self._extract_user_text(messages).lower()
        
        for trigger in HF_TRIGGERS:
            if trigger in user_text:
                expert_config = get_expert("code_hf_curator")
                return RouterDecision(
                    expert_id="code_hf_curator",
                    lora_adapter=expert_config["lora_adapter"],
                    rag_domains=expert_config["rag_domains"],
                    reason=f"HF override detected (trigger: '{trigger}')",
                    expert_config=expert_config
                )

        # PRIORITY 3: Autonomous Agent Orchestrator
        orchestrator_config = get_expert("crew_agent_orchestrator")
        for trigger in orchestrator_config["keywords"]:
            if trigger.lower() in user_text:
                return RouterDecision(
                    expert_id="crew_agent_orchestrator",
                    lora_adapter=orchestrator_config["lora_adapter"],
                    rag_domains=orchestrator_config["rag_domains"],
                    reason=f"Autonomous task detected (trigger: '{trigger}')",
                    expert_config=orchestrator_config
                )

        # PRIORITY 4: Keyword-based routing
        expert_id, reason = self._route_by_keywords(messages)
        expert_config = get_expert(expert_id)
        
        decision = RouterDecision(
            expert_id=expert_id,
            lora_adapter=expert_config["lora_adapter"],
            rag_domains=expert_config["rag_domains"],
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
        """
        Resolve explicit mode string to expert_id.
        
        Args:
            mode: Mode string (e.g. "python", "code_python", "ts")
            
        Returns:
            Expert ID
        """
        # Check if it's already a valid expert_id
        if mode in self.experts:
            return mode
        
        # Try hint resolution
        expert_id = resolve_from_hint(mode)
        return expert_id
    
    def _extract_user_text(self, messages: List[Dict[str, str]]) -> str:
        """
        Extract and concatenate all user messages for trigger detection.
        
        Args:
            messages: Conversation history
            
        Returns:
            Concatenated user text
        """
        user_messages = [
            msg.get("content", "")
            for msg in messages
            if msg.get("role") == "user"
        ]
        return " ".join(user_messages)
    
    def _route_by_keywords(self, messages: List[Dict[str, str]]) -> tuple[str, str]:
        """
        Route based on keyword analysis of messages.
        
        Args:
            messages: Chat messages
            
        Returns:
            Tuple of (expert_id, reason)
        """
        # Extract user messages only
        user_messages = [
            msg.get("content", "").lower()
            for msg in messages
            if msg.get("role") == "user"
        ]
        
        if not user_messages:
            return "code_general", "No user messages found"
        
        # Concatenate all user text
        full_text = " ".join(user_messages)
        
        # Score each expert based on keyword matches
        expert_scores: Dict[str, tuple[int, List[str]]] = {}
        
        for expert_id, expert_config in self.experts.items():
            keywords = expert_config["keywords"]
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in full_text:
                    matched_keywords.append(keyword)
            
            score = len(matched_keywords)
            expert_scores[expert_id] = (score, matched_keywords)
        
        # Find expert with highest score
        best_expert = "code_general"
        best_score = 0
        best_keywords: List[str] = []
        
        for expert_id, (score, keywords) in expert_scores.items():
            if score > best_score:
                best_score = score
                best_expert = expert_id
                best_keywords = keywords
        
        # Build reason string
        if best_score > 0:
            keyword_preview = ", ".join(best_keywords[:5])  # First 5 keywords
            if len(best_keywords) > 5:
                keyword_preview += f" (+{len(best_keywords) - 5} more)"
            reason = f"Detected keywords: {keyword_preview}"
        else:
            reason = "No specific keywords detected, using general expert"
        
        return best_expert, reason


# Singleton instance
_router_instance: Optional[ExpertRouter] = None


def get_router() -> ExpertRouter:
    """Get singleton router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = ExpertRouter()
    return _router_instance
