"""
agent/tracing.py — LangSmith observability for the analytics agent.

Reads LANGSMITH_API_KEY and LANGSMITH_PROJECT from the environment / .env file.
If the key is absent, or if any tracing call fails for any reason, everything
degrades silently: the agent continues to work identically without tracing.

Public API
----------
trace_query(query, active_case)
    Context manager for agent_callbacks.py.
    Wraps the full query cycle as a top-level LangSmith run.
    Yields the RunTree object (or None if tracing is off).
    Caller may call `log_to_run(run, {...})` to attach routing metadata.

trace_llm(name, inputs)
    Context manager for classifier.py and explain.py.
    Wraps one generate_content call as a child run nested under the
    current trace_query run (if active).
    Yields a plain mutable dict — caller populates it with outputs
    (e.g. raw_response, parsed_intent) before the block exits.

log_to_run(run, data)
    Safe helper — adds `data` to the run's outputs/metadata without
    risking an exception if the SDK version does not support a method.
"""

from __future__ import annotations

import contextlib
import contextvars
import os
import time
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# bootstrap  
_ENABLED: bool = False
_PROJECT: str = "institutional-analytics-dashboard"

# Stores the active top-level RunTree so child trace_llm calls can find it.
_active_run: contextvars.ContextVar[Any] = contextvars.ContextVar(
    "ls_active_run", default=None
)


def _bootstrap() -> None:
    global _ENABLED, _PROJECT
    api_key = os.environ.get("LANGSMITH_API_KEY", "").strip()
    if not api_key:
        return
    try:
        import langsmith  # noqa: F401 — verify the package is installed
        _PROJECT = os.environ.get("LANGSMITH_PROJECT", _PROJECT)
        # The LangSmith SDK reads these standard env vars internally.
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", api_key)
        os.environ.setdefault("LANGCHAIN_PROJECT", _PROJECT)
        _ENABLED = True
    except Exception:
        pass


_bootstrap()


# ── Public helpers ─────────────────────────────────────────────────────────────

def log_to_run(run: Any, data: dict) -> None:
    """
    Safely attach `data` to a RunTree as metadata.
    No-op if run is None, tracing is off, or any SDK call fails.
    """
    if run is None or not _ENABLED:
        return
    try:
        # add_metadata is available in langsmith >= 0.1.x
        run.add_metadata(data)
    except Exception:
        try:
            # Fallback: merge into the run's extra dict directly
            run.extra = run.extra or {}
            run.extra.setdefault("metadata", {}).update(data)
        except Exception:
            pass


# ── trace_query ────────────────────────────────────────────────────────────────

@contextlib.contextmanager
def trace_query(query: str, active_case: str):
    """
    Top-level LangSmith run for one full agent query cycle.

    Yields the RunTree object so the caller can attach routing metadata via
    log_to_run(run, {...}).  Yields None if tracing is disabled or setup fails.

    The context manager measures wall-clock latency and records it as an
    output automatically.  Any unhandled exception is recorded as an error.

    Example (agent_callbacks.py):
        with trace_query(query, active_case) as run:
            ...
            log_to_run(run, {"intent": intent, "final_params": params})
    """
    if not _ENABLED:
        yield None
        return

    run = None
    try:
        from langsmith.run_trees import RunTree
        run = RunTree(
            name="agent_query",
            run_type="chain",
            project_name=_PROJECT,
            inputs={"query": query, "active_case": active_case},
        )
        run.post()
    except Exception:
        yield None
        return

    token = _active_run.set(run)
    t0 = time.perf_counter()
    exc_str: str | None = None

    try:
        yield run
    except Exception as exc:
        exc_str = str(exc)
        raise
    finally:
        _active_run.reset(token)
        try:
            latency_ms = round((time.perf_counter() - t0) * 1000)
            run.end(outputs={"latency_ms": latency_ms}, error=exc_str)
            run.patch()
        except Exception:
            pass


# ── trace_llm ──────────────────────────────────────────────────────────────────

@contextlib.contextmanager
def trace_llm(name: str, inputs: dict):
    """
    Child LangSmith run wrapping one generate_content call.

    Automatically nests under the active trace_query run if one exists.
    Yields a plain mutable dict — the caller should populate it with any
    outputs that should be logged (raw_response, parsed_intent, etc.).

    Example (classifier.py):
        with trace_llm("gemini_classify", {"prompt": prompt}) as out:
            response = model.generate_content(prompt, ...)
            out["raw_response"] = response.text
            out["parsed_intent"] = result.get("intent")

    Example (explain.py):
        with trace_llm("gemini_explain", {"prompt": prompt}) as out:
            response = model.generate_content(prompt)
            out["response"] = response.text.strip()
    """
    outputs: dict = {}

    if not _ENABLED:
        yield outputs
        return

    run = None
    try:
        from langsmith.run_trees import RunTree
        parent = _active_run.get()

        if parent is not None:
            run = parent.create_child(
                name=name,
                run_type="llm",
                inputs=inputs,
            )
        else:
            run = RunTree(
                name=name,
                run_type="llm",
                project_name=_PROJECT,
                inputs=inputs,
            )
        run.post()
    except Exception:
        yield outputs
        return

    exc_str: str | None = None
    try:
        yield outputs
    except Exception as exc:
        exc_str = str(exc)
        raise
    finally:
        try:
            run.end(outputs=outputs, error=exc_str)
            run.patch()
        except Exception:
            pass
