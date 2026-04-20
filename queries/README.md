# Queries

Thu muc nay chua cac bo payload JSONL de ban chay kiem thu nhanh bang script:

```bash
python3 scripts/run_queries.py --file queries/pii.jsonl
```

Goi y:
- Doi base url: `--base-url http://127.0.0.1:8000`
- Tang do song song nhe: `--concurrency 5`
- Them header: `--header 'x-request-id:req-deadbeef'`

