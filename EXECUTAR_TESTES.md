# 🧪 Como Executar os Testes

## Pré-requisitos

1. **Servidor rodando**: O backend Python deve estar em execução
   ```bash
   .\start_backend_python.bat
   ```

2. **Aguardar inicialização**: Aguarde o modelo carregar (1-2 minutos)

## Testes Disponíveis

### 1. Teste Rápido (`test_quick.py`)
Teste rápido que valida funcionalidades básicas:
- Health check
- Métricas
- Chat básico
- RAG injection

**Executar:**
```bash
cd backend
python test_quick.py
```

### 2. Teste Completo (`test_system_completo.py`)
Teste completo que valida todas as melhorias:
- Health checks (básico e detalhado)
- Métricas
- Chat básico
- RAG injection
- Rate limiting
- Prompt cache
- Error handling
- Mode routing

**Executar:**
```bash
cd backend
python test_system_completo.py
```

### 3. Teste com Aguardo (`test_and_wait.py`)
Aguarda servidor estar pronto e executa testes completos:

**Executar:**
```bash
cd backend
python test_and_wait.py
```

## Resultados

Os resultados são salvos em:
- `backend/test_results.json` - Resultados detalhados em JSON

## Interpretação dos Resultados

- ✅ **PASS**: Teste passou com sucesso
- ⚠️ **WARN**: Teste passou mas com avisos (pode ser esperado)
- ❌ **FAIL**: Teste falhou

## Troubleshooting

### Servidor não está respondendo
```bash
# Verificar se está rodando
curl http://localhost:8000/health

# Iniciar servidor
.\start_backend_python.bat
```

### Erro de conexão
- Verifique se a porta 8000 está livre
- Verifique se o servidor está realmente rodando
- Aguarde alguns segundos após iniciar o servidor

### Testes falhando
- Verifique os logs do servidor
- Certifique-se de que o modelo está carregado
- Verifique se há erros no console do servidor

