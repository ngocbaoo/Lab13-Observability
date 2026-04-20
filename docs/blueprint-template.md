# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: D1
- [REPO_URL]: https://github.com/ngocbaoo/Lab13-Observability
- [MEMBERS]:
  - Member A: [Tạ Bảo Ngọc] | Role: Project Setup, Logging & PII
  - Member B: [Thái Minh Kiên] | Role: Tracing & Observability Context
  - Member C: [Nguyễn Xuân Hải] | Role: Load Test, Automations & Documentation
  - Member D: [Lê Minh Hoàng] | Role: SLO, Alerts & System Optimization

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
- [TASKS_COMPLETED]: Khởi tạo toàn bộ cấu trúc dự án (app, config, docs, scripts, tests). Chịu trách nhiệm thiết lập nền tảng Logging cơ bản, dữ liệu sample queries và hệ thống đáp án kỳ vọng.
- [EVIDENCE_LINK]: commit `9558fa92e58259e93241095b1591d33af99b71a9` và `8c63e7073df4c3ef1fcaafc0ea9e219ecc97de7a`

### [Thái Minh Kiên]
- [TASKS_COMPLETED]: Triển khai hệ thống Tracing cơ bản. Thêm cơ chế kiểm tra `_LANGFUSE_AVAILABLE`, tạo lớp `_LangfuseContext` để quản lý `update_current_trace`, tracking usage details và flushing dữ liệu trace an toàn.
- [EVIDENCE_LINK]: commit `6bd270381214da3bfeef045d486c23ff78c9171a`

### [Nguyễn Xuân Hải]
- [TASKS_COMPLETED]: Xây dựng các kịch bản chạy test truy vấn tự động (`scripts/run_queries.py`). Chuẩn bị bộ truy vấn mới, sửa lỗi tiến trình flush tracing và cập nhật tài liệu chạy ứng dụng (`tester.md`).
- [EVIDENCE_LINK]: commit `d29812ec0f5b3396438584c2ba0dbc8ac706ad73` và `2d86d889b2641519c73d1e2be784f68ac48b024e`

### [Lê Minh Hoàng]
- [TASKS_COMPLETED]: Thiết lập các quy tắc Alert và khai báo SLO (`alert_rules.yaml`, `slo.yaml`, `alerts.md`). Refactor tối ưu hệ thống: loại bỏ API thừa, tinh gọn tracing agent và tối ưu hóa hệ thống mock (LLM, RAG).
- [EVIDENCE_LINK]: commit `152d9c66077bd2f864ff1c044a40eba6f4035f8b`

---

## 6. Bonus Items (Optional)
- [BONUS_SYSTEM_OPTIMIZATION]: Đã thực hiện code-refactor tinh gọn ứng dụng, loại bỏ các file và logic không cần thiết, tối giản kiến trúc để focus toàn bộ sức mạnh vào Core Observability.
- [BONUS_RESILIENT_TRACING]: Phát triển cơ sở Tracing ổn định qua việc cấu hình fallback (ngăn ứng dụng crash khi gọi thiếu Langfuse API key) và tối ưu tiến trình flush.
