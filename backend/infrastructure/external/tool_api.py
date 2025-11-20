"""
Tool API Client
Cliente HTTP para executar tools via servidor Express (Node.js)
Moved from backend/tool_executor.py to infrastructure/external/
"""
import os
import requests
from typing import Dict, Any
from infrastructure.config.settings import get_settings


settings = get_settings()
EXPRESS_API_URL = settings.express_api_url
TOOL_TIMEOUT = settings.tool_timeout


def execute_tool_http(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa uma ferramenta via servidor Express (Node.js).
    
    Args:
        tool_name: Nome da ferramenta (ex: "search_files", "read_file")
        parameters: Parâmetros da ferramenta
        
    Returns:
        Resultado da execução da ferramenta
    """
    try:
        # Mapear nomes de parâmetros do formato Python para Node.js
        mapped_params = _map_parameters(tool_name, parameters)
        
        # Chamar servidor Express
        response = requests.post(
            f"{EXPRESS_API_URL}/api/agent/tools/execute",
            json={
                "toolName": tool_name,
                "parameters": mapped_params,
                "confirmed": True  # Auto-confirmar para não bloquear
            },
            timeout=TOOL_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "result": result.get("result"),
                "error": result.get("error")
            }
        else:
            return {
                "success": False,
                "error": f"Erro HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Servidor Express não está rodando em {EXPRESS_API_URL}. Certifique-se de que o servidor Node.js está ativo."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao executar ferramenta: {str(e)}"
        }


def _map_parameters(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeia parâmetros do formato Python (tools_config.py) para formato Node.js (agentTools.ts).
    """
    mapping = {
        "read_file": {"path": "filePath"},
        "write_file": {"path": "filePath", "content": "content"},
        "delete_file": {"path": "filePath"},
        "get_file_info": {"path": "filePath"},
        "list_directory": {"path": "dirPath"},
        "create_directory": {"path": "dirPath"},
        "search_files": {"path": "searchPath", "pattern": "pattern"},
    }
    
    if tool_name in mapping:
        mapped = {}
        for py_key, node_key in mapping[tool_name].items():
            if py_key in parameters:
                mapped[node_key] = parameters[py_key]
        return mapped
    
    # Se não houver mapeamento, retornar como está
    return parameters

