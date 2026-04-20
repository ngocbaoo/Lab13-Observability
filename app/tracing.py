from __future__ import annotations

import os
import functools
from typing import Any

_LANGFUSE_AVAILABLE = False
_LANGFUSE_IMPORT_ERROR: str | None = None
_LANGFUSE_INTEGRATION: str = "disabled"  # "decorators" | "client" | "disabled"
_LANGFUSE_SDK_VERSION: str | None = None

try:
    from langfuse.decorators import observe, langfuse_context

    _LANGFUSE_AVAILABLE = True
    _LANGFUSE_INTEGRATION = "decorators"
    try:  # pragma: no cover
        import langfuse as _langfuse_mod

        _LANGFUSE_SDK_VERSION = getattr(_langfuse_mod, "__version__", None)
    except Exception:
        _LANGFUSE_SDK_VERSION = None
except Exception as e:  # pragma: no cover
    # Fallback for older SDK versions where `langfuse.decorators` may not exist.
    try:  # pragma: no cover
        from langfuse import Langfuse
        import langfuse as _langfuse_mod

        _LANGFUSE_AVAILABLE = True
        _LANGFUSE_INTEGRATION = "client"
        _LANGFUSE_SDK_VERSION = getattr(_langfuse_mod, "__version__", None)
        _client = Langfuse()

        class _ClientContext:
            def update_current_trace(self, **kwargs: Any) -> None:
                _client.update_current_trace(**kwargs)

            def update_current_observation(self, **kwargs: Any) -> None:
                # In older SDKs, "observation" maps to the current span and the accepted
                # parameter set is smaller than in newer decorator-based integration.
                allowed = {"name", "input", "output", "metadata", "version", "level", "status_message"}
                safe_kwargs: dict[str, Any] = {}
                metadata: dict[str, Any] = {}

                # Keep explicit metadata if provided.
                if isinstance(kwargs.get("metadata"), dict):
                    metadata.update(kwargs["metadata"])

                # Map common extra fields to metadata.
                if "model" in kwargs:
                    metadata.setdefault("model", kwargs["model"])
                if "usage" in kwargs:
                    metadata.setdefault("usage", kwargs["usage"])

                # Pass through allowed fields.
                for k, v in kwargs.items():
                    if k in allowed and k != "metadata":
                        safe_kwargs[k] = v
                    elif k not in allowed and k not in {"model", "usage"}:
                        # Preserve any unexpected keys without breaking the SDK.
                        metadata.setdefault(k, v)

                if metadata:
                    safe_kwargs["metadata"] = metadata

                _client.update_current_span(**safe_kwargs)

            def flush(self) -> None:
                _client.flush()

            def get_current_trace_id(self) -> str | None:
                return _client.get_current_trace_id()

            def get_current_trace_url(self) -> str | None:
                return _client.get_trace_url()

        langfuse_context = _ClientContext()

        def observe(*args: Any, **kwargs: Any):
            name = kwargs.get("name")
            capture_input = bool(kwargs.get("capture_input", True))
            capture_output = bool(kwargs.get("capture_output", True))

            def decorator(func):
                @functools.wraps(func)
                def wrapper(*f_args: Any, **f_kwargs: Any):
                    span_input = None
                    if capture_input:
                        span_input = {"args": f_args, "kwargs": f_kwargs}
                    with _client.start_as_current_span(name=name or func.__name__, input=span_input):
                        try:
                            result = func(*f_args, **f_kwargs)
                        except Exception as exc:
                            _client.update_current_span(level="ERROR", status_message=str(exc))
                            raise
                        if capture_output:
                            _client.update_current_span(output=result)
                        return result

                return wrapper

            return decorator

    except Exception as e2:  # pragma: no cover
        _LANGFUSE_IMPORT_ERROR = (
            "Failed to import Langfuse SDK integration. "
            f"decorators error=({type(e).__name__}: {e}); "
            f"client error=({type(e2).__name__}: {e2})."
        )

        def observe(*args: Any, **kwargs: Any):
            def decorator(func):
                return func

            return decorator

        class _DummyContext:
            def update_current_trace(self, **kwargs: Any) -> None:
                return None

            def update_current_observation(self, **kwargs: Any) -> None:
                return None

            # Some code paths call `langfuse_context.flush()` to ensure traces are sent.
            # When Langfuse isn't installed/configured, this is a no-op.
            def flush(self) -> None:
                return None

            def get_current_trace_id(self) -> str | None:
                return None

            def get_current_trace_url(self) -> str | None:
                return None

        langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(
        _LANGFUSE_AVAILABLE
        and os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
    )


def tracing_diagnostics() -> dict[str, Any]:
    host = os.getenv("LANGFUSE_HOST")
    public_key_set = bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
    secret_key_set = bool(os.getenv("LANGFUSE_SECRET_KEY"))
    enabled = bool(_LANGFUSE_AVAILABLE and public_key_set and secret_key_set)

    reason: str | None = None
    if not _LANGFUSE_AVAILABLE:
        reason = _LANGFUSE_IMPORT_ERROR or "Langfuse is not available in this environment."
    elif not public_key_set or not secret_key_set:
        reason = "Missing LANGFUSE_PUBLIC_KEY/LANGFUSE_SECRET_KEY."

    return {
        "enabled": enabled,
        "available": _LANGFUSE_AVAILABLE,
        "integration": _LANGFUSE_INTEGRATION,
        "sdk_version": _LANGFUSE_SDK_VERSION,
        "reason": reason,
        "host": host,
        "public_key_set": public_key_set,
        "secret_key_set": secret_key_set,
    }


def current_trace_info() -> dict[str, str | None]:
    get_id = getattr(langfuse_context, "get_current_trace_id", None)
    get_url = getattr(langfuse_context, "get_current_trace_url", None)
    trace_id = get_id() if callable(get_id) else None
    trace_url = get_url() if callable(get_url) else None
    return {"trace_id": trace_id, "trace_url": trace_url}
