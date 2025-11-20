"""
Monitor de treino LLaMA-Factory
Mostra progresso em tempo real
"""
import json
import time
from pathlib import Path

OUTPUT_DIR = Path(r"C:\Users\marco\Superezio Realtime\models\lora_familia_llamafactory_v1")
LOG_FILE = OUTPUT_DIR / "trainer_log.jsonl"

def monitor_training():
    print("="*70)
    print("📊 MONITOR DE TREINO - LLaMA Factory")
    print("="*70)
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"📝 Log: {LOG_FILE}")
    print("="*70)
    
    if not OUTPUT_DIR.exists():
        print("⏳ Aguardando início do treino...")
        while not OUTPUT_DIR.exists():
            time.sleep(5)
            print(".", end="", flush=True)
        print("\n✅ Treino iniciado!")
    
    if not LOG_FILE.exists():
        print("⏳ Aguardando log file...")
        while not LOG_FILE.exists():
            time.sleep(2)
            print(".", end="", flush=True)
        print("\n")
    
    # Ler logs
    last_size = 0
    last_step = 0
    
    print("\n🔄 Monitorando progresso (Ctrl+C para sair)...\n")
    
    try:
        while True:
            if LOG_FILE.exists():
                current_size = LOG_FILE.stat().st_size
                
                if current_size > last_size:
                    with open(LOG_FILE, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                        last_size = current_size
                    
                    for line in new_lines:
                        try:
                            entry = json.loads(line.strip())
                            
                            # Dados de treino
                            step = entry.get('current_steps', 0)
                            loss = entry.get('loss', 0)
                            lr = entry.get('learning_rate', 0)
                            epoch = entry.get('epoch', 0)
                            
                            if step > last_step:
                                last_step = step
                                print(f"Step {step:4d} | Epoch {epoch:.2f} | Loss: {loss:.4f} | LR: {lr:.2e}")
                                
                        except json.JSONDecodeError:
                            continue
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitor encerrado")
        print("="*70)
        
        # Resumo final
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1].strip())
                    print("📊 Último status:")
                    print(f"   Step: {last_entry.get('current_steps', 'N/A')}")
                    print(f"   Epoch: {last_entry.get('epoch', 'N/A')}")
                    print(f"   Loss: {last_entry.get('loss', 'N/A')}")
        
        print("="*70)

if __name__ == "__main__":
    monitor_training()
