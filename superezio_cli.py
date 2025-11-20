#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SuperEzio CLI - Interface de linha de comando interativa
Tipo Gemini CLI, direto no PowerShell/CMD

Uso:
    python superezio_cli.py                    # Modo interativo
    python superezio_cli.py "sua pergunta"     # Pergunta única
    python superezio_cli.py --help             # Ajuda

Ferramentas automáticas:
- Leitura/escrita de arquivos
- Listagem de diretórios
- Busca de arquivos
- Criação de tabelas
- E mais...
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from inference import chat_completion, load_model
from tools_config import AVAILABLE_TOOLS

# Cores ANSI para terminal
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Cores de texto
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Cores brilhantes
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

def print_banner():
    """Exibe banner do SuperEzio"""
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}")
    print("=" * 70)
    print("  ____                       _____     _       ")
    print(" / ___| _   _ _ __   ___ _ _| ____|___(_) ___  ")
    print(" \\___ \\| | | | '_ \\ / _ \\ '__||  _| / __| |/ _ \\ ")
    print("  ___) | |_| | |_) |  __/ |   | |__| (__| | (_) |")
    print(" |____/ \\__,_| .__/ \\___|_|   |_____\\___|_|\\___/ ")
    print("             |_|                                 ")
    print("=" * 70)
    print(f"{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}🤖 SuperEzio CLI - Seu assistente AI local{Colors.RESET}")
    print(f"{Colors.DIM}💡 Digite 'ajuda' para comandos | 'sair' para encerrar{Colors.RESET}")
    print()

def print_help():
    """Exibe ajuda"""
    help_text = f"""
{Colors.BRIGHT_CYAN}{Colors.BOLD}COMANDOS DISPONÍVEIS:{Colors.RESET}

{Colors.BRIGHT_GREEN}Conversação:{Colors.RESET}
  <sua pergunta>     Faça qualquer pergunta ao SuperEzio
  ajuda              Mostra esta mensagem
  sair / exit        Encerra o CLI
  limpar / clear     Limpa o histórico de conversa
  historico          Mostra histórico da conversa

{Colors.BRIGHT_GREEN}Ferramentas automáticas:{Colors.RESET}
  SuperEzio tem acesso automático a:
  • Arquivos: ler, escrever, deletar, info
  • Diretórios: listar, criar, buscar
  • Dados: criar tabelas
  • Email: ler, buscar (se configurado)

{Colors.BRIGHT_GREEN}Exemplos:{Colors.RESET}
  {Colors.CYAN}> liste os arquivos do meu desktop{Colors.RESET}
  {Colors.CYAN}> crie um arquivo teste.txt no desktop com "Olá Mundo"{Colors.RESET}
  {Colors.CYAN}> leia o arquivo config.json{Colors.RESET}
  {Colors.CYAN}> busque todos os arquivos .py na pasta atual{Colors.RESET}

{Colors.BRIGHT_GREEN}Atalhos:{Colors.RESET}
  Ctrl+C             Cancela entrada atual
  Ctrl+D             Sai do CLI
"""
    print(help_text)

def format_response(response_text: str) -> str:
    """Formata resposta com cores e markdown básico"""
    # Code blocks
    if "```" in response_text:
        parts = response_text.split("```")
        formatted = ""
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Texto normal
                formatted += part
            else:
                # Code block
                formatted += f"{Colors.DIM}{Colors.CYAN}{part}{Colors.RESET}"
        response_text = formatted
    
    # Bold **texto**
    while "**" in response_text:
        response_text = response_text.replace("**", f"{Colors.BOLD}", 1)
        if "**" in response_text:
            response_text = response_text.replace("**", f"{Colors.RESET}", 1)
    
    return response_text

