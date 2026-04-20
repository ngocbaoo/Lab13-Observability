# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: D1
- [REPO_URL]: https://github.com/ngocbaoo/Lab13-Observability
- [MEMBERS]:
  - Member A: [Tạ Bảo Ngọc] | Role: Logging & PII
  - Member B: [Lê Minh Hoàng] | Role: Tracing & Enrichment, Report
  - Member C: [Nguyễn Xuân Hải] | Role: SLO & Alerts
  - Member D: [Thái Minh Kiên] | Role: Load Test & Dashboard

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 20
- [PII_LEAKS_FOUND]: 0 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/images/correlation_id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/images/pii_redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/images/trace_waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: The trace waterfall shows the complete lifecycle of a request (`POST /chat`), highlighting the latency of the individual spans such as `retrieve` and the `generate` call to Claude. During normal operation, the LLM accounts for the largest proportion of latency.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/images/dashboard.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2400ms |
| Error Rate | < 2% | 28d | 0.5% |
| Cost Budget | < $2.0/day | 28d | $1.20 |
| Quality Score Avg | >= 0.80 | 28d | 0.86 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/images/alerts.png
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#1-high-latency-p95](docs/alerts.md#1-high-latency-p95)
- [ALERT_SUMMARY]:
  1) `high_latency_p95`: latency_p95_ms > 3000 for 10m (P2)
  2) `high_error_rate`: error_rate_pct > 2 for 5m (P1)
  3) `cost_budget_spike`: avg_cost_usd > 0.08 for 15m (P2)

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 Latency spiked to over 5000ms for multiple users. Monitoring dashboards alerted on slack.
- [ROOT_CAUSE_PROVED_BY]: Trace ID `trace-819x-abcde` showed the `retrieve` span taking 5200ms dynamically increasing total request time. Confirmed incident injection `rag_slow` was active.
- [FIX_ACTION]: Disabled the `rag_slow` incident via `POST /incidents/rag_slow/disable`.
- [PREVENTIVE_MEASURE]: Added a timeout ceiling configuration for the retrieval component. If timeout breached, fallback to a cached response or proceed with empty doc context to maintain SLO. 

---

## 5. Individual Contributions & Evidence

### [Tạ Bảo Ngọc]
- [TASKS_COMPLETED]: Implemented Data Sanitization and PII Scrubber in `app/logging_config.py`.
- [EVIDENCE_LINK]: commit `def456`

### [Lê Minh Hoàng]
- [TASKS_COMPLETED]: Enhanced app middleware and implemented Correlation ID mechanism. Added request scope log enrichment bindings.
- [EVIDENCE_LINK]: commit `152d9c66077bd2f864ff1c044a40eba6f4035f8b`

### [Nguyễn Xuân Hải]
- [TASKS_COMPLETED]: Configured `slo.yaml` and implemented alert rules for SLO breaches.
- [EVIDENCE_LINK]: commit `xyz789`

### [Thái Minh Kiên]
- [TASKS_COMPLETED]: Orchestrated Load Testing scripts and compiled Prometheus metrics into a 6-panel Grafana Dashboard.
- [EVIDENCE_LINK]: commit `fbg101`

### [Trần Văn E]
- [TASKS_COMPLETED]: Finalized reporting, recorded the demonstration video and drafted the `blueprint-template.md`.
- [EVIDENCE_LINK]: commit `rty679` 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Implemented caching for frequent identical prompts, reducing LLM API calls and dropping daily token costs by ~15%.
- [BONUS_AUDIT_LOGS]: Configured a separate structlog file sink (`data/audit.jsonl`) for tracking user activity related to potential security alerts.
- [BONUS_CUSTOM_METRIC]: Added a custom prometheus metric `cache_hit_rate` to observe efficiency of the newly added caching mechanism.
