"""
Error Handling Middleware
Tratamento robusto de erros com fallbacks
Updated to use new infrastructure imports
"""
import traceback
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from infrastructure.observability.logger import app_logger, model_logger, tool_logger, rag_logger
from infrastructure.observability.metrics import metrics


class ErrorHandler:
    """Handler centralizado de erros"""
    
    @staticmethod
    async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handler genérico de exceções"""
        error_id = f"ERR_{id(exc)}"
        
        # Log estruturado
        app_logger.error(
            "Unhandled exception",
            error_id=error_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
            method=request.method,
            traceback=traceback.format_exc()
        )
        
        # Métricas
        metrics.increment("errors.total", tags={"type": type(exc).__name__})
        
        # Resposta amigável
        status_code = 500
        if isinstance(exc, HTTPException):
            status_code = exc.status_code
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": "Internal server error",
                "error_id": error_id,
                "message": str(exc) if isinstance(exc, HTTPException) else "An unexpected error occurred",
                "type": type(exc).__name__
            }
        )
    
    @staticmethod
    def handle_model_error(exc: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handler específico para erros de modelo"""
        model_logger.error(
            "Model error",
            error_type=type(exc).__name__,
            error_message=str(exc),
            context=context or {}
        )
        
        metrics.increment("errors.model")
        
        return {
            "error": "Model inference failed",
            "message": "The AI model encountered an error. Please try again.",
            "retryable": True
        }
    
    @staticmethod
    def handle_tool_error(exc: Exception, tool_name: str) -> Dict[str, Any]:
        """Handler específico para erros de ferramentas"""
        tool_logger.error(
            "Tool error",
            tool_name=tool_name,
            error_type=type(exc).__name__,
            error_message=str(exc)
        )
        
        metrics.increment("errors.tools", tags={"tool": tool_name})
        
        return {
            "error": f"Tool '{tool_name}' failed",
            "message": f"The tool '{tool_name}' encountered an error.",
            "retryable": True
        }
    
    @staticmethod
    def handle_rag_error(exc: Exception) -> Dict[str, Any]:
        """Handler específico para erros de RAG"""
        rag_logger.error(
            "RAG error",
            error_type=type(exc).__name__,
            error_message=str(exc)
        )
        
        metrics.increment("errors.rag")
        
        # RAG errors são não-críticos, retornar fallback
        return {
            "error": "RAG service unavailable",
            "message": "Knowledge retrieval failed, continuing without RAG context.",
            "fallback": True
        }
