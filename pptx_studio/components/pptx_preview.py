"""Browser-side PowerPoint slide preview component."""

from __future__ import annotations

import base64

import streamlit as st

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
