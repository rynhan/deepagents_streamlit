# DeepAgent PPTX Studio

A small Streamlit front end for the existing deepagents + OpenSandbox PowerPoint generator.
The `sandbox/` directory is copied from the parent project and includes the PPTX skill and
all five presentation template skills.

## Run on Coolify with Docker

This repo includes a Streamlit `Dockerfile` and a Compose deployment for the UI plus the
OpenSandbox Docker runtime. In Coolify, create a Docker Compose resource from this directory
(or point the resource at `streamlit_app/docker-compose.yml`). Configure the required secrets
in Coolify's environment settings, including `OPENAI_API_KEY` and a strong, random
`OPEN_SANDBOX_API_KEY`. The API key is applied to both services; do not publish the
OpenSandbox server port publicly.

Expose the `streamlit` service on port `8501` through Coolify's proxy and enable HTTPS. The
OpenSandbox service uses the host Docker socket and creates sibling sandbox containers; this is
high privilege. Deploy only on a host dedicated to this application. The configured bridge
network publishes sandbox ports in `40000-60000`, so allow that range as required by the
OpenSandbox runtime and firewall design. Keep the SQLite state in the `opensandbox-data` volume.

If Coolify cannot resolve Compose service names from app containers, put both services on the
same Coolify network and set `OPEN_SANDBOX_DOMAIN` to the OpenSandbox service's internal DNS
name and port. The app defaults to the Compose service address `opensandbox-server:8090`.

Build the separate PPTX sandbox image on the Docker host used by OpenSandbox and make the image
available to that host's Docker daemon under the name `pptx-sandbox:1`. The existing sandbox
Dockerfile is the build context `streamlit_app/sandbox`; it is intentionally separate from the
Streamlit UI image. For a single host, build/pull it on that same host. For multiple hosts, push
it to a private registry and configure `PPTX_SANDBOX_IMAGE` to that registry image. OpenSandbox
also needs to pull its configured `opensandbox/execd:v1.1.0` runtime image.

The Compose server config is in `sandbox/coolify.os-sandbox.toml`. It uses the host-gateway
routing pattern for sandboxes created from a server container. If Docker networking on your
Coolify host differs, verify sandbox creation and agent file operations before opening the app
publicly.

## Local setup

1. Build the sandbox image from this project's copied sandbox directory, or use an image that
   already contains the same skills:

   ```bash
   cd sandbox
   docker build -t pptx-sandbox:1 .
   ```

2. Install the Python requirements in a virtual environment, then configure
   `OPENAI_API_KEY` in `.env.local` (or in the process environment). `OPENAI_BASE_URL` and
   `OPENAI_MODEL` can override the notebook defaults. Langfuse tracing is enabled when both
   `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY` are set.
3. Start the OpenSandbox server using `sandbox/os-sandbox.toml` and run the app:

   ```bash
   streamlit run app.py
   ```

The form accepts instructions, slide count, and one of the template skills under
`sandbox/skills/template-*`. The selected skill is pinned for the agent. Progress updates
are displayed during the run, and generated `.pptx` files are previewed in a wide, landscape
viewer using PptxViewJS. Each generated file can be downloaded from the app. The
viewer supports slide navigation but not editing. It loads PptxViewJS and its rendering
dependencies from jsDelivr, so the user's browser needs network access to that CDN. The sandbox
stays alive (up to the configured 24-hour sandbox maximum) until the user selects
**Destroy sandbox and start over**.
