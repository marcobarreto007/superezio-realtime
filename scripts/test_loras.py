"""
Script para testar os LoRAs de personalidade
"""

import json
from pathlib import Path

def test_lora_info():
    """Testa informações dos LoRAs sem carregar"""
    
    loras = [
        'C:/Users/marco/Superezio Realtime/models/lora_familia_FINAL',
        'C:/Users/marco/Superezio Realtime/models/lora_familia_mega_v2'
    ]
    
    print("\n🧪 TESTE DE LORAS DE PERSONALIDADE")
    print("=" * 60)
    
    for lora_path in loras:
        print(f'\n📦 {Path(lora_path).name}')
        print('-' * 60)
        
        # Adapter config
        config_file = Path(lora_path) / 'adapter_config.json'
        if config_file.exists():
            config = json.loads(config_file.read_text())
            print(f'  LoRA Rank: {config.get("r", "N/A")}')
            print(f'  LoRA Alpha: {config.get("lora_alpha", "N/A")}')
            print(f'  Target Modules: {", ".join(config.get("target_modules", [])[:3])}...')
            print(f'  Base Model: {Path(config.get("base_model_name_or_path", "N/A")).name}')
        
        # Training info
        training_file = Path(lora_path) / 'training_info.json'
        if training_file.exists():
            training = json.loads(training_file.read_text())
            print(f'  Epochs: {training.get("num_train_epochs", "N/A")}')
            print(f'  Steps: {training.get("total_steps", "N/A")}')
            print(f'  Loss final: {training.get("final_loss", "N/A")}')
        
        # Tamanho do adapter
        adapter_file = Path(lora_path) / 'adapter_model.safetensors'
        if adapter_file.exists():
            size_gb = adapter_file.stat().st_size / (1024**3)
            print(f'  Tamanho: {size_gb:.2f} GB')
    
    print('\n' + '=' * 60)
    print('✅ Informações coletadas!')
    print('\n💡 Para testar conversação, configure model_status.json para usar um deles:')
    print('   {"active_adapter": "lora_familia_FINAL"}')
    print('   ou')
    print('   {"active_adapter": "lora_familia_mega_v2"}')
    print('\nDepois inicie: cd backend; python api.py')

if __name__ == '__main__':
    test_lora_info()
