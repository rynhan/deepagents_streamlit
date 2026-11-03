"""Application configuration and selectable generation options."""

from __future__ import annotations

import os
from pathlib import Path

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
MODELS = [
    "openai/gpt-6-luna",
    "openai/gpt-6.1-sol",
    "anthropic/claude-opus-5-5",
    "anthropic/claude-haiku-5-5",
]
