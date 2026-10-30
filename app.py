"""Streamlit UI for generating PowerPoint presentations with deepagents."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import timedelta
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_opensandbox import OpenSandboxBackend
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync

from prompts import SYSTEM_PROMPT, build_human_prompt


APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env.local")

SANDBOX_IMAGE = os.getenv("PPTX_SANDBOX_IMAGE", "pptx-sandbox:1")
REMOTE_SKILLS = "/skills"


def _sandbox_connection_config() -> ConnectionConfigSync | None:
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
TEMPLATES = [
    "template-cobalt-grid",
    "template-monochrome",
    "template-neo-grid-bold",
    "template-raw-grid",
    "template-soft-editorial",
]

_PPTX_VIEWER_HTML = """
<div class="pptx-viewer">
    <div class="pptx-toolbar" role="toolbar" aria-label="Presentation controls">
        <button class="pptx-prev" type="button" disabled>Previous</button>
        <button class="pptx-next" type="button" disabled>Next</button>
        <button class="pptx-fullscreen" type="button">Fullscreen</button>
        <span class="pptx-status" aria-live="polite">Loading presentation…</span>
    </div>
    <div class="pptx-stage">
        <canvas class="pptx-canvas" aria-label="Presentation slide preview"></canvas>
    </div>
    <p class="pptx-error" role="alert" hidden></p>
