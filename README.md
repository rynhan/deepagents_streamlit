# DeepAgent PPTX Studio

A small Streamlit front end for the existing deepagents + OpenSandbox PowerPoint generator.
The `sandbox/` directory is copied from the parent project and includes the PPTX skill and
all five presentation template skills.

## Run on Coolify with Docker

This repo includes a Streamlit `Dockerfile` and a Compose deployment for the UI plus the
OpenSandbox Docker runtime. In Coolify, create a Docker Compose resource from this directory
(or point the resource at `streamlit_app/docker-compose.yml`). Configure the required secrets
in Coolify's environment settings, including `OPENAI_API_KEY`, `SUPABASE_URL`,
`SUPABASE_SERVICE_ROLE_KEY`, and a strong, random `OPEN_SANDBOX_API_KEY`. Supabase credentials
are used only by the Streamlit server; never expose the service-role key in browser code. Create
the `files` Storage bucket in Supabase before deploying. The API key is applied to both services;
do not publish the OpenSandbox server port publicly.

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

1. From the project root, build the sandbox image:

   ```bash
   docker build -t pptx-sandbox:1 -f sandbox/Dockerfile sandbox
   ```

2. Install the Python requirements and create `.env.local`:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   cp .env.example .env.local
   ```

   Set `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and a random
   `OPEN_SANDBOX_API_KEY` in `.env.local`. Create the `files` bucket in Supabase. The service-role
   key grants broad access, so keep it server-side and do not commit it. Set
   `OPENAI_BASE_URL` if using a non-default OpenAI-compatible endpoint. Set
   `OPEN_SANDBOX_DOMAIN=127.0.0.1:8090` for the host-run server below.

3. Start the OpenSandbox server in one terminal. Run from the project root:

   ```bash
   set -a
   . ./.env.local
   set +a
   OPENSANDBOX_SERVER_API_KEY="$OPEN_SANDBOX_API_KEY" \
     uvx opensandbox-server --config ./sandbox/os-sandbox.toml
   ```

4. In a second terminal, from the project root, start Streamlit:

   ```bash
   cd /path/to/deepagents_streamlit
   set -a
   . ./.env.local
   set +a
   .venv/bin/streamlit run app.py
   ```

   Open the local URL shown by Streamlit. The OpenSandbox API key must match the server key.

Alternatively, run all containers locally with `docker compose up --build`; the Compose setup
builds the UI, server, and sandbox images and is closest to the Coolify deployment.

## Code layout

```text
app.py                         # Small Streamlit entry point
prompts.py                     # System and user prompt construction
pptx_studio/
  config.py                    # Environment loading and model/template options
  generation.py                # OpenSandbox lifecycle and agent execution
  models.py                    # Chat model and optional Langfuse callback factories
  ui.py                        # Streamlit form, session state, and comparison results
  components/pptx_preview.py   # Browser-side PowerPoint preview
```

The UI owns Streamlit state and rendering; `generation.py` handles sandbox and agent work
without importing Streamlit. This keeps UI changes separate from generation behavior.

The form accepts instructions, slide count, one of the template skills under
`sandbox/skills/template-*`, and one to three models. Selected models generate concurrently in
separate sandboxes, which increases API usage and host CPU/memory/network demand. The app shows
a summary table, expandable per-model logs with expandable steps, and side-by-side previews with
download buttons. Each generated `.pptx` is uploaded immediately after retrieval to the private
Supabase Storage bucket named `files` and can also be downloaded from the app. Objects are stored
under `presentations/YYYY/MM/DD/<run-id>/<model>/<filename>` to avoid collisions. The result
table reports upload counts and any upload failures; a failed upload does not discard the deck
from the current session. The bucket must already exist. The viewer supports
slide navigation but not editing, and loads PptxViewJS from jsDelivr, so the browser needs CDN
access. Each temporary sandbox is destroyed after its model run completes.
