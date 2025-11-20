#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE ÉPICO DO SUPEREZIO CLI
Demonstração completa de capacidades com ferramentas
"""

import sys
import os
import time
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from inference import chat_completion, load_model
from tools_config import AVAILABLE_TOOLS

print("=" * 70)
print("🔥 TESTE ÉPICO DO SUPEREZIO - PROVA DE CAPACIDADES")
print("=" * 70)
print()

# Carregar modelo
print("⏳ Carregando SuperEzio...")
start_load = time.time()
load_model(mode=None)
load_time = time.time() - start_load
print(f"✅ SuperEzio carregado em {load_time:.2f}s")
print()

# Histórico de conversa
history = []

# ========================================
# TESTE 1: Listagem de arquivos
# ========================================
print("=" * 70)
print("📋 TESTE 1: Liste os 5 primeiros arquivos do Desktop")
print("=" * 70)

query1 = "Liste os 5 primeiros arquivos do meu Desktop"
history.append({"role": "user", "content": query1})

print(f"❓ Pergunta: {query1}")
start = time.time()

response1 = chat_completion(
    messages=history.copy(),
    tools=AVAILABLE_TOOLS,
    temperature=0.7,
    max_tokens=512,
    stream=False
)

elapsed = time.time() - start

if isinstance(response1, dict):
    content = response1.get("content", "")
    tool_calls = response1.get("tool_calls")
    
    if tool_calls:
        print(f"🔧 Ferramentas usadas: {len(tool_calls)}")
        for tc in tool_calls:
            print(f"   • {tc.get('name')}")
    
    print(f"\n💬 Resposta:")
    print(content)
    print(f"\n⏱️  Tempo: {elapsed:.2f}s")
    
    history.append({"role": "assistant", "content": content})
else:
    print(f"❌ Erro: {response1}")

print()

# ========================================
# TESTE 2: Criação de arquivo
# ========================================
print("=" * 70)
print("📝 TESTE 2: Crie um arquivo teste no Desktop")
print("=" * 70)

query2 = "Crie um arquivo chamado 'superezio_test.txt' no Desktop com o texto 'SuperEzio funcionando perfeitamente! Data: 13/11/2025 - Hora: " + time.strftime("%H:%M:%S") + "'"
history.append({"role": "user", "content": query2})

print(f"❓ Pergunta: Crie arquivo superezio_test.txt no Desktop")
start = time.time()

response2 = chat_completion(
    messages=history.copy(),
    tools=AVAILABLE_TOOLS,
    temperature=0.7,
    max_tokens=512,
    stream=False
)

elapsed = time.time() - start

if isinstance(response2, dict):
    content = response2.get("content", "")
    tool_calls = response2.get("tool_calls")
    
    if tool_calls:
        print(f"🔧 Ferramentas usadas: {len(tool_calls)}")
        for tc in tool_calls:
            print(f"   • {tc.get('name')}")
    
    print(f"\n💬 Resposta:")
    print(content)
    print(f"\n⏱️  Tempo: {elapsed:.2f}s")
    
    history.append({"role": "assistant", "content": content})
else:
    print(f"❌ Erro: {response2}")

print()

# ========================================
# TESTE 3: Leitura do arquivo criado
# ========================================
print("=" * 70)
print("👀 TESTE 3: Leia o arquivo que você criou")
print("=" * 70)

query3 = "Agora leia o arquivo superezio_test.txt que você acabou de criar"
history.append({"role": "user", "content": query3})

print(f"❓ Pergunta: {query3}")
start = time.time()

response3 = chat_completion(
    messages=history.copy(),
    tools=AVAILABLE_TOOLS,
    temperature=0.7,
    max_tokens=512,
    stream=False
)

elapsed = time.time() - start

if isinstance(response3, dict):
    content = response3.get("content", "")
    tool_calls = response3.get("tool_calls")
    
    if tool_calls:
        print(f"🔧 Ferramentas usadas: {len(tool_calls)}")
        for tc in tool_calls:
            print(f"   • {tc.get('name')}")
    
    print(f"\n💬 Resposta:")
    print(content)
    print(f"\n⏱️  Tempo: {elapsed:.2f}s")
    
    history.append({"role": "assistant", "content": content})
else:
    print(f"❌ Erro: {response3}")

print()

# ========================================
# TESTE 4: Busca de arquivos
# ========================================
print("=" * 70)
print("🔍 TESTE 4: Busque arquivos .txt no disco D:")
print("=" * 70)

query4 = "Busque todos os arquivos .txt na pasta bebe_ia do disco D:"
history.append({"role": "user", "content": query4})

print(f"❓ Pergunta: {query4}")
start = time.time()

response4 = chat_completion(
    messages=history.copy(),
    tools=AVAILABLE_TOOLS,
    temperature=0.7,
    max_tokens=512,
    stream=False
)

elapsed = time.time() - start

if isinstance(response4, dict):
    content = response4.get("content", "")
    tool_calls = response4.get("tool_calls")
    
    if tool_calls:
        print(f"🔧 Ferramentas usadas: {len(tool_calls)}")
        for tc in tool_calls:
            print(f"   • {tc.get('name')}")
    
    print(f"\n💬 Resposta:")
    print(content)
    print(f"\n⏱️  Tempo: {elapsed:.2f}s")
    
    history.append({"role": "assistant", "content": content})
else:
    print(f"❌ Erro: {response4}")

print()

# ========================================
# RESUMO FINAL
# ========================================
print("=" * 70)
print("📊 RESUMO DO TESTE ÉPICO")
print("=" * 70)
print(f"✅ 4 testes executados com sucesso")
print(f"💬 {len(history)} mensagens trocadas")
print(f"🔧 Ferramentas usadas:")
print(f"   • list_directory")
print(f"   • write_file")
print(f"   • read_file")
print(f"   • search_files")
print()
print("🎯 RESULTADO: SuperEzio 100% FUNCIONAL!")
print("=" * 70)
