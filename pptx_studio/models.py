"""Factories for chat models and optional tracing callbacks."""

from __future__ import annotations

import os
from typing import Any

from langchain_openai import ChatOpenAI

from pptx_studio.config import MODELS


def make_model(model_name: str) -> ChatOpenAI:
    """Create the selected OpenAI-compatible chat model."""
    model_config = next(model for model in MODELS if model["model_id"] == model_name)
    model_kwargs: dict[str, Any] = {
        "base_url": os.getenv("OPENAI_BASE_URL", "https://mlapi.run/v1"),
        "model": model_name,
        "reasoning_effort": model_config["reasoning_effort"],
        "use_responses_api": model_config.get("use_responses_api", False),
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
