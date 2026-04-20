#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import time
from pathlib import Path

import httpx


def _parse_headers(items: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in items:
        if ":" not in item:
            raise SystemExit(f"Invalid --header {item!r}. Expected KEY:VALUE")
        k, v = item.split(":", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise SystemExit(f"Invalid --header {item!r}. Empty key")
        headers[k] = v
    return headers


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"Query file not found: {path}")
    out: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path}:{i}: invalid JSON: {e}") from e
        if not isinstance(obj, dict):
            raise SystemExit(f"{path}:{i}: expected JSON object, got {type(obj).__name__}")
        out.append(obj)
    if not out:
        raise SystemExit(f"No queries found in {path}")
    return out


def _send_one(client: httpx.Client, url: str, payload: dict, headers: dict[str, str]) -> None:
    start = time.perf_counter()
    try:
        r = client.post(url, json=payload, headers=headers)
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        print(f"[ERR] {latency_ms:.1f}ms | {e}")
        return

    latency_ms = (time.perf_counter() - start) * 1000
    cid = "-"
    body_preview = ""
    try:
        j = r.json()
        if isinstance(j, dict):
            cid = str(j.get("correlation_id", "-"))
        body_preview = json.dumps(j)[:200]
    except Exception:
        body_preview = r.text[:200]

    print(f"[{r.status_code}] {cid} | {latency_ms:.1f}ms | {body_preview}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run JSONL queries against the lab API.")
    parser.add_argument("--file", default="queries/pii.jsonl", help="Path to JSONL file of JSON objects")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL (no trailing slash)")
    parser.add_argument("--endpoint", default="/chat", help="Endpoint path (e.g. /chat)")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    parser.add_argument("--repeat", type=int, default=1, help="Repeat each query N times")
    parser.add_argument("--header", action="append", default=[], help="Extra header KEY:VALUE (repeatable)")
    args = parser.parse_args()

    path = Path(args.file)
    queries = _load_jsonl(path)
    headers = _parse_headers(args.header)

    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")
    if args.repeat < 1:
        raise SystemExit("--repeat must be >= 1")

    total = len(queries) * args.repeat
    # Safety guard: this is a lab runner, not a load test cannon.
    if total > 250:
        raise SystemExit(f"Refusing to send {total} requests (>250). Lower --repeat or shrink the file.")

    base = args.base_url.rstrip("/")
    endpoint = args.endpoint if args.endpoint.startswith("/") else f"/{args.endpoint}"
    url = f"{base}{endpoint}"

    with httpx.Client(timeout=30.0) as client:
        if args.concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
                futures = []
                for _ in range(args.repeat):
                    for q in queries:
                        futures.append(ex.submit(_send_one, client, url, q, headers))
                concurrent.futures.wait(futures)
        else:
            for _ in range(args.repeat):
                for q in queries:
                    _send_one(client, url, q, headers)


if __name__ == "__main__":
    main()

