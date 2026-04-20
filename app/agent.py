from __future__ import annotations

import time
from dataclasses import dataclass

from . import metrics
from .logging_config import get_logger
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import current_trace_info, langfuse_context, observe, tracing_enabled

log = get_logger()


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(name="movie-recommendation-agent", capture_input=False, capture_output=False)
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        langfuse_context.update_current_observation(input=message)
        started = time.perf_counter()
        docs = retrieve(message)
        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
        response = self.llm.generate(prompt)
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(
            response.usage.input_tokens, 
            response.usage.output_tokens, 
            response.usage.cache_read_tokens
        )

        langfuse_context.update_current_trace(
            name=f"chat-{feature}",
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=["lab", feature, self.model],
        )
        langfuse_context.update_current_observation(
            metadata={"doc_count": len(docs), "query_preview": summarize_text(message)},
            output=response.text,
        )

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        langfuse_context.flush()
        if tracing_enabled():
            log.info("trace_flushed", service="tracing", payload=current_trace_info())
        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int, cache_read_tokens: int = 0) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        cache_cost = (cache_read_tokens / 1_000_000) * 0.3  # Anthropic prompt caching hits cost 10%
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + cache_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
