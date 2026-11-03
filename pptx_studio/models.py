"""Factories for chat models and optional tracing callbacks."""

from __future__ import annotations

import os
from typing import Any

from langchain_openai import ChatOpenAI


def make_model(model_name: str) -> ChatOpenAI:
    """Create the selected OpenAI-compatible chat model."""
    model_kwargs: dict[str, Any] = {
        "base_url": os.getenv("OPENAI_BASE_URL", "https://mlapi.run/v1"),
        "model": model_name,
        "reasoning_effort": "none",
        "stream_usage": True,
        "streaming": True,
    }
    if os.getenv("OPENAI_API_KEY"):
        model_kwargs["api_key"] = os.environ["OPENAI_API_KEY"]
    return ChatOpenAI(**model_kwargs)


def langfuse_callbacks() -> list[Any]:
    """Return Langfuse callbacks when credentials and dependency are available."""
    if not (os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_PUBLIC_KEY")):
        return []
    try:
        from langfuse.langchain import CallbackHandler
    except ImportError:
        return []
    return [CallbackHandler()]
