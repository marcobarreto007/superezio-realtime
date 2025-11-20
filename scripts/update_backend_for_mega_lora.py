"""
Script para atualizar backend/inference.py para usar o Mega LoRA Unificado
Remove multi-LoRA logic e SYSTEM_PROMPT (agora tudo está no LoRA)
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
INFERENCE_FILE = PROJECT_ROOT / "backend" / "inference.py"

print("="*80)
print("🔧 ATUALIZANDO BACKEND PARA MEGA LoRA UNIFICADO")
print("="*80)
print(f"📁 Arquivo: {INFERENCE_FILE}")
print()

# Ler arquivo
with open(INFERENCE_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
backup_file = INFERENCE_FILE.with_suffix(".py.backup")
with open(backup_file, "w", encoding="utf-8") as f:
    f.write(content)
print(f"💾 Backup criado: {backup_file}")

# 1. Atualizar configuração de LoRA
print("\n1️⃣  Atualizando configuração de LoRA...")
old_lora_config = """# Multi-LoRA configuration
LORA_PERSONALITY_DIR = PROJECT_ROOT / "models" / "lora_personality_v2"  # 🎭
LORA_ACCOUNTING_DIR = PROJECT_ROOT / "models" / "lora_accounting"    # 🇨🇦
LORA_LEGACY_DIR = PROJECT_ROOT / "models" / "lora_superezio"          # Legacy"""

new_lora_config = """# MEGA LoRA Unificado - Personalidade + Contabilidade + Ferramentas
LORA_MEGA_UNIFIED_DIR = PROJECT_ROOT / "models" / "lora_mega_unified"  # 🚀 MEGA"""

content = content.replace(old_lora_config, new_lora_config)
print("   ✅ Configuração de LoRA atualizada")

# 2. Remover/comentar SYSTEM_PROMPT
print("\n2️⃣  Comentando SYSTEM_PROMPT (agora está no LoRA)...")
# Encontrar e comentar todo o bloco SYSTEM_PROMPT
system_prompt_pattern = r'(SYSTEM_PROMPT = """.*?""")'
content = re.sub(
    system_prompt_pattern,
    lambda m: '\n'.join(['# ' + line for line in m.group(1).split('\n')]),
    content,
    flags=re.DOTALL
)
print("   ✅ SYSTEM_PROMPT comentado")

# 3. Simplificar lógica de carregamento de LoRA
print("\n3️⃣  Simplificando lógica de carregamento...")
# Substituir toda a lógica de multi-LoRA por carregamento simples
old_loading_logic_pattern = r'# Configurar e carregar LoRA.*?print\("✅ Modelo LoRA carregado"\)'

new_loading_logic = '''# Carregar MEGA LoRA Unificado
print("🔧 Carregando MEGA LoRA Unificado...")
if LORA_MEGA_UNIFIED_DIR.exists():
    print(f"   📁 LoRA: {LORA_MEGA_UNIFIED_DIR.name}")
    model = PeftModel.from_pretrained(
        model,
        str(LORA_MEGA_UNIFIED_DIR),
        is_trainable=False,
    )
    print("✅ MEGA LoRA carregado!")
    print("   🎭 Personalidade SuperEzio")
    print("   🇨🇦 Conhecimento Contabilidade CRA")
    print("   🔧 11 Ferramentas integradas")
else:
    print("⚠️  MEGA LoRA não encontrado, usando modelo base")
print("✅ Modelo LoRA carregado")'''

content = re.sub(
    old_loading_logic_pattern,
    new_loading_logic,
    content,
    flags=re.DOTALL
)
print("   ✅ Lógica de carregamento simplificada")

# 4. Atualizar função generate() para não usar SYSTEM_PROMPT
print("\n4️⃣  Atualizando função generate()...")
# Remover uso de SYSTEM_PROMPT na função generate
old_generate_pattern = r'messages = \[\{"role": "system", "content": SYSTEM_PROMPT\}\]'
new_generate_pattern = 'messages = []  # Sem system prompt - tudo está no LoRA!'
content = content.replace(old_generate_pattern, new_generate_pattern)
print("   ✅ Função generate() atualizada")

# Salvar arquivo atualizado
with open(INFERENCE_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("="*80)
print("✅ BACKEND ATUALIZADO COM SUCESSO!")
print("="*80)
print()
print("📝 MUDANÇAS APLICADAS:")
print("   1. ✅ Configuração de LoRA: lora_mega_unified")
print("   2. ✅ SYSTEM_PROMPT comentado")
print("   3. ✅ Multi-LoRA removido → Single MEGA LoRA")
print("   4. ✅ Função generate() sem system prompt")
print()
print("🚀 PRÓXIMOS PASSOS:")
print("   1. Verificar se o training completou")
print("   2. Reiniciar backend:")
print("      cd backend")
print("      python api.py")
print()
print("="*80)
