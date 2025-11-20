"""
Executor de ferramentas para o SuperEzio
Executa ferramentas locais (Python) e remotas (Node.js)
"""
import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

# Ferramentas de controle de sistema (locais)
from system_control_tools import SYSTEM_CONTROL_TOOLS

# URL do servidor Express (Node.js) para ferramentas remotas
EXPRESS_API_URL = os.getenv("EXPRESS_API_URL", "http://localhost:8080")

# Registro de ferramentas locais
LOCAL_TOOLS: Dict[str, Callable[..., Any]] = {
    tool["name"]: tool["function"] for tool in SYSTEM_CONTROL_TOOLS
}

def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa uma ferramenta. Verifica primeiro se é uma ferramenta local (Python),
    se não, delega para o servidor remoto (Node.js).
    """
    if tool_name in LOCAL_TOOLS:
        # Executar ferramenta localmente
        print(f"   🐍 Executing local Python tool: {tool_name}")
        try:
            func = LOCAL_TOOLS[tool_name]
            result = func(**parameters)
            return {"success": True, "result": result}
        except Exception as e:
            print(f"      ❌ Local tool failed: {e}")
            return {"success": False, "error": str(e)}
    else:
        # Executar ferramenta remota via servidor Express
        print(f"   🌐 Executing remote Node.js tool: {tool_name}")
        return execute_remote_tool(tool_name, parameters)

def execute_remote_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa uma ferramenta via servidor Express (Node.js).
    """
    try:
        mapped_params = _map_parameters(tool_name, parameters)
        
        response = requests.post(
            f"{EXPRESS_API_URL}/api/agent/tools/execute",
            json={
                "toolName": tool_name,
                "parameters": mapped_params,
                "confirmed": True
            },
            timeout=30
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
            "error": f"Servidor Express não está rodando em {EXPRESS_API_URL}."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao executar ferramenta remota: {str(e)}"
        }

def _map_parameters(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Mapeia parâmetros do formato Python para Node.js."""
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
    return parameters

def resolve_desktop_path() -> Path:
    """Resolve o caminho do Desktop do usuário atual."""
    desktop = Path.home() / "Desktop"
    return desktop if desktop.exists() else Path.home()

def process_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Processa múltiplas chamadas de ferramentas e retorna resultados."""
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        parameters = tool_call.get("parameters", {})
        
        print(f"   🔧 Executando: {tool_name} com parâmetros: {parameters}")
        
        # Lógica de resolução de caminho (mantida)
        path_keys = ["path", "searchPath", "dirPath", "filePath"]
        for path_key in path_keys:
            if path_key in parameters:
                path_value = str(parameters[path_key])
                if path_value.startswith("~/") or path_value.startswith("~\\"):
                    rest_of_path = path_value[2:]
                    parameters[path_key] = str(Path.home() / rest_of_path)
                elif "desktop" in path_value.lower() and not Path(path_value).is_absolute():
                     parameters[path_key] = str(resolve_desktop_path())

        # Executar a ferramenta (agora usa o dispatcher híbrido)
        result = execute_tool(tool_name, parameters)
        results.append({
            "tool": tool_name,
            "parameters": parameters,
            "result": result
        })
        
        if result.get("success"):
            print(f"      ✅ {tool_name} executado com sucesso")
        else:
            print(f"      ❌ {tool_name} falhou: {result.get('error')}")
    
    return results

