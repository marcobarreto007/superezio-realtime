"""
LoRA Selector - Seleciona adaptador LoRA correto
Mapeia especialista → arquivo LoRA
"""

from typing import Optional
from pathlib import Path


# Mapeamento de especialista para LoRA
EXPERT_TO_LORA = {
    "familia": "familia",
    "contabilidade": "contabilidade",
    "trafego": "trafego",
    "pessoal": None,  # Usa modelo base
    "geral": None     # Usa modelo base
}


def select_lora(expert: str) -> Optional[str]:
    """
    Seleciona qual LoRA usar baseado no especialista
    
    Args:
        expert: Nome do especialista
    
    Returns:
        str | None: Nome do LoRA ou None para usar modelo base
    """
    return EXPERT_TO_LORA.get(expert, None)


def get_lora_path(expert: str, base_path: Path) -> Optional[Path]:
    """
    Retorna caminho completo para o adaptador LoRA
    
    Args:
        expert: Nome do especialista
        base_path: Diretório base dos LoRAs
    
    Returns:
        Path | None: Caminho completo ou None se não usar LoRA
    """
    lora_name = select_lora(expert)
    if lora_name is None:
        return None
    
    lora_path = base_path / f"lora_{lora_name}"
    return lora_path if lora_path.exists() else None


def list_available_loras(base_path: Path) -> dict:
    """Lista LoRAs disponíveis no sistema"""
    available = {}
    
    for expert, lora_name in EXPERT_TO_LORA.items():
        if lora_name:
            lora_path = base_path / f"lora_{lora_name}"
            available[expert] = {
                "name": lora_name,
                "path": str(lora_path),
                "exists": lora_path.exists()
            }
    
    return available


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 LORA SELECTOR")
    print("="*80)
    
    for expert in ["familia", "contabilidade", "trafego", "pessoal", "geral"]:
        lora = select_lora(expert)
        status = "🎯" if lora else "📦"
        print(f"{status} {expert:15} -> {lora or 'Base Model'}")
    
    print("="*80 + "\n")
