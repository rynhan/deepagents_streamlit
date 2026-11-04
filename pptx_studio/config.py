"""Application configuration and selectable generation options."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent.parent
load_dotenv(APP_DIR / ".env.local")

SANDBOX_IMAGE = os.getenv("PPTX_SANDBOX_IMAGE", "pptx-sandbox:1")
REMOTE_SKILLS = "/skills"

TEMPLATES = [
    "template-cobalt-grid",
    "template-monochrome",
    "template-neo-grid-bold",
    "template-raw-grid",
    "template-soft-editorial",
]
class ModelConfig(TypedDict):
    model_id: str
    reasoning_effort: Literal["none", "low", "medium", "high", "xhigh", "max"]
    use_responses_api: NotRequired[bool]


MODELS: list[ModelConfig] = [
    {"model_id": "openai/gpt-6-luna", "reasoning_effort": "none"},
    {
        "model_id": "openai/gpt-6.1-sol",
        "reasoning_effort": "low",
        # Tool calls with reasoning require Responses for this model.
        "use_responses_api": True,
    },
    {"model_id": "anthropic/claude-opus-5-5", "reasoning_effort": "low"},
    {"model_id": "anthropic/claude-haiku-5-5", "reasoning_effort": "low"},
]
