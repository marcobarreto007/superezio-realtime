"""
Sistema de Métricas
Coleta métricas de performance e uso
Moved from backend/utils/metrics.py to infrastructure/observability/
"""
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import threading


@dataclass
class Metric:
    """Métrica individual"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Coletor de métricas thread-safe"""
    
    def __init__(self):
        self._metrics: List[Metric] = []
        self._counters: Dict[str, int] = defaultdict(int)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Incrementa contador"""
        with self._lock:
            if tags:
                key = f"{name}:{json.dumps(tags, sort_keys=True)}"
                self._counters[key] = self._counters.get(key, 0) + value
            else:
                self._counters[name] += value
    
    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Registra valor"""
        with self._lock:
            self._metrics.append(Metric(name, value, tags=tags or {}))
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Registra valor em histograma"""
        with self._lock:
            self._histograms[name].append(value)
    
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager para medir tempo"""
        return Timer(self, name, tags)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas agregadas"""
        with self._lock:
            aggregated_counters = defaultdict(int)
            for key, value in self._counters.items():
                base_name = key.split(':')[0]
                aggregated_counters[base_name] += value
            
            stats = {
                'counters': dict(aggregated_counters),
                'histograms': {}
            }
            
            for name, values in self._histograms.items():
                if values:
                    stats['histograms'][name] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'p50': sorted(values)[len(values) // 2],
                        'p95': sorted(values)[int(len(values) * 0.95)],
                        'p99': sorted(values)[int(len(values) * 0.99)],
                    }
            
            return stats
    
    def reset(self):
        """Limpa todas as métricas"""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._histograms.clear()


class Timer:
    """Context manager para medir tempo"""
    
    def __init__(self, collector: MetricsCollector, name: str, tags: Optional[Dict[str, str]]):
        self.collector = collector
        self.name = name
        self.tags = tags or {}
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.histogram(self.name, duration, self.tags)


# Instância global
metrics = MetricsCollector()

