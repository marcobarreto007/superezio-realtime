"""
Script para INTERAGIR com o treino LLaMA-Factory em execução
Injeta comandos via sinais do sistema operacional
"""

import os
import sys
import psutil
import signal
import time
from pathlib import Path

# Cores para output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def find_training_process():
    """Encontra o processo de treino LLaMA-Factory"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('llamafactory-cli' in str(arg) or 'train' in str(arg) for arg in cmdline):
                # Verifica se é o processo de treino (não o monitor)
                if 'train' in ' '.join(cmdline) and 'monitor' not in ' '.join(cmdline):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def pause_training(proc):
    """PAUSA o treino (suspende o processo)"""
    try:
        proc.suspend()
        print(f"{YELLOW}⏸️  TREINO PAUSADO{RESET}")
        print(f"   PID: {proc.pid}")
        print(f"   Para retomar: use 'resume' ou pressione Ctrl+C e escolha 'r'")
        return True
    except Exception as e:
        print(f"{RED}❌ Erro ao pausar: {e}{RESET}")
        return False

def resume_training(proc):
    """RETOMA o treino pausado"""
    try:
        proc.resume()
        print(f"{GREEN}▶️  TREINO RETOMADO{RESET}")
        return True
    except Exception as e:
        print(f"{RED}❌ Erro ao retomar: {e}{RESET}")
        return False

def stop_training(proc):
    """PARA o treino (SIGTERM graceful)"""
    try:
        print(f"{YELLOW}🛑 Enviando sinal de parada graceful...{RESET}")
        proc.terminate()
        
        # Aguarda até 30 segundos para finalizar
        try:
            proc.wait(timeout=30)
            print(f"{GREEN}✅ Treino parado com sucesso{RESET}")
            return True
        except psutil.TimeoutExpired:
            print(f"{YELLOW}⚠️  Processo não respondeu, forçando kill...{RESET}")
            proc.kill()
            print(f"{RED}💀 Treino morto à força{RESET}")
            return True
    except Exception as e:
        print(f"{RED}❌ Erro ao parar: {e}{RESET}")
        return False

def get_process_stats(proc):
    """Obtém estatísticas do processo"""
    try:
        cpu = proc.cpu_percent(interval=1)
        mem = proc.memory_info().rss / (1024**3)  # GB
        runtime = time.time() - proc.create_time()
        
        hours = int(runtime // 3600)
        minutes = int((runtime % 3600) // 60)
        
        return {
            'cpu': cpu,
            'mem': mem,
            'runtime_hours': hours,
            'runtime_minutes': minutes
        }
    except:
        return None

def show_training_log(lines=20):
    """Mostra últimas linhas do log de treino"""
    log_path = Path("C:/Users/marco/Superezio Realtime/models/lora_code_expert_v1/trainer_log.jsonl")
    
    if not log_path.exists():
        print(f"{RED}❌ Log não encontrado: {log_path}{RESET}")
        return
    
    print(f"\n{BLUE}📋 ÚLTIMAS {lines} LINHAS DO LOG:{RESET}")
    print("-" * 80)
    
    with open(log_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        for line in all_lines[-lines:]:
            print(line.strip())
    print("-" * 80)

def interactive_menu(proc):
    """Menu interativo para controlar o treino"""
    while True:
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{GREEN}🎮 CONTROLE DO TREINO - MENU INTERATIVO{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        # Status do processo
        try:
            status = proc.status()
            stats = get_process_stats(proc)
            
            print(f"\n📊 Status: {status.upper()}")
            print(f"   PID: {proc.pid}")
            if stats:
                print(f"   CPU: {stats['cpu']:.1f}%")
                print(f"   RAM: {stats['mem']:.2f} GB")
                print(f"   Runtime: {stats['runtime_hours']}h {stats['runtime_minutes']}m")
        except psutil.NoSuchProcess:
            print(f"\n{RED}❌ Processo de treino não está mais rodando{RESET}")
            return
        
        print(f"\n{YELLOW}Comandos disponíveis:{RESET}")
        print("  [p] PAUSAR treino (suspender processo)")
        print("  [r] RETOMAR treino (continuar)")
        print("  [s] PARAR treino (graceful stop)")
        print("  [k] MATAR treino (kill -9)")
        print("  [l] Ver LOG (últimas 20 linhas)")
        print("  [i] Ver INFO detalhada")
        print("  [q] SAIR (deixar treino rodando)")
        
        choice = input(f"\n{GREEN}Digite sua escolha: {RESET}").strip().lower()
        
        if choice == 'p':
            pause_training(proc)
        elif choice == 'r':
            resume_training(proc)
        elif choice == 's':
            if stop_training(proc):
                return
        elif choice == 'k':
            print(f"{RED}💀 MATANDO PROCESSO...{RESET}")
            proc.kill()
            print(f"{RED}✅ Processo morto{RESET}")
            return
        elif choice == 'l':
            show_training_log(20)
        elif choice == 'i':
            show_detailed_info(proc)
        elif choice == 'q':
            print(f"{GREEN}👋 Saindo (treino continua rodando)...{RESET}")
            return
        else:
            print(f"{RED}❌ Comando inválido{RESET}")

def show_detailed_info(proc):
    """Mostra informações detalhadas do processo"""
    try:
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{GREEN}📊 INFORMAÇÕES DETALHADAS DO TREINO{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        # Processo
        print(f"\n🔹 Processo:")
        print(f"   PID: {proc.pid}")
        print(f"   Nome: {proc.name()}")
        print(f"   Status: {proc.status()}")
        print(f"   Criado em: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(proc.create_time()))}")
        
        # Recursos
        stats = get_process_stats(proc)
        if stats:
            print(f"\n🔹 Recursos:")
            print(f"   CPU: {stats['cpu']:.1f}%")
            print(f"   RAM: {stats['mem']:.2f} GB")
            print(f"   Tempo rodando: {stats['runtime_hours']}h {stats['runtime_minutes']}m")
        
        # Threads
        print(f"\n🔹 Threads: {proc.num_threads()}")
        
        # Arquivos abertos (limitado)
        try:
            open_files = proc.open_files()[:5]
            if open_files:
                print(f"\n🔹 Arquivos abertos (primeiros 5):")
                for f in open_files:
                    print(f"   {f.path}")
        except:
            pass
        
        # Progresso do treino (do log)
        log_path = Path("C:/Users/marco/Superezio Realtime/models/lora_code_expert_v1/trainer_log.jsonl")
        if log_path.exists():
            import json
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    print(f"\n🔹 Progresso do Treino:")
                    print(f"   Step atual: {last_entry.get('current_steps', 'N/A')}")
                    print(f"   Steps totais: {last_entry.get('total_steps', 'N/A')}")
                    print(f"   Percentual: {last_entry.get('percentage', 'N/A')}%")
                    print(f"   Loss: {last_entry.get('loss', 'N/A')}")
                    print(f"   Tempo restante: {last_entry.get('remaining_time', 'N/A')}")
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        
    except Exception as e:
        print(f"{RED}❌ Erro ao obter informações: {e}{RESET}")

def main():
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}🎮 CONTROLE INTERATIVO DO TREINO LLAMA-FACTORY{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    
    print(f"\n{YELLOW}🔍 Procurando processo de treino...{RESET}")
    
    proc = find_training_process()
    
    if not proc:
        print(f"{RED}❌ Processo de treino não encontrado!{RESET}")
        print(f"\n{YELLOW}Dica: O treino está rodando?{RESET}")
        print("   Use: cd C:\\Users\\marco\\LLaMA-Factory")
        print("   E execute: .\\venv\\Scripts\\llamafactory-cli.exe train ...")
        return
    
    print(f"{GREEN}✅ Processo encontrado!{RESET}")
    print(f"   PID: {proc.pid}")
    print(f"   Nome: {proc.name()}")
    print(f"   Status: {proc.status()}")
    
    # Menu interativo
    try:
        interactive_menu(proc)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️  Ctrl+C detectado!{RESET}")
        print(f"\n{YELLOW}O que você quer fazer?{RESET}")
        print("  [p] PAUSAR treino")
        print("  [s] PARAR treino (graceful)")
        print("  [k] MATAR treino (kill -9)")
        print("  [c] CONTINUAR (voltar ao menu)")
        
        choice = input(f"\n{GREEN}Digite sua escolha: {RESET}").strip().lower()
        
        if choice == 'p':
            pause_training(proc)
        elif choice == 's':
            stop_training(proc)
        elif choice == 'k':
            proc.kill()
            print(f"{RED}💀 Processo morto{RESET}")
        elif choice == 'c':
            interactive_menu(proc)
        
        print(f"\n{GREEN}👋 Saindo...{RESET}")

if __name__ == "__main__":
    main()
