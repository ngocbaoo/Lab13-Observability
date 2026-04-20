# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 10m`
- Impact: tail latency breaches SLO
- Typical incident mapping: `rag_slow`
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries
  - fallback retrieval source
  - lower prompt size
- Recovery criteria:
  - p95 latency returns below 2800ms for at least 15 minutes

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Impact: users receive failed responses
- Typical incident mapping: `tool_fail`
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - rollback latest change
  - disable failing tool
  - retry with fallback model
- Recovery criteria:
  - error rate stays below 1% for 10 minutes and no new dominant error type appears

## 3. Cost budget spike
- Severity: P2
- Trigger: `avg_cost_usd > 0.08 for 15m`
- Impact: burn rate exceeds budget
- Typical incident mapping: `cost_spike`
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache
- Recovery criteria:
  - avg_cost_usd remains below 0.07 for 30 minutes after mitigation
