"""Streamlit UI and session-state orchestration."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import streamlit as st

from pptx_studio.components.pptx_preview import pptx_preview
from pptx_studio.config import MODELS, TEMPLATES
from pptx_studio.generation import ModelRunResult, PresentationResult, generate_presentations
from pptx_studio.storage import storage_is_configured


def _render_step_content(state_update: Any) -> None:
    """Render the message and tool-call details from a streamed update."""
    if not isinstance(state_update, dict):
        st.write(str(state_update))
        return

    messages = state_update.get("messages", [])
    if not isinstance(messages, list):
        messages = [messages]
    for message in messages:
        for call in getattr(message, "tool_calls", []) or []:
            args = json.dumps(call.get("args", {}), ensure_ascii=False, default=str)
            st.code(f"Tool call: {call.get('name')} {args}", language="text")
        content = getattr(message, "content", "")
        if content:
            st.write(content if isinstance(content, str) else str(content))


def _initialize_session() -> None:
    """Initialize Streamlit session-state values once per browser session."""
    defaults = {
        "generated_presentations": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _run_comparison(
    instructions: str,
    slides_count: int,
    template: str,
    model_names: list[str],
) -> list[ModelRunResult]:
    """Run each selected model concurrently and stream lightweight progress."""
    statuses: dict[str, Any] = {}

    def render_progress(
        model_name: str, step_number: int, node: str, state_update: Any
    ) -> None:
        if model_name not in statuses:
            statuses[model_name] = st.status(
                f"Generating with {model_name}…", expanded=False
            )
        with statuses[model_name].container():
            st.write(f"Step {step_number} · {node}")

    try:
        results = generate_presentations(
            instructions,
            slides_count,
            template,
            model_names,
            render_progress,
        )
    except Exception:
        for model_name, status in statuses.items():
            status.update(label=f"{model_name} failed", state="error")
        raise

    for run in results:
        status = statuses.get(run.model_name)
        if status:
            status.update(
                label=f"{run.model_name} failed" if run.error else f"{run.model_name} finished",
                state="error" if run.error else "complete",
            )
    return results


def _render_comparison(model_runs: list[ModelRunResult]) -> None:
    """Render run status, nested step logs, downloads, and slide comparisons."""
    st.header("Your presentations")
    st.caption("Review each model's steps, then compare successful decks side by side.")
    summary_rows = [
        {
            "Model": run.model_name,
            "Status": "Failed" if run.error else ("Completed" if run.presentations else "No PPTX found"),
            "Presentations": len(run.presentations),
            "Uploaded": sum(presentation.storage_path is not None for presentation in run.presentations),
            "Error": run.error or "",
            "Upload error": run.upload_error or "",
        }
        for run in model_runs
    ]
    st.table(summary_rows)

    st.subheader("Generation steps")
    log_columns = st.columns(min(len(model_runs), 3))
    for index, run in enumerate(model_runs):
        with log_columns[index % len(log_columns)]:
            with st.expander(run.model_name, expanded=False):
                if run.error:
                    st.error(run.error)
                if not run.steps:
                    st.caption("No agent steps were reported.")
                for step_number, node, state_update in run.steps:
                    with st.expander(f"Step {step_number} · {node}", expanded=False):
                        _render_step_content(state_update)

    presentations: list[PresentationResult] = [
        presentation
        for run in model_runs
        for presentation in run.presentations
    ]
    if not presentations:
        return

    st.subheader("PowerPoint comparison")
    st.caption("Download and inspect each generated deck side by side.")
    compare_columns = st.columns(min(len(presentations), 3))
    for index, presentation in enumerate(presentations):
        model_name = presentation.model_name
        filename = presentation.filename
        pptx_content = presentation.content
        column = compare_columns[index % len(compare_columns)]
        presentation_id = hashlib.sha256(pptx_content).hexdigest()[:12]
        with column:
            st.subheader(model_name)
            st.caption(Path(filename).stem.replace("_", " ").replace("-", " ").title())
            st.download_button(
                "Download PowerPoint",
                data=pptx_content,
                file_name=f"{Path(filename).stem}_{model_name.replace('/', '-')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                icon=":material/download:",
                key=f"pptx-download-{index}-{presentation_id}",
                width="stretch",
            )
            if presentation.storage_path:
                st.caption(f"Saved to `files/{presentation.storage_path}`")
            else:
                st.warning("This deck was not uploaded to Supabase Storage.")
            pptx_preview(
                pptx_content,
                key=f"pptx-preview-{model_name}-{presentation_id}",
            )


def main() -> None:
    """Render the Streamlit application."""
    st.set_page_config(
        page_title="DeepAgent PPTX Studio",
        page_icon=":material/slideshow:",
        layout="wide",
    )
    _initialize_session()

    st.title("DeepAgent PPTX Studio")
    st.caption("Describe a presentation, choose a design, and watch the agent build it.")

    with st.form("presentation_request"):
        instructions = st.text_area(
            "Presentation instructions",
            placeholder="For example: Explain modern C++ concepts for software engineers, with practical examples.",
            height=160,
        )
        col_count, col_template = st.columns(2)
        with col_count:
            slides_count = st.number_input(
                "Number of slides", min_value=1, max_value=60, value=20, step=1
            )
        with col_template:
            template = st.selectbox("Design template", TEMPLATES, index=1)
        model_names = st.multiselect(
            "Models to compare (choose 1–3)",
            [model["model_id"] for model in MODELS],
            default=[MODELS[0]["model_id"]],
            max_selections=3,
            help="The same presentation request will be generated once by each selected model.",
        )
        submitted = st.form_submit_button(
            "Generate presentation",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not instructions.strip():
            st.error("Enter presentation instructions before generating.")
            return
        if not model_names:
            st.error("Select at least one model.")
            return
        if not os.getenv("OPENAI_API_KEY"):
            st.error("Set `OPENAI_API_KEY` in `.env.local` (or the process environment) before generating.")
            return
        if not storage_is_configured():
            st.error(
                "Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env.local` "
                "(or the process environment) before generating."
            )
            return

        st.session_state.generated_presentations = []
        try:
            model_runs = _run_comparison(
                instructions, int(slides_count), template, model_names
            )
        except Exception as exc:
            st.exception(exc)
        else:
            if not model_runs:
                st.error("No model runs completed.")
            else:
                st.session_state.generated_presentations = model_runs
                successful_count = sum(len(run.presentations) for run in model_runs)
                st.success(f"Generated {successful_count} presentation(s) across {len(model_runs)} model run(s).")

    if st.session_state.generated_presentations:
        _render_comparison(st.session_state.generated_presentations)
