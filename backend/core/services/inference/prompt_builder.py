"""
Prompt Builder
Centralized prompt construction with strict priority system
Moved from backend/prompt_builder.py to core/services/inference/
"""
import os
from typing import List, Dict, Optional
from expert_registry import get_expert_persona


# Debug flag
DEBUG_PROMPT = os.getenv("DEBUG_PROMPT", "true").lower() == "true"


def build_messages(
    base_system: str,
    core_identity: str,
    rag_message: Optional[str],
    expert_id: str,
    history: List[Dict[str, str]],
    user_message: str,
    tools: Optional[List[Dict]] = None,
    max_history_turns: int = 10
) -> List[Dict[str, str]]:
    """
    Build final messages list with strict priority ordering.
    
    PRIORITY ORDER (most important first):
    1. SYSTEM: base_system (global safety/OS rules)
    2. SYSTEM: core_identity (SuperEzio global identity)
    3. SYSTEM: rag_message (RAG context with override wording)
    4. SYSTEM: expert_persona (expert-specific instructions)
    5. HISTORY: recent conversation turns
    6. USER: latest user message
    
    Args:
        base_system: Base system prompt (safety, OS rules)
        core_identity: Core SuperEzio identity
        rag_message: RAG context (or None)
        expert_id: Expert ID to get persona from
        history: Previous conversation turns (will be truncated)
        user_message: Latest user message
        tools: Optional tool definitions (will be injected in expert persona)
        max_history_turns: Maximum number of history turns to keep
        
    Returns:
        List of message dicts ready for model
    """
    messages: List[Dict[str, str]] = []
    
    # 1. BASE SYSTEM
    if base_system:
        messages.append({
            "role": "system",
            "content": base_system
        })
    
    # 2. CORE IDENTITY
    if core_identity:
        messages.append({
            "role": "system",
            "content": core_identity
        })
    
    # 3. RAG CONTEXT (if available)
    if rag_message:
        messages.append({
            "role": "system",
            "content": rag_message
        })
        if DEBUG_PROMPT:
            print(f"[PROMPT] RAG context injected: {len(rag_message)} chars")
    
    # 4. EXPERT PERSONA
    expert_persona = get_expert_persona(expert_id)
    
    # Add tool information if tools are provided
    if tools:
        tool_names = [t.get("name", "unknown") for t in tools]
        expert_persona += f"\n\nAVAILABLE TOOLS: {', '.join(tool_names)}"
        expert_persona += "\nUse these tools when needed to inspect files, read data, or execute actions."
        expert_persona += "\nNEVER hallucinate file contents or directory structures - always use tools first."
    
    messages.append({
        "role": "system",
        "content": expert_persona
    })
    
    if DEBUG_PROMPT:
        print(f"[PROMPT] Expert persona: {expert_id}")
        if tools:
            print(f"[PROMPT] Tools injected: {len(tools)} tools")
    
    # 5. HISTORY (truncated to last N turns)
    recent_history = history[-max_history_turns*2:] if history else []
    
    for msg in recent_history:
        # Skip system messages from history (already added above)
        if msg.get("role") != "system":
            messages.append(msg)
    
    if DEBUG_PROMPT:
        print(f"[PROMPT] History: {len(recent_history)} messages (from {len(history)} total)")
    
    # 6. USER MESSAGE
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    if DEBUG_PROMPT:
        print(f"[PROMPT] Final message count: {len(messages)}")
        system_count = sum(1 for m in messages if m.get("role") == "system")
        print(f"[PROMPT] System messages: {system_count}")
    
    return messages

