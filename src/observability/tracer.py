import time
import uuid
import functools
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel, Field

class StepTelemetry(BaseModel):
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)

class PipelineTracer:
    """Unified telemetry tracer for an end-to-end request pipeline."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or f"tr-{uuid.uuid4().hex[:8]}"
        self.start_time = time.perf_counter()
        self.steps: Dict[str, StepTelemetry] = {}

    def record_step(
        self,
        step_name: str,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        estimated_cost_usd: float = 0.0,
        details: Optional[Dict[str, Any]] = None
    ):
        step = self.steps.get(step_name, StepTelemetry())
        step.latency_ms += latency_ms
        step.prompt_tokens += prompt_tokens
        step.completion_tokens += completion_tokens
        step.estimated_cost_usd += estimated_cost_usd
        if details:
            step.details.update(details)
        self.steps[step_name] = step

    def get_summary(self) -> Dict[str, Any]:
        total_latency = (time.perf_counter() - self.start_time) * 1000.0
        total_prompt_tokens = sum(s.prompt_tokens for s in self.steps.values())
        total_completion_tokens = sum(s.completion_tokens for s in self.steps.values())
        total_cost = sum(s.estimated_cost_usd for s in self.steps.values())
        
        return {
            "trace_id": self.trace_id,
            "total_latency_ms": round(total_latency, 2),
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_estimated_cost_usd": round(total_cost, 6),
            "steps": {k: v.model_dump() for k, v in self.steps.items()}
        }

def trace_step(step_name: str):
    """Decorator to automatically time and trace a function step."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer: Optional[PipelineTracer] = kwargs.get("tracer")
            t0 = time.perf_counter()
            res = await func(*args, **kwargs)
            dt = (time.perf_counter() - t0) * 1000.0
            if tracer:
                tracer.record_step(step_name, dt)
            return res

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer: Optional[PipelineTracer] = kwargs.get("tracer")
            t0 = time.perf_counter()
            res = func(*args, **kwargs)
            dt = (time.perf_counter() - t0) * 1000.0
            if tracer:
                tracer.record_step(step_name, dt)
            return res

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
