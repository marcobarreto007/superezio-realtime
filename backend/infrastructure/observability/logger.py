"""
Structured Logging
Logs consistentes e parseáveis para análise
Moved from backend/utils/logger.py to infrastructure/observability/
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
from infrastructure.config.settings import get_settings


settings = get_settings()


class StructuredLogger:
    """Logger estruturado com JSON output"""
    
    def __init__(self, name: str, log_file: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        
        # Formatter JSON
        if log_file:
            log_path = settings.log_dir / log_file
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_path, encoding='utf-8')
        else:
            handler = logging.StreamHandler(sys.stdout)
        
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        self.logger.propagate = False
    
    def log(self, level: str, message: str, **kwargs):
        """Log estruturado"""
        extra = {
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def info(self, message: str, **kwargs):
        self.log('info', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log('error', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log('warning', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log('debug', message, **kwargs)


class JSONFormatter(logging.Formatter):
    """Formatter que produz JSON estruturado"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Adicionar campos extras
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'message', 'pathname', 'process',
                          'processName', 'relativeCreated', 'thread', 'threadName',
                          'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


# Loggers globais
app_logger = StructuredLogger('superezio.app')
rag_logger = StructuredLogger('superezio.rag')
tool_logger = StructuredLogger('superezio.tools')
model_logger = StructuredLogger('superezio.model')

