"""
Health Check Avançado
Verifica saúde de todos os componentes do sistema
"""
import time
import torch
from typing import Dict, Any, Optional
from pathlib import Path
from utils.metrics import metrics
from utils.logger import app_logger
from model_registry import LOCAL_MODEL_PATH, DEVICE


class HealthChecker:
    """Verificador de saúde do sistema"""
    
    def __init__(self):
        self._last_check: Optional[float] = None
        self._cache_ttl = 5.0  # Cache health check por 5 segundos
    
    def check_all(self) -> Dict[str, Any]:
        """Verifica saúde de todos os componentes"""
        now = time.time()
        
        # Usar cache se disponível
        if self._last_check and (now - self._last_check) < self._cache_ttl:
            return self._cached_health
        
        health = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }
        
        # Verificar modelo
        model_health = self._check_model()
        health["components"]["model"] = model_health
        
        # Verificar GPU
        gpu_health = self._check_gpu()
        health["components"]["gpu"] = gpu_health
        
        # Verificar disco
        disk_health = self._check_disk()
        health["components"]["disk"] = disk_health
        
        # Verificar memória
        memory_health = self._check_memory()
        health["components"]["memory"] = memory_health
        
        # Status geral
        all_healthy = all(
            comp.get("status") == "healthy" 
            for comp in health["components"].values()
        )
        health["status"] = "healthy" if all_healthy else "degraded"
        
        self._last_check = now
        self._cached_health = health
        
        return health
    
    def _check_model(self) -> Dict[str, Any]:
        """Verifica se modelo está disponível"""
        try:
            exists = LOCAL_MODEL_DIR.exists()
            return {
                "status": "healthy" if exists else "unhealthy",
                "path": str(LOCAL_MODEL_DIR),
                "exists": exists
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _check_gpu(self) -> Dict[str, Any]:
        """Verifica saúde da GPU"""
        try:
            if not torch.cuda.is_available():
                return {
                    "status": "unavailable",
                    "available": False
                }
            
            gpu_count = torch.cuda.device_count()
            gpu_info = []
            
            for i in range(gpu_count):
                props = torch.cuda.get_device_properties(i)
                memory_total = props.total_memory / (1024**3)  # GB
                memory_allocated = torch.cuda.memory_allocated(i) / (1024**3)
                memory_reserved = torch.cuda.memory_reserved(i) / (1024**3)
                memory_free = memory_total - memory_reserved
                
                gpu_info.append({
                    "id": i,
                    "name": props.name,
                    "memory_total_gb": round(memory_total, 2),
                    "memory_allocated_gb": round(memory_allocated, 2),
                    "memory_reserved_gb": round(memory_reserved, 2),
                    "memory_free_gb": round(memory_free, 2),
                    "utilization_percent": round((memory_reserved / memory_total) * 100, 1)
                })
            
            # Status baseado em memória livre
            min_free_gb = 2.0  # Mínimo necessário
            all_healthy = all(g["memory_free_gb"] >= min_free_gb for g in gpu_info)
            
            return {
                "status": "healthy" if all_healthy else "degraded",
                "available": True,
                "device_count": gpu_count,
                "devices": gpu_info
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _check_disk(self) -> Dict[str, Any]:
        """Verifica espaço em disco"""
        try:
            import shutil
            disk_usage = shutil.disk_usage(LOCAL_MODEL_DIR)
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Alertar se menos de 10GB livres
            status = "healthy" if free_gb >= 10 else "degraded"
            
            return {
                "status": status,
                "total_gb": round(total_gb, 2),
                "free_gb": round(free_gb, 2),
                "used_percent": round(used_percent, 1)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Verifica memória RAM"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            
            status = "healthy"
            if mem.percent > 90:
                status = "degraded"
            elif mem.percent > 95:
                status = "unhealthy"
            
            return {
                "status": status,
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_percent": mem.percent
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Instância global
health_checker = HealthChecker()

