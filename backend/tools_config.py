"""
Lista de ferramentas disponíveis para o SuperEzio.
Mantém o mesmo conjunto usado anteriormente no frontend, agora visível apenas pelo backend/modelo.
"""
from __future__ import annotations
from typing import Any, Dict, List
from system_control_tools import SYSTEM_CONTROL_TOOLS

Tool = Dict[str, Any]

# Ferramentas existentes
EXISTING_TOOLS: List[Tool] = [
    # === FILE OPERATIONS (4) ===
    {
        "name": "read_file",
        "description": "Lê o conteúdo completo de um arquivo do sistema",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho absoluto do arquivo a ser lido",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Escreve conteúdo em um arquivo (cria ou sobrescreve)",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho absoluto do arquivo",
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo a ser escrito",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "delete_file",
        "description": "Deleta um arquivo do sistema",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho absoluto do arquivo a deletar",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "get_file_info",
        "description": "Obtém informações sobre um arquivo (tamanho, data modificação, etc)",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho absoluto do arquivo",
                }
            },
            "required": ["path"],
        },
    },
    # === DIRECTORY OPERATIONS (3) ===
    {
        "name": "list_directory",
        "description": "Lista todos os arquivos e subdiretórios de um diretório",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho absoluto do diretório",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "create_directory",
        "description": "Cria um novo diretório (e subdiretórios se necessário)",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho absoluto do diretório a criar",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_files",
        "description": "Busca arquivos por padrão (glob pattern ou extensão)",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Diretório raiz para busca",
                },
                "pattern": {
                    "type": "string",
                    "description": 'Padrão de busca (ex: "*.py", "test_*")',
                },
            },
            "required": ["path", "pattern"],
        },
    },
    # === DATA OPERATIONS (1) ===
    {
        "name": "create_table",
        "description": "Cria uma tabela formatada a partir de dados estruturados",
        "parameters": {
            "type": "object",
            "properties": {
                "headers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Cabeçalhos das colunas",
                },
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "description": "Linhas da tabela",
                },
            },
            "required": ["headers", "rows"],
        },
    },
    # === EMAIL OPERATIONS (3) ===
    {
        "name": "read_emails",
        "description": "Lê emails da caixa de entrada (últimos N emails)",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "number",
                    "description": "Número máximo de emails a retornar",
                    "default": 10,
                },
                "folder": {
                    "type": "string",
                    "description": "Pasta a verificar (inbox, sent, etc)",
                    "default": "inbox",
                },
            },
            "required": [],
        },
    },
    {
        "name": "search_emails",
        "description": "Busca emails por critérios (remetente, assunto, conteúdo, data)",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo de busca",
                },
                "field": {
                    "type": "string",
                    "enum": ["from", "subject", "body", "all"],
                    "description": "Campo onde buscar",
                },
                "limit": {
                    "type": "number",
                    "description": "Máximo de resultados",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_unread_count",
        "description": "Retorna o número de emails não lidos",
        "parameters": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "Pasta a verificar",
                    "default": "inbox",
                }
            },
            "required": [],
        },
    },
    # === WEATHER/EXTERNAL DATA (1) ===
    {
        "name": "get_weather",
        "description": "Busca informações de clima/tempo para uma localidade e data específica. OBRIGATÓRIO usar antes de responder perguntas sobre clima. Se não houver API configurada, retorna erro indicando que não há acesso a dados de clima em tempo real.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Nome da cidade/localidade (ex: 'Lévis, Canada', 'Montreal', 'São Paulo')",
                },
                "date": {
                    "type": "string",
                    "description": "Data para a previsão (ex: 'amanhã', '2024-12-25', 'hoje'). Se não especificado, assume 'hoje'",
                    "default": "hoje",
                },
            },
            "required": ["location"],
        },
    },
]

# Combinar ferramentas existentes com as novas de controle do sistema
AVAILABLE_TOOLS: List[Tool] = EXISTING_TOOLS + SYSTEM_CONTROL_TOOLS

