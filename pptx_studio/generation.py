"""OpenSandbox-backed Deep Agent presentation generation service."""

from __future__ import annotations

import os
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from queue import Empty, SimpleQueue
from typing import Any, Callable
from uuid import uuid4

from deepagents import create_deep_agent
from langchain_opensandbox import OpenSandboxBackend
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync

from prompts import SYSTEM_PROMPT, build_human_prompt
from pptx_studio.config import REMOTE_SKILLS, SANDBOX_IMAGE
from pptx_studio.models import langfuse_callbacks, make_model
from pptx_studio.storage import upload_presentation

StepEvent = tuple[int, str, Any]
ProgressCallback = Callable[[str, int, str, Any], None]


@dataclass
class PresentationResult:
    """A generated deck and its Supabase Storage location, if uploaded."""

    model_name: str
    filename: str
    content: bytes
    storage_path: str | None = None


@dataclass
class ModelRunResult:
    """Outcome, generated decks, and captured agent steps for one model."""

    model_name: str
    presentations: list[PresentationResult] = field(default_factory=list)
    steps: list[StepEvent] = field(default_factory=list)
    error: str | None = None
    upload_error: str | None = None


def sandbox_connection_config() -> ConnectionConfigSync | None:
    """Build the OpenSandbox client config when a remote server is specified."""
    domain = os.getenv("OPEN_SANDBOX_DOMAIN")
    if not domain:
        return None
    return ConnectionConfigSync(
        domain=domain,
        protocol=os.getenv("OPEN_SANDBOX_PROTOCOL", "http"),
        api_key=os.getenv("OPEN_SANDBOX_API_KEY") or None,
        use_server_proxy=True,
    )


def create_sandbox() -> tuple[Any, OpenSandboxBackend]:
    """Create a sandbox and its Deep Agents filesystem backend."""
    sandbox = SandboxSync.create(
        SANDBOX_IMAGE,
        timeout=timedelta(hours=24),
        connection_config=sandbox_connection_config(),
    )
    return sandbox, OpenSandboxBackend(sandbox=sandbox)


def _generate_for_model(
    instructions: str,
    slides_count: int,
    template: str,
    model_name: str,
    run_id: str,
    on_progress: ProgressCallback,
) -> ModelRunResult:
    """Run one model in its own sandbox to isolate concurrent filesystem work."""
    sandbox = None
    steps: list[StepEvent] = []
    try:
        sandbox, backend = create_sandbox()
        backend.execute("mkdir -p /workspace/build /workspace/output")
        agent = create_deep_agent(
            tools=[],
            model=make_model(model_name),
            system_prompt=SYSTEM_PROMPT,
            backend=backend,
            skills=[f"{REMOTE_SKILLS}/"],
        )
        request = {
            "messages": [{
                "role": "user",
                "content": build_human_prompt(instructions, slides_count, template),
            }],
            "pinned_skills": ["pptx", template],
        }
        for step_number, update in enumerate(
            agent.stream(
                request,
                config={"callbacks": langfuse_callbacks()},
                stream_mode="updates",
            ),
            start=1,
        ):
            for node, state_update in update.items():
                event = (step_number, node, state_update)
                steps.append(event)
                on_progress(model_name, step_number, node, state_update)

        listing = backend.execute("ls -1 /workspace/output/*.pptx 2>/dev/null")
        output = getattr(listing, "output", str(listing))
        remote_paths = [
            line.strip() for line in output.splitlines() if line.strip().endswith(".pptx")
        ]
        presentations: list[PresentationResult] = []
        upload_errors: list[str] = []
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        safe_model = model_name.replace("/", "-")
        for result, remote_path in zip(backend.download_files(remote_paths), remote_paths):
            content = getattr(result, "content", None)
            if content:
                filename = Path(remote_path).name
                storage_path = None
                try:
                    storage_path = upload_presentation(
                        content,
                        f"presentations/{date_prefix}/{run_id}/{safe_model}/{filename}",
                    )
                except Exception as exc:
                    upload_errors.append(f"{filename}: {exc}")
                presentations.append(
                    PresentationResult(model_name, filename, content, storage_path)
                )
        return ModelRunResult(
            model_name,
            presentations,
            steps,
            upload_error="; ".join(upload_errors) or None,
        )
    except Exception as exc:
        return ModelRunResult(model_name, steps=steps, error=str(exc))
    finally:
        if sandbox is not None:
            try:
                sandbox.destroy()
            except Exception:
                # Preserve the generation outcome; sandbox cleanup can be retried
                # by the server's timeout if the API is temporarily unavailable.
                pass


def generate_presentations(
    instructions: str,
    slides_count: int,
    template: str,
    model_names: list[str],
    on_progress: ProgressCallback,
) -> list[ModelRunResult]:
    """Generate concurrently, isolating each selected model in its own sandbox."""
    if not model_names:
        return []

    run_id = uuid4().hex
    progress_events: SimpleQueue[tuple[str, int, str, Any]] = SimpleQueue()

    def report_progress(
        model_name: str, step_number: int, node: str, state_update: Any
    ) -> None:
        progress_events.put((model_name, step_number, node, state_update))

    results: dict[str, ModelRunResult] = {}
    with ThreadPoolExecutor(max_workers=min(len(model_names), 3)) as executor:
        futures: dict[Future[ModelRunResult], str] = {
            executor.submit(
                _generate_for_model,
                instructions,
                slides_count,
                template,
                model_name,
                run_id,
                report_progress,
            ): model_name
            for model_name in model_names
        }
        pending = set(futures)
        while pending:
            done, pending = wait(pending, timeout=0.2, return_when=FIRST_COMPLETED)
            while True:
                try:
                    on_progress(*progress_events.get_nowait())
                except Empty:
                    break
                except Exception:
                    # A UI progress-rendering failure must not cancel worker runs.
                    break
            for future in done:
                model_name = futures[future]
                try:
                    results[model_name] = future.result()
                except Exception as exc:
                    results[model_name] = ModelRunResult(model_name, error=str(exc))

        while True:
            try:
                on_progress(*progress_events.get_nowait())
            except Empty:
                break
            except Exception:
                break
    return [results[name] for name in model_names]
