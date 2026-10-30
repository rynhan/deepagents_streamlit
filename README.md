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
high privilege. Deploy only on a host dedicated to this application. Its server image is built
from `sandbox/OpenSandbox.Dockerfile`, which copies `sandbox/os-sandbox.toml` into the image;
there is no host-side config-file bind mount. The configured bridge network publishes sandbox
ports in `40000-60000`, so allow that range as required by the OpenSandbox runtime and firewall
design. Keep the SQLite state in the `opensandbox-data` volume.

`OPEN_SANDBOX_API_KEY` is a secret you generate and set in Coolify; it is shared by the app and
server and is not issued by OpenSandbox. The server config restricts host-path mounts to
`/opt/opensandbox/allowed-host-mounts`; the app does not currently request host mounts. The
allowlisted path is on the Docker host, so create it there only if you enable host mounts, keep
it empty of sensitive data, and review the allowlist before enabling that feature.

If Coolify cannot resolve Compose service names from app containers, put both services on the
same Coolify network and set `OPEN_SANDBOX_DOMAIN` to the OpenSandbox service's internal DNS
name and port. The app defaults to the Compose service address `opensandbox-server:8090`.

Compose builds the PPTX sandbox image from `sandbox/Dockerfile` and tags it `pptx-sandbox:1`
by default. A one-shot Compose service ensures the image is built in the same Docker daemon
used by OpenSandbox through the host Docker socket, then exits; OpenSandbox can use that image
when it creates a sandbox. To override the image name, set `PPTX_SANDBOX_IMAGE` in Coolify.
OpenSandbox also needs to pull its configured `opensandbox/execd:v1.1.0` runtime image.

The deployment server config is `sandbox/os-sandbox.toml`. It is copied into the custom
OpenSandbox server image, so Compose does not depend on a config-file bind mount from Coolify's
host checkout. Verify sandbox creation and agent file operations before opening the app publicly.

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
3. Start the OpenSandbox server with the appropriate local configuration and run the app:

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
