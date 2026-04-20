from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe
except Exception:  # pragma: no cover
    _LANGFUSE_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()
else:
    _LANGFUSE_AVAILABLE = True

    class _LangfuseContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            get_client().update_current_trace(**kwargs)

        def update_current_observation(self, **kwargs: Any) -> None:
            usage = kwargs.pop("usage", None)
            if usage is not None:
                kwargs["usage_details"] = {
                    "input": usage.get("input", 0),
                    "output": usage.get("output", 0),
                }

            if "model" in kwargs or "usage_details" in kwargs:
                get_client().update_current_generation(**kwargs)
            else:
                get_client().update_current_span(**kwargs)

        def flush(self) -> None:
            get_client().flush()

    langfuse_context = _LangfuseContext()


def tracing_enabled() -> bool:
    return bool(
        _LANGFUSE_AVAILABLE
        and os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
    )
