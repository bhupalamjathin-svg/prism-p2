import time
from typing import Dict, Any, Optional, Tuple
from .models import TroubleshootingPlanResponse

class FastPathCache:
    """
    Sub-300ms Fast-Path Semantic Cache.
    Keys on: canonical_id:device_model:one_ui_version
    Guarantees sub-millisecond in-memory resolution for repeat scenarios.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[float, TroubleshootingPlanResponse]] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
            "total_hit_latency_ms": 0.0
        }

    def generate_key(self, canonical_id: str, model: str, one_ui_version: str) -> str:
        clean_id = canonical_id.strip().lower()
        clean_model = model.strip().lower().replace(" ", "_")
        clean_version = one_ui_version.strip().lower()
        return f"{clean_id}:{clean_model}:{clean_version}"

    def get(self, canonical_id: str, model: str, one_ui_version: str) -> Optional[TroubleshootingPlanResponse]:
        key = self.generate_key(canonical_id, model, one_ui_version)
        self.stats["total_queries"] += 1
        start_t = time.perf_counter()

        if key in self._cache:
            created_at, plan = self._cache[key]
            if (time.time() - created_at) < self.ttl_seconds:
                hit_latency = (time.perf_counter() - start_t) * 1000.0
                self.stats["hits"] += 1
                self.stats["total_hit_latency_ms"] += hit_latency

                # Clone plan with updated latency & cache hit metadata
                plan_copy = plan.model_copy(deep=True)
                plan_copy.cache_hit = True
                plan_copy.latency_ms = round(hit_latency, 3)
                return plan_copy
            else:
                del self._cache[key]

        self.stats["misses"] += 1
        return None

    def set(self, canonical_id: str, model: str, one_ui_version: str, plan: TroubleshootingPlanResponse) -> None:
        key = self.generate_key(canonical_id, model, one_ui_version)
        self._cache[key] = (time.time(), plan)

    def get_metrics(self) -> Dict[str, Any]:
        total = self.stats["total_queries"]
        hits = self.stats["hits"]
        hit_rate = (hits / total) if total > 0 else 0.0
        avg_hit_latency = (
            (self.stats["total_hit_latency_ms"] / hits) if hits > 0 else 0.0
        )
        return {
            "total_queries": total,
            "cache_hits": hits,
            "cache_misses": self.stats["misses"],
            "hit_rate_percentage": round(hit_rate * 100, 2),
            "cached_entries_count": len(self._cache),
            "avg_cache_hit_latency_ms": round(avg_hit_latency, 3),
            "sla_target_ms": 300.0,
            "sla_compliance": avg_hit_latency < 300.0
        }

    def clear(self) -> None:
        self._cache.clear()
