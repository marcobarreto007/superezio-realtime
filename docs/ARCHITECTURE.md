# Arquitetura SuperEzio Realtime

Este documento descreve a arquitetura técnica do SuperEzio, um assistente de IA local avançado que combina inferência GPU de alta performance com capacidades de agente de sistema seguro.

## 🏗️ Visão Geral

O sistema opera em uma arquitetura híbrida **Python + Node.js + React**:

```mermaid
graph TD
    User[Usuário] <--> Frontend[Frontend React (Vite)]
    Frontend <--> Node[Node.js Server (Express)]
    Frontend <--> Python[Python FastAPI (Inference)]

    Node -- Filesystem/Email --> OS[Sistema Operacional]
    Python -- Multi-LoRA --> GPU[NVIDIA GPU]
```

### 1. Python FastAPI (O "Cérebro")
*   **Responsabilidade:** Inferência de IA pura.
*   **Modelo:** `Qwen2.5-7B-Instruct` (Quantizado 4-bit NF4).
*   **Especialização:** Usa **Multi-LoRA** para carregar múltiplos adaptadores ("Experts") simultaneamente:
    *   `lora_personality_v2`: Personalidade, tom de voz, anti-overfit.
    *   `lora_accounting`: Conhecimento especializado (ex: Contabilidade Canadense).
*   **Engine:** Hugging Face Transformers + BitsAndBytes + Optimum BetterTransformer.
*   **Localização:** `backend/`

### 2. Node.js Express (As "Mãos")
*   **Responsabilidade:** Execução de ferramentas e Proxy.
*   **Agente de Sistema:** Expõe uma API segura (`/api/agent`) para manipular arquivos, pastas e e-mails.
*   **Segurança:** Implementa confirmação humana obrigatória (`requiresConfirmation: true`) para ações destrutivas (escrita/deleção).
*   **Proxy:** Redireciona chamadas de inferência (`/api/hf`) para o backend Python, lidando com timeouts longos.
*   **Localização:** `server.ts` e `server/`

### 3. Frontend React (A "Interface")
*   **Responsabilidade:** Interface de Chat, Gerenciamento de Estado e Orquestração.
*   **Orquestração:**
    1. Envia prompt do usuário para o Python.
    2. Recebe intenção de uso de ferramenta (`tool_calls`).
    3. Solicita confirmação do usuário (se necessário).
    4. Executa a ferramenta via Node.js.
    5. (Futuro) Retorna o resultado para o Python para resposta final.
*   **Tecnologias:** React 18, Vite, Tailwind CSS, Lucide React.
*   **Localização:** `src/`

---

## 🧠 Sistema Multi-LoRA (Mixture of Experts Lite)

Diferente de modelos monolíticos, o SuperEzio carrega adaptadores leves (Low-Rank Adapters) sobre o modelo base congelado.

**Benefícios:**
1.  **Memória:** Consome apenas ~6GB VRAM (vs 14GB+ de modelos maiores).
2.  **Modularidade:** Permite "ligar/desligar" habilidades (Personalidade, Contabilidade, Coding) sem retreinar o modelo base.
3.  **Performance:** Otimizado com `BetterTransformer` para inferência rápida (~30-50 tokens/s).

---

## 🛠️ Ferramentas do Agente (Agent Tools)

O sistema implementa o protocolo de **Function Calling**. O modelo sabe *quais* ferramentas existem, mas não as executa diretamente.

**Fluxo de Execução:**
1.  **Definição:** `backend/tools_config.py` define as assinaturas JSON para o LLM.
2.  **Decisão:** O LLM decide chamar uma tool e retorna um JSON estruturado.
3.  **Execução:** O Node.js (`server/agentTools.ts`) executa a ação real no SO.

**Lista de Ferramentas:**
*   `read_file`, `write_file`, `delete_file`
*   `list_directory`, `create_directory`, `search_files`
*   `create_table` (HTML/CSV)
*   `read_emails`, `search_emails`

---

## 🚀 Como Contribuir

1.  **Python:** Alterações em `backend/` requerem reinício do servidor Python.
2.  **Node:** `server.ts` usa `tsx watch` para reload automático.
3.  **Frontend:** Vite com HMR instantâneo.

Para atualizar a documentação de ferramentas, altere tanto `backend/tools_config.py` (definição) quanto `server/agentTools.ts` (implementação).