def chat_interactive():
    """Modo interativo do CLI"""
    print_banner()
    
    # Carregar modelo
    print(f"{Colors.YELLOW}⏳ Carregando SuperEzio... (15-20 segundos){Colors.RESET}")
    try:
        load_model(mode=None)
        print(f"{Colors.GREEN}✅ SuperEzio pronto!{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao carregar modelo: {e}{Colors.RESET}")
        sys.exit(1)
    
    # Histórico da conversa
    history: List[Dict[str, str]] = []
    
    while True:
        try:
            # Prompt
            prompt_text = f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}Você:{Colors.RESET} "
            user_input = input(prompt_text).strip()
            
            if not user_input:
                continue
            
            # Comandos especiais
            if user_input.lower() in ["sair", "exit", "quit"]:
                print(f"{Colors.YELLOW}👋 Até logo!{Colors.RESET}")
                break
            
            if user_input.lower() in ["ajuda", "help", "?"]:
                print_help()
                continue
            
            if user_input.lower() in ["limpar", "clear", "cls"]:
                history.clear()
                os.system("cls" if os.name == "nt" else "clear")
                print(f"{Colors.GREEN}✅ Histórico limpo{Colors.RESET}\n")
                continue
            
            if user_input.lower() in ["historico", "history"]:
                if not history:
                    print(f"{Colors.YELLOW}ℹ️  Histórico vazio{Colors.RESET}\n")
                else:
                    print(f"{Colors.CYAN}📜 Histórico ({len(history)} mensagens):{Colors.RESET}")
                    for i, msg in enumerate(history, 1):
                        role_color = Colors.BRIGHT_MAGENTA if msg["role"] == "user" else Colors.BRIGHT_CYAN
                        role_label = "Você" if msg["role"] == "user" else "SuperEzio"
                        content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        print(f"{role_color}{i}. {role_label}:{Colors.RESET} {content_preview}")
                    print()
                continue
            
            # Adicionar mensagem do usuário ao histórico
            history.append({"role": "user", "content": user_input})
            
            # Chamar SuperEzio com ferramentas ativadas
            print(f"{Colors.YELLOW}⏳ Pensando...{Colors.RESET}", end="\r")
            
            messages = history.copy()
            
            response = chat_completion(
                messages=messages,
                tools=AVAILABLE_TOOLS,  # ✅ Ferramentas ativadas
                temperature=0.7,
                max_tokens=512,
                stream=False
            )
            
            # Limpar linha "Pensando..."
            print(" " * 50, end="\r")
            
            # Processar resposta
            if isinstance(response, dict):
                content = response.get("content", "")
                tool_calls = response.get("tool_calls")
                tool_results = response.get("tool_results")
                
                # Mostrar ferramentas usadas
                if tool_calls:
                    print(f"{Colors.DIM}🔧 Ferramentas usadas: {len(tool_calls)}{Colors.RESET}")
                    for tc in tool_calls:
                        tool_name = tc.get("name", "unknown")
                        print(f"{Colors.DIM}   • {tool_name}{Colors.RESET}")
                
                # Mostrar resposta
                print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}SuperEzio:{Colors.RESET}")
                formatted_content = format_response(content)
                print(formatted_content)
                print()
                
                # Adicionar resposta ao histórico
                history.append({"role": "assistant", "content": content})
                
            else:
                print(f"{Colors.RED}❌ Erro: resposta inválida{Colors.RESET}\n")
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Use 'sair' para encerrar{Colors.RESET}\n")
            continue
        
        except EOFError:
            print(f"\n{Colors.YELLOW}👋 Até logo!{Colors.RESET}")
            break
        
        except Exception as e:
            print(f"{Colors.RED}❌ Erro: {e}{Colors.RESET}\n")
            import traceback
            traceback.print_exc()

def chat_single(question: str):
    """Modo de pergunta única"""
    print(f"{Colors.YELLOW}⏳ Carregando SuperEzio...{Colors.RESET}")
    try:
        load_model(mode=None)
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao carregar modelo: {e}{Colors.RESET}")
        sys.exit(1)
    
    print(f"{Colors.BRIGHT_MAGENTA}Pergunta:{Colors.RESET} {question}\n")
    print(f"{Colors.YELLOW}⏳ Processando...{Colors.RESET}")
    
    messages = [{"role": "user", "content": question}]
    
    response = chat_completion(
        messages=messages,
        tools=AVAILABLE_TOOLS,  # ✅ Ferramentas ativadas
        temperature=0.7,
        max_tokens=512,
        stream=False
    )
    
    if isinstance(response, dict):
        content = response.get("content", "")
        tool_calls = response.get("tool_calls")
        
        if tool_calls:
            print(f"\n{Colors.DIM}🔧 Ferramentas usadas: {len(tool_calls)}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}SuperEzio:{Colors.RESET}")
        formatted_content = format_response(content)
        print(formatted_content)
        print()
    else:
        print(f"{Colors.RED}❌ Erro: resposta inválida{Colors.RESET}")

def main():
    """Entrada principal"""
    parser = argparse.ArgumentParser(
        description="SuperEzio CLI - Assistente AI local com ferramentas",
        epilog="Exemplos:\n"
               "  python superezio_cli.py\n"
               "  python superezio_cli.py \"liste os arquivos do desktop\"\n"
               "  python superezio_cli.py --help",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "question",
        nargs="*",
        help="Pergunta única (se omitido, entra em modo interativo)"
    )
    
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Desabilitar ferramentas (apenas conversa)"
    )
    
    args = parser.parse_args()
    
    # Modo interativo ou pergunta única
    if args.question:
        question = " ".join(args.question)
        chat_single(question)
    else:
        chat_interactive()

if __name__ == "__main__":
    main()
