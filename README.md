# SuperEzio Realtime (Multi-LoRA Edition)

O **SuperEzio Realtime** é um assistente de IA local de alta performance, projetado para privacidade, velocidade e utilidade real.

Diferente de chatbots comuns, ele opera como um **Agente de Sistema**, capaz de interagir com seus arquivos, e-mails e dados, tudo rodando 100% localmente na sua GPU.

![Status](https://img.shields.io/badge/Status-Active-green)
![Model](https://img.shields.io/badge/Model-Qwen2.5--7B-blue)
![Tech](https://img.shields.io/badge/Tech-Multi--LoRA-purple)

## ✨ Destaques

*   **🧠 Cérebro Multi-LoRA:** Usa múltiplos adaptadores "Experts" (Personalidade, Contabilidade, etc.) simultaneamente sobre um modelo base Qwen2.5-7B.
*   **🛡️ 100% Local e Privado:** Nenhum dado sai da sua máquina. Inferência acelerada por GPU (CUDA).
*   **🛠️ Agente Real:** Capaz de ler/escrever arquivos, gerenciar pastas e ler e-mails (com sua permissão expressa).
*   **⚡ Interface Moderna:** Frontend React reativo, com streaming de tokens em tempo real e highlight de sintaxe.

## 🚀 Início Rápido

### Pré-requisitos
*   NVIDIA GPU com drivers atualizados (recomendado 6GB+ VRAM).
*   Node.js 18+ e Python 3.10+.

### Instalação

1.  **Clone e Instale:**
    ```bash
    git clone https://github.com/marcobarreto007/superezio-realtime.git
    cd superezio-realtime
    npm install
    ```

2.  **Backend Python (Venv):**
    ```bash
    cd backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    # Se necessário, instale PyTorch com CUDA:
    # pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```

3.  **Modelos:**
    Certifique-se de que o modelo `qwen2.5-7b-instruct` está em `models/`.
    (Use `scripts/download_model.py` se necessário).

### Rodando

Use o script mestre para iniciar tudo (Backend Python, Servidor Node e Frontend):

```bash
# Windows
start_all.bat
```

Acesse **http://localhost:3000**.

## 📚 Documentação

A documentação completa foi reorganizada em `docs/`:

*   [**Arquitetura Técnica**](docs/ARCHITECTURE.md): Entenda como o Multi-LoRA e o Agente funcionam.
*   [**Guia de Uso**](docs/usage/COMO_USAR_BACKEND.md): Como interagir com o bot.
*   [**Guia de Setup**](docs/setup/COMO_INICIAR_SERVIDORES.md): Detalhes de instalação e solução de problemas.

## 🛠️ Estrutura do Projeto

*   `backend/`: API de Inferência Python (FastAPI + Transformers).
*   `server/`: Servidor Intermediário Node.js (Express + Ferramentas de Sistema).
*   `src/`: Frontend React (Chat Interface).
*   `models/`: Armazenamento local de modelos e LoRAs.

---
*Desenvolvido por Marco Barreto.*