</div>
"""

_PPTX_VIEWER_CSS = """
.pptx-viewer {
    width: 100%;
    overflow: hidden;
    border: 1px solid var(--st-border-color, #d9d9d9);
    border-radius: 8px;
    background: var(--st-secondary-background-color, #f8f9fa);
    color: var(--st-text-color, #262730);
    font-family: var(--st-font, system-ui, sans-serif);
}
.pptx-toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    border-bottom: 1px solid var(--st-border-color, #d9d9d9);
}
.pptx-toolbar button {
    min-height: 34px;
    padding: 6px 12px;
    border: 1px solid var(--st-border-color, #c9cdd4);
    border-radius: 6px;
    background: var(--st-background-color, #fff);
    color: inherit;
    cursor: pointer;
    font: inherit;
}
.pptx-toolbar button:disabled { opacity: .5; cursor: not-allowed; }
.pptx-toolbar button:hover:not(:disabled) { border-color: var(--st-primary-color, #ff4b4b); }
.pptx-status { margin-left: auto; color: var(--st-text-color, #555); font-size: .85rem; }
.pptx-stage { width: 100%; padding: 12px; box-sizing: border-box; }
.pptx-canvas {
    display: block;
    width: 100%;
    height: auto;
    border: 1px solid var(--st-border-color, #d9d9d9);
    border-radius: 4px;
    background: #fff;
}
.pptx-error { margin: 0; padding: 12px; color: var(--st-text-color, #b42318); }
.pptx-viewer:fullscreen {
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    border: 0;
    border-radius: 0;
    background: #111;
}
.pptx-viewer:fullscreen .pptx-toolbar { flex: 0 0 auto; }
.pptx-viewer:fullscreen .pptx-stage {
    display: flex;
    flex: 1;
    align-items: center;
    justify-content: center;
    min-height: 0;
}
.pptx-viewer:fullscreen .pptx-canvas {
    width: auto;
    max-width: 100%;
    max-height: 100%;
}
"""

_PPTX_VIEWER_JS = """
export default function (component) {
const { data, parentElement } = component;
const root = parentElement.querySelector(".pptx-viewer");
if (!root) return () => {};

const canvas = root.querySelector(".pptx-canvas");
const stage = root.querySelector(".pptx-stage");
const prev = root.querySelector(".pptx-prev");
const next = root.querySelector(".pptx-next");
const fullscreen = root.querySelector(".pptx-fullscreen");
const status = root.querySelector(".pptx-status");
const error = root.querySelector(".pptx-error");
let viewer;
let slideAspect = 9 / 16;
let resizeObserver;
let renderVersion = 0;
let disposed = false;

function loadScript(src, ready) {
    if (ready()) return Promise.resolve();
    const existing = Array.from(parentElement.querySelectorAll("script[data-pptx-src]"))
        .find((script) => script.dataset.pptxSrc === src);
    if (existing) {
        return new Promise((resolve, reject) => {
            if (ready()) return resolve();
            existing.addEventListener("load", resolve, { once: true });
            existing.addEventListener("error", reject, { once: true });
        });
    }
    return new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = src;
        script.dataset.pptxSrc = src;
        script.onload = resolve;
        script.onerror = () => reject(new Error("Could not load " + src));
        parentElement.appendChild(script);
    });
}

function decodeBase64(value) {
    const binary = atob(value);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) {
        bytes[index] = binary.charCodeAt(index);
    }
    return bytes;
}

function updateStatus() {
    if (!viewer || disposed) return;
    const total = viewer.getSlideCount();
    const index = typeof viewer.getCurrentSlideIndex === "function"
        ? viewer.getCurrentSlideIndex()
        : 0;
    status.textContent = total ? `Slide ${index + 1} of ${total}` : "";
    prev.disabled = index <= 0 || total <= 1;
    next.disabled = index >= total - 1 || total <= 1;
}

function sizeCanvas() {
    if (!viewer || disposed) return;
    const width = Math.max(1, Math.floor(stage.clientWidth));
    const height = Math.max(1, Math.round(width * slideAspect));
    if (canvas.width === width && canvas.height === height) return;
    canvas.width = width;
    canvas.height = height;
    const version = ++renderVersion;
    const index = typeof viewer.getCurrentSlideIndex === "function"
        ? viewer.getCurrentSlideIndex()
        : 0;
    viewer.render(canvas, { slideIndex: index }).then(() => {
        if (version === renderVersion) updateStatus();
    }).catch(showError);
}

function applySlideAspect() {
    const dimensions = viewer && viewer.processor && viewer.processor.getSlideDimensions
        ? viewer.processor.getSlideDimensions()
        : null;
    if (dimensions && dimensions.cx && dimensions.cy) {
        slideAspect = dimensions.cy / dimensions.cx;
    }
    sizeCanvas();
}

function showError(reason) {
    if (disposed) return;
    error.hidden = false;
    error.textContent = "Unable to render this PowerPoint file. " + (reason?.message || "");
    status.textContent = "Preview unavailable";
}

prev.onclick = () => viewer && viewer.previousSlide(canvas).then(updateStatus).catch(showError);
next.onclick = () => viewer && viewer.nextSlide(canvas).then(updateStatus).catch(showError);
fullscreen.onclick = async () => {
    try {
        if (document.fullscreenElement === root) {
            await document.exitFullscreen();
        } else {
            await root.requestFullscreen();
        }
    } catch (reason) {
        showError(reason);
    }
};

Promise.resolve()
    .then(() => loadScript(
        "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js",
        () => Boolean(window.Chart),
    ))
    .then(() => loadScript(
        "https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js",
        () => Boolean(window.JSZip),
    ))
    .then(() => loadScript(
        "https://cdn.jsdelivr.net/npm/pptxviewjs/dist/PptxViewJS.min.js",
        () => Boolean(window.PptxViewJS && window.PptxViewJS.PPTXViewer),
    ))
    .then(() => {
        if (disposed) return;
        const PPTXViewer = window.PptxViewJS && window.PptxViewJS.PPTXViewer;
        if (!PPTXViewer) throw new Error("PptxViewJS did not expose its viewer API.");
        viewer = new PPTXViewer({ canvas });
        viewer.on && viewer.on("loadComplete", applySlideAspect);
        viewer.on && viewer.on("renderComplete", updateStatus);
        resizeObserver = new ResizeObserver(sizeCanvas);
        resizeObserver.observe(stage);
        status.textContent = "Loading presentation…";
        return viewer.loadFile(decodeBase64(data.pptxBase64))
            .then(() => {
                if (disposed) return;
                applySlideAspect();
                return viewer.render(canvas, { slideIndex: 0 });
            })
            .then(updateStatus);
    })
    .catch(showError);

return () => {
    disposed = true;
    renderVersion += 1;
    if (resizeObserver) resizeObserver.disconnect();
    prev.onclick = null;
    next.onclick = null;
    fullscreen.onclick = null;
};
}
"""

_PPTX_VIEWER = st.components.v2.component(
        "deepagent_pptx_preview",
        html=_PPTX_VIEWER_HTML,
        css=_PPTX_VIEWER_CSS,
        js=_PPTX_VIEWER_JS,
)


def pptx_preview(pptx_content: bytes, *, key: str) -> None:
        """Render a responsive PowerPoint preview with PptxViewJS."""
        _PPTX_VIEWER(
                data={"pptxBase64": base64.b64encode(pptx_content).decode("ascii")},
                key=key,
                width="stretch",
                height=820,
        )


def _make_model() -> ChatOpenAI:
    """Create the OpenAI-compatible model used by the existing notebook."""
    model_kwargs: dict[str, Any] = {
        "base_url": os.getenv("OPENAI_BASE_URL", "https://mlapi.run/v1"),
        "model": os.getenv("OPENAI_MODEL", "openai/gpt-6-luna"),
        "reasoning_effort": "none",
        "stream_usage": True,
        "streaming": True,
    }
    if os.getenv("OPENAI_API_KEY"):
        model_kwargs["api_key"] = os.environ["OPENAI_API_KEY"]
    return ChatOpenAI(**model_kwargs)


def _langfuse_callbacks() -> list[Any]:
    """Enable Langfuse tracing only when its credentials are configured."""
    if not (os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_PUBLIC_KEY")):
        return []
    try:
        from langfuse.langchain import CallbackHandler

        return [CallbackHandler()]
    except ImportError:
        st.warning("Langfuse credentials are set, but Langfuse is not installed; continuing without tracing.")
        return []


def _render_update(step_number: int, node: str, state_update: Any, log: Any) -> None:
    """Show each streamed graph update and its associated messages/tool calls."""
    with log.expander(f"Step {step_number} · {node}", expanded=False):
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


def _destroy_active_sandbox() -> None:
    """Destroy the active sandbox and clear its session state."""
    sandbox = st.session_state.pptx_sandbox
    try:
        if sandbox is not None:
            sandbox.destroy()
    finally:
        st.session_state.pptx_sandbox = None
        st.session_state.pptx_backend = None
        st.session_state.generated_presentations = []


def generate_presentations(
    instructions: str, slides_count: int, template: str
) -> list[tuple[str, bytes]]:
    """Generate presentations and return their bytes with the still-live sandbox."""
    sandbox = st.session_state.pptx_sandbox
    if sandbox is None:
        sandbox = SandboxSync.create(
            SANDBOX_IMAGE,
            timeout=timedelta(hours=24),
            connection_config=_sandbox_connection_config(),
        )
        st.session_state.pptx_sandbox = sandbox
        st.session_state.pptx_backend = OpenSandboxBackend(sandbox=sandbox)
    backend = st.session_state.pptx_backend
    backend.execute("mkdir -p /workspace/build /workspace/output")

    agent = create_deep_agent(
        tools=[],
        model=_make_model(),
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

    status = st.status("Generating your presentation…", expanded=False)
    with status.container():
        for step_number, update in enumerate(
            agent.stream(
                request,
                config={"callbacks": _langfuse_callbacks()},
                stream_mode="updates",
            ),
            start=1,
        ):
            for node, state_update in update.items():
                _render_update(step_number, node, state_update, st)

    status.update(label="Generation finished. Retrieving PowerPoint files…", state="complete")
    listing = backend.execute("ls -1 /workspace/output/*.pptx 2>/dev/null")
    output = getattr(listing, "output", str(listing))
    remote_paths = [line.strip() for line in output.splitlines() if line.strip().endswith(".pptx")]
    results: list[tuple[str, bytes]] = []
    for result, remote_path in zip(backend.download_files(remote_paths), remote_paths):
        content = getattr(result, "content", None)
        if content:
            results.append((Path(remote_path).name, content))
    return results


def main() -> None:
    st.set_page_config(
        page_title="DeepAgent PPTX Studio",
        page_icon=":material/slideshow:",
        layout="wide",
    )
    if "pptx_sandbox" not in st.session_state:
        st.session_state.pptx_sandbox = None
    if "pptx_backend" not in st.session_state:
        st.session_state.pptx_backend = None
    if "generated_presentations" not in st.session_state:
        st.session_state.generated_presentations = []

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
            slides_count = st.number_input("Number of slides", min_value=1, max_value=60, value=20, step=1)
        with col_template:
            template = st.selectbox("Design template", TEMPLATES, index=1)
        submitted = st.form_submit_button(
            "Generate presentation",
            type="primary",
            width="stretch",
            disabled=st.session_state.pptx_sandbox is not None,
        )

    if submitted:
        if not instructions.strip():
            st.error("Enter presentation instructions before generating.")
            return
        if not os.getenv("OPENAI_API_KEY"):
            st.error("Set `OPENAI_API_KEY` in `streamlit_app/.env.local` (or the environment) before generating.")
            return

        try:
            presentations = generate_presentations(instructions, int(slides_count), template)
        except Exception as exc:
            st.exception(exc)
            if st.session_state.pptx_sandbox is not None:
                st.info("The sandbox remains available for inspection. Use the reset button below when ready.")
        else:
            if not presentations:
                st.error("The agent finished, but no PowerPoint file was found in the sandbox output folder.")
            else:
                st.session_state.generated_presentations = presentations
                st.success(f"Generated {len(presentations)} presentation(s).")

    if st.session_state.generated_presentations:
        st.header("Your presentations")
        st.caption("Preview the landscape slides below, or download the original PowerPoint file.")
        for index, (filename, pptx_content) in enumerate(st.session_state.generated_presentations):
            st.subheader(Path(filename).stem.replace("_", " ").replace("-", " ").title())
            presentation_id = hashlib.sha256(pptx_content).hexdigest()[:12]
            st.download_button(
                "Download PowerPoint",
                data=pptx_content,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                icon=":material/download:",
                key=f"pptx-download-{index}-{presentation_id}",
            )
            pptx_preview(pptx_content, key=f"pptx-preview-{index}-{presentation_id}")

    if st.session_state.pptx_sandbox is not None:
        if st.button("Destroy sandbox and start over", type="secondary"):
            _destroy_active_sandbox()
            st.rerun()


if __name__ == "__main__":
    main()