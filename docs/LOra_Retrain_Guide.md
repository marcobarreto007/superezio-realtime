## SuperEzio LoRA – Processo de Atualização

### 1. Gerar/atualizar dataset expandido
- Edite o conteúdo em `scripts/build_extended_persona_dataset.py` se precisar ajustar exemplos.
- Rodar `python3 scripts/build_extended_persona_dataset.py`.
- Saída esperada: `data/persona_superezio_expanded.jsonl` com ~140 exemplos.

### 2. Conferir arquivo
- `wc -l data/persona_superezio_expanded.jsonl` → deve retornar 100-150 linhas.
- `head`/`tail` para garantir mensagens no formato `[system,user,assistant]`.

### 3. Treinar o LoRA
- Certifique-se de que o modelo base existe em `models/qwen2.5-7b-instruct`.
- Com CUDA disponível: `python3 scripts/train_lora.py`.
- O script detecta automaticamente o dataset expandido; para sobrescrever use `PERSONA_DATA_PATH=/caminho/arquivo.jsonl python3 scripts/train_lora.py`.
- Checkpoints e adapter final são salvos em `models/lora_superezio`.

### 4. Validar
- Rode `python3 backend/test_quick.py` para validação rápida de carregamento.
- Inicie o backend (`start_backend_python.bat` ou `python3 backend/api.py`) e faça perguntas sobre: personalidade, família, Oilers, saúde (somente quando solicitado).
- Confirmar que respostas usam o novo contexto sem alterar o fluxo existente (FastAPI → Express → Frontend).

### 5. Rollback
- Caso queira voltar ao dataset antigo, defina `PERSONA_DATA_PATH=data/persona_superezio.jsonl` antes do treino.
