# 🧪 Guia de Testes - Agente de Sistema SuperEzio

**Como testar todas as funcionalidades do agente de sistema**

---

## 🚀 COMO INICIAR

### 1. Iniciar o servidor
```bash
npm run dev
```

### 2. Abrir no navegador
```
http://localhost:3000
```

---

## 📋 TESTES POR FUNCIONALIDADE

### 1. **LER ARQUIVO** 📖

**Comandos para testar:**
```
"ler arquivo: package.json"
"mostrar conteúdo de package.json"
"ler package.json"
"abrir arquivo: src/App.tsx"
```

**O que deve acontecer:**
- ✅ SuperEzio lê o arquivo automaticamente
- ✅ Mostra o conteúdo no chat
- ✅ Não pede confirmação (só leitura)

**Exemplo esperado:**
```
SuperEzio: [Conteúdo do arquivo package.json]:
{
  "name": "superezio-realtime",
  ...
}
```

---

### 2. **ESCREVER ARQUIVO** ✏️

**Comandos para testar:**
```
"escrever arquivo: teste.txt com conteúdo: Olá mundo"
"criar arquivo: script.ps1 com: Get-Process"
"escreva arquivo: dados.json com: {"nome": "Marco"}"
```

**O que deve acontecer:**
- ✅ Modal de confirmação aparece
- ✅ Mostra o que vai ser escrito
- ✅ Você clica "Confirmar (OK)"
- ✅ Arquivo é criado

**Exemplo esperado:**
```
[Modal aparece]
"Confirmação Necessária
Escrever arquivo: teste.txt
[Preview do conteúdo]
[Botão Confirmar] [Botão Cancelar]
```

---

### 3. **LISTAR DIRETÓRIO** 📁

**Comandos para testar:**
```
"listar pasta: ./src"
"mostrar arquivos em ./src/components"
"listar diretório: C:\Users\marco"
```

**O que deve acontecer:**
- ✅ Lista arquivos e pastas
- ✅ Mostra tamanho e data de modificação
- ✅ Não pede confirmação

**Exemplo esperado:**
```
SuperEzio: [Arquivos em ./src]:
- App.tsx (arquivo, 2.5 KB)
- components/ (diretório)
- services/ (diretório)
...
```

---

### 4. **BUSCAR ARQUIVOS** 🔍

**Comandos para testar:**
```
"buscar arquivo: *.ts em ./src"
"procurar arquivo: package.json"
"encontrar arquivo: config"
```

**O que deve acontecer:**
- ✅ Busca recursiva
- ✅ Retorna lista de arquivos encontrados
- ✅ Não pede confirmação

---

### 5. **CRIAR TABELA** 📊

**Comandos para testar:**
```
"criar tabela HTML com dados: [{'nome': 'Marco', 'idade': 30}, {'nome': 'Ana', 'idade': 28}]"
"gerar CSV com: [{'produto': 'A', 'preco': 10}, {'produto': 'B', 'preco': 20}]"
```

**O que deve acontecer:**
- ✅ Modal de confirmação
- ✅ Cria tabela HTML ou CSV
- ✅ Pode salvar em arquivo

---

### 6. **CRIAR AGENDA** 📅

**Comandos para testar:**
```
"escreva agenda"
"criar agenda"
"faz uma agenda"
```

**O que deve acontecer:**
- ✅ Modal de confirmação
- ✅ Cria `agenda.md` automaticamente
- ✅ Template com data atual

**Exemplo esperado:**
```
[Modal]
"Confirmação Necessária
Escrever arquivo: agenda.md
[Preview do conteúdo da agenda]
```

---

### 7. **DELETAR ARQUIVO** 🗑️

**Comandos para testar:**
```
"deletar arquivo: teste.txt"
"apagar: arquivo_antigo.txt"
```

**O que deve acontecer:**
- ✅ Modal de confirmação (OBRIGATÓRIO)
- ✅ Mostra o que vai ser deletado
- ✅ Só deleta se você confirmar

---

## 🧪 TESTE COMPLETO (SEQUÊNCIA)

### Teste 1: Criar e Ler
```
1. "criar arquivo: teste.txt com conteúdo: Teste do SuperEzio"
   → Confirmar
   → Verificar se arquivo foi criado

2. "ler arquivo: teste.txt"
   → Deve mostrar o conteúdo que você escreveu
```

### Teste 2: Listar e Buscar
```
1. "listar pasta: ./src"
   → Deve listar todos os arquivos

2. "buscar arquivo: *.tsx em ./src"
   → Deve encontrar todos os arquivos .tsx
```

### Teste 3: Agenda
```
1. "escreva agenda"
   → Confirmar
   → Verificar se agenda.md foi criado

2. "ler agenda"
   → Deve mostrar o conteúdo da agenda
```

---

## 🔍 VERIFICAÇÃO MANUAL

### Verificar se arquivo foi criado:
```powershell
# No PowerShell
Get-Content teste.txt
# ou
type teste.txt
```

### Verificar se arquivo existe:
```powershell
Test-Path teste.txt
# Retorna: True ou False
```

### Listar arquivos criados:
```powershell
Get-ChildItem -Filter "*.txt"
Get-ChildItem -Filter "agenda.md"
```

---

## ⚠️ TROUBLESHOOTING

### Problema: Modal não aparece
**Solução:**
- Verifique se o servidor está rodando
- Abra o console do navegador (F12)
- Procure por erros

### Problema: Arquivo não é criado
**Solução:**
- Verifique permissões da pasta
- Veja logs do servidor (terminal)
- Verifique se confirmou a ação

### Problema: Erro 500
**Solução:**
- Verifique se `server.mjs` está rodando
- Veja logs do servidor
- Verifique se `fs-extra` está instalado

---

## 📊 CHECKLIST DE TESTES

```
□ Ler arquivo existente
□ Criar arquivo novo
□ Listar diretório
□ Buscar arquivos
□ Criar tabela HTML
□ Criar tabela CSV
□ Criar agenda
□ Ler agenda criada
□ Deletar arquivo (com confirmação)
□ Verificar que arquivos foram criados no sistema
```

---

## 🎯 TESTE RÁPIDO (1 MINUTO)

Execute estes 3 comandos:

```
1. "escreva agenda"
   → Confirmar

2. "ler agenda"
   → Deve mostrar a agenda criada

3. "listar pasta: ."
   → Deve listar agenda.md na lista
```

Se os 3 funcionarem, o agente está OK! ✅

---

*Criado em 2025-11-12*

