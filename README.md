# SuperEzio Realtime

Um frontend de chat moderno, limpo e responsivo, construído para interagir com o modelo Qwen2.5-7B-Instruct rodando 100% local via Hugging Face.

Este projeto foi completamente reestruturado para ter uma arquitetura clara, uma interface de usuário moderna e uma integração com backend Python FastAPI para inferência GPU local.

## ✨ Features

-   Interface de chat fullscreen e responsiva.
-   Estilização moderna com **Tailwind CSS**.
-   Bolhas de mensagem distintas para usuário e assistente.
-   Indicador de "digitando" enquanto o bot processa a resposta.
-   Scroll automático para a mensagem mais recente.
-   Lógica de envio com "Enter" (Shift+Enter para nova linha).
-   Arquitetura baseada em componentes com React e hooks.

## 🚀 Como Rodar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/marcobarreto007/superezio-realtime.git
    cd superezio-realtime
    ```

2.  **Instale as dependências:**
    ```bash
    npm install
    ```

3.  **Configure as variáveis de ambiente:**
    -   Não é mais necessário configurar `.env.local`
    -   O backend Python usa o modelo local em `models/qwen2.5-7b-instruct/`

4.  **Inicie o servidor de desenvolvimento:**
    ```bash
    npm run dev
    ```

    Abra [http://localhost:3000](http://localhost:3000) no seu navegador para ver o projeto.

## 🛠️ Tech Stack

-   **Framework:** React 18
-   **Linguagem:** TypeScript
-   **Build Tool:** Vite
-   **Estilização:** Tailwind CSS
-   **IA Backend:** Python FastAPI + Hugging Face Transformers (Qwen2.5-7B-Instruct)

---
*Este projeto foi refatorado com a assistência do Gemini CLI.*