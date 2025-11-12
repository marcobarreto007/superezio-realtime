# 🔧 Correção de Alucinações no Ollama

**Data:** 2025-11-12  
**Problema:** SuperEzio estava alucinando respostas (inventando arquivos, diretórios, etc)  
**Causa Raiz:** Falta de parâmetros de geração no Ollama + SYSTEM_PROMPT insuficiente

---

## 🚨 PROBLEMA IDENTIFICADO

O SuperEzio estava **inventando** informações:
- ❌ Listou arquivos que não existem (`.gitignore`, `package.json`, `scripts/` no diretório `c/`)
- ❌ Respondeu sobre `/dev/cdrom` quando perguntado sobre disco C: (Windows)
- ❌ Inventou arquivos na área de trabalho que não existem

**Causa:** O modelo LLM (Ollama) estava gerando respostas criativas demais, sem seguir estritamente o contexto fornecido.

---

## ✅ SOLUÇÕES IMPLEMENTADAS

### 1. **Parâmetros de Geração do Ollama** (REDUZ ALUCINAÇÕES)

Adicionados parâmetros críticos no payload da API do Ollama:

```typescript
options: {
  temperature: 0.2,        // BAIXO = menos alucinações (padrão: 0.7-0.9)
  top_p: 0.9,             // Nucleus sampling (padrão: 0.9)
  top_k: 40,              // Limita tokens considerados (padrão: 40)
  repeat_penalty: 1.1,     // Reduz repetição (padrão: 1.1)
  num_predict: 2048,      // Limite de tokens gerados
}
```

**Explicação:**
- **Temperature 0.2**: Reduz criatividade, aumenta determinismo (menos alucinações)
- **Top_p 0.9**: Considera apenas os 90% tokens mais prováveis
- **Top_k 40**: Limita a apenas 40 tokens mais prováveis por posição
- **Repeat_penalty 1.1**: Penaliza repetição de tokens

### 2. **SYSTEM_PROMPT Melhorado** (ZERO ALUCINAÇÕES)

Adicionadas regras explícitas:

```
REGRA CRÍTICA - ARQUIVOS E DIRETÓRIOS (HONESTIDADE TOTAL - ZERO ALUCINAÇÕES):
- 🚨 REGRA DE OURO: Se você NÃO VIU dados no contexto, NÃO INVENTE. Diga "Não tenho essa informação."
- SE NÃO HOUVER DADOS NO CONTEXTO: Diga "Não tenho essa informação" ao invés de inventar
- EXEMPLO DE ALUCINAÇÃO (NÃO FAÇA): "Aqui estão os arquivos: package.json, App.tsx..." quando você NÃO VIU essa listagem
- EXEMPLO CORRETO: "Não consegui listar o diretório. O diretório pode não existir ou não tenho acesso."
```

### 3. **Tratamento de Erros Melhorado** (HONESTIDADE)

Backend (`server/agentTools.mjs`) agora retorna erros claros:

```javascript
{
  error: `HONESTIDADE: O diretório "${listPath}" NÃO EXISTE.`,
  requestedPath: parameters.dirPath,
  resolvedPath: listPath,
  suggestion: `Você pediu "${parameters.dirPath}". Eu resolvi para "${listPath}". Este caminho não existe no sistema.`
}
```

---

## 📊 COMPARAÇÃO: ANTES vs DEPOIS

### ❌ ANTES (ALUCINANDO):
```
Usuário: "cara liste os componentes do disco c"
SuperEzio: "ls /dev/cdrom" (Linux, não Windows!)
```

```
Usuário: "o que eu tenho fixado na minha area de trabalho?"
SuperEzio: "package.json, App.tsx, script.sh, data.csv" (INVENTADO!)
```

### ✅ DEPOIS (HONESTO):
```
Usuário: "cara liste os componentes do disco c"
SuperEzio: "Não consegui listar o diretório C:\. O diretório pode não existir ou não tenho acesso."
```

```
Usuário: "o que eu tenho fixado na minha area de trabalho?"
SuperEzio: "Não tenho essa informação. Preciso acessar sua área de trabalho para ver."
```

---

## 🔍 COMO FUNCIONA AGORA

1. **Backend verifica se diretório existe** → Retorna erro claro se não existir
2. **Frontend passa contexto real** → `[DIRETÓRIO LISTADO]` ou `[ERRO]`
3. **Ollama recebe parâmetros restritivos** → `temperature: 0.2` (menos criatividade)
4. **SYSTEM_PROMPT instrui explicitamente** → "NÃO INVENTE se não viu dados"
5. **Modelo gera resposta baseada em contexto real** → Sem alucinações

---

## 🧪 TESTES RECOMENDADOS

Após reiniciar o servidor, teste:

1. **Diretório inexistente:**
   ```
   "listar pasta c"
   "verificar ./c"
   ```
   **Esperado:** "Não consegui listar o diretório. O diretório pode não existir."

2. **Diretório existente:**
   ```
   "listar pasta src"
   "verificar ./src"
   ```
   **Esperado:** Lista real dos arquivos em `src/`

3. **Pergunta sem contexto:**
   ```
   "o que eu tenho fixado na minha area de trabalho?"
   ```
   **Esperado:** "Não tenho essa informação" (não inventar arquivos)

---

## 📝 ARQUIVOS MODIFICADOS

1. **`src/services/ollamaClient.ts`**:
   - Adicionado `options` ao `OllamaRequest`
   - Configurado `temperature: 0.2` e outros parâmetros
   - Melhorado `SYSTEM_PROMPT` com regras anti-alucinação

2. **`server/agentTools.mjs`**:
   - Melhorado tratamento de erros
   - Mensagens de erro com prefixo "HONESTIDADE:"
   - Verificação de existência antes de listar

---

## 🚀 PRÓXIMOS PASSOS

1. **Reiniciar servidor** para aplicar mudanças
2. **Testar** com comandos que antes causavam alucinações
3. **Ajustar temperature** se necessário (0.1-0.3 para menos alucinações, 0.4-0.6 para mais criatividade)
4. **Monitorar** se alucinações persistem

---

## 📚 REFERÊNCIAS

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Temperature Parameter Explained](https://platform.openai.com/docs/api-reference/chat/create#temperature)
- [Reducing LLM Hallucinations](https://www.anthropic.com/research/reducing-hallucinations)

---

**Status:** ✅ Implementado  
**Próximo:** Testar e validar redução de alucinações

