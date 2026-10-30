# PPTX sandbox image for OpenSandbox + Deep Agents

A Docker image with everything an agent needs to build `.pptx` decks, with your **skills baked in**
at `/skills`, so nothing has to be uploaded when a sandbox starts.

```
sandbox/
├── Dockerfile
├── .dockerignore
├── README.md
├── fonts/                 # optional .ttf/.otf files; the folder must exist, it can be empty
└── skills/
    ├── pptx/                       # general PPTX creation, editing, and QA
    ├── template-cobalt-grid/       # optional visual design skill
    ├── template-monochrome/
    ├── template-neo-grid-bold/
    ├── template-raw-grid/
    ├── template-soft-editorial/
    └── frontend-slides/            # optional HTML presentation skill
```

`skills/pptx/` is the base skill for `.pptx` work. Optional design/template skills use the
`template-<slug>/` naming convention. Each skill is a separate direct child of `skills/`, not a
subfolder inside `pptx/`. The directory name must match the `name:` in its `SKILL.md` frontmatter.
`frontend-slides/` is optional and is for HTML presentations rather than `.pptx` output.

The image contains Node 22 + `pptxgenjs`, Python 3 + `markitdown`, Pillow, `defusedxml`, `lxml`, `python-pptx`,
LibreOffice (headless), Poppler (`pdftoppm`), common fonts, and your `skills/` folder at `/skills`.
The agent works in `/workspace/build` (scripts) and `/workspace/output` (deliverables).

## Prerequisites

- **Docker Engine from Docker's official apt repository, not the snap package.** OpenSandbox starts containers
  with `no-new-privileges`, which snap Docker's AppArmor profile rejects (the container dies instantly with
  `exec /opt/opensandbox/bootstrap.sh: operation not permitted`).
- The OpenSandbox server running locally (`uvx opensandbox-server --config ./os-sandbox.toml`).
- Python packages: `opensandbox`, `langchain-opensandbox`, `deepagents` (0.7.23 or newer if you use `pinned_skills`).

## 1. Prepare the folders

```bash
cd sandbox
mkdir -p fonts skills/pptx skills/template-my-design
# Put each skill directly under skills/<skill-name>/.
# Each skill directory needs SKILL.md, with `name:` matching its folder name.
```

Example template skill structure:

```
skills/
├── pptx/
│   ├── SKILL.md
│   └── scripts/
└── template-my-design/
    ├── SKILL.md
    ├── assets/
    ├── examples/
    └── references/
```

Do not put templates under `skills/pptx/` or add a nesting level such as
`skills/templates/template-my-design/`: `/skills/` is scanned for immediate child skill
directories containing `SKILL.md`.

Optional: put font files in `fonts/` (for example Cormorant Garamond and Work Sans from Google Fonts)
so LibreOffice renders templates faithfully during QA. People who open the finished deck still need those
fonts installed, or a fallback.

## 2. Build

```bash
docker build -t pptx-sandbox:1 .
```

The first build takes several minutes and the image is over 1 GB. The build ends with a smoke test
(pptxgenjs, Python imports, LibreOffice, Poppler) and checks that every skill folder has a `SKILL.md`.

Useful build options:

```bash
docker build --build-arg WITH_ICONS=0 -t pptx-sandbox:1 .      # skip react-icons/sharp (smaller image)
docker build --build-arg SKILLS_DIR=/opt/skills -t pptx-sandbox:1 .   # different skills path
```

## 3. Verify

```bash
# skills are in the image
docker run --rm pptx-sandbox:1 ls /skills

# OpenSandbox's security flag works with your Docker (should print "ok")
docker run --rm --security-opt no-new-privileges=true pptx-sandbox:1 echo ok

# custom fonts were picked up (only if you added some)
docker run --rm pptx-sandbox:1 fc-list | grep -i cormorant
```

## 4. Use it

```python
from deepagents import create_deep_agent
from langchain_opensandbox import OpenSandboxBackend
from opensandbox import SandboxSync

IMAGE = "pptx-sandbox:1"

sandbox = SandboxSync.create(IMAGE)   # add connection_config=... if your server is not on the default address
try:
    backend = OpenSandboxBackend(sandbox=sandbox, timeout=300)

    agent = create_deep_agent(
        tools=[],
        model=model,
        system_prompt=SYSTEM_PROMPT,   # tell it: skill scripts are under /skills/<name>/scripts/
        backend=backend,
        skills=["/skills/"],          # parent directory containing skill folders
    )

    request = {
        "messages": [{"role": "user", "content": "Create a 12-slide deck about ..."}],
        "pinned_skills": ["pptx", "template-cobalt-grid"],
    }
    # ... agent.stream(request, stream_mode="updates") ...

    # Copy results out BEFORE destroying the sandbox
    listing = backend.execute("ls -1 /workspace/output/*.pptx")
    # ... backend.download_files([...]) and write the bytes to disk ...
finally:
    sandbox.destroy()
```

Replace `template-cobalt-grid` with the selected skill's directory/frontmatter name, such as
`template-monochrome`. If no template is selected, pin only `pptx`. Choose the template in your
application code (for example, from a dropdown or explicit name matching); do not ask the model to
guess. Template skills provide visual guidance, while `pptx` handles deck generation and QA.

## Changing skills

1. Edit files under `skills/`.
2. Rebuild with a new tag: `docker build -t pptx-sandbox:2 .` (takes seconds, because the skills layer is last).
3. Create a **new** sandbox from the new tag. A running sandbox keeps the image it started from.

Quick iteration without rebuilding: after creating a sandbox, `backend.upload_files([...])` can overwrite files
under `/skills/` for that sandbox only. When you're happy, rebuild so the image matches.

### Adding a template skill

Create `skills/template-<slug>/SKILL.md` with frontmatter `name: template-<slug>` (exactly matching
the directory name) and a description explaining when to use the design. Put supporting files such
as `assets/`, `examples/`, and `references/` inside that directory. Rebuild, then pin both `pptx`
and the selected `template-<slug>` in `pinned_skills`.

## Troubleshooting

| Symptom                                                                          | Likely cause and fix                                                                                                                                                              |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Container exits right after start, `docker logs` shows `operation not permitted` | You are on snap Docker. Install Docker Engine from the apt repo.                                                                                                                  |
| Build fails at the smoke test                                                    | A package failed to install. Read the step output; rerun with `--progress=plain`.                                                                                                 |
| Build fails with `has no SKILL.md`                                               | A skill directory directly under `skills/` is missing `SKILL.md`, or a skill is nested too deeply.                                                                                |
| Agent doesn't see a skill                                                        | `skills=[...]` must point at the directory containing skill folders (`/skills/` here); each immediate child's `name:` must match its folder name.                                 |
| Agent sees `pptx` but not a template skill                                       | Put `template-<slug>/` directly under `skills/`, match its folder and frontmatter names, rebuild, and pin the template in `pinned_skills`.                                        |
| Agent can't find skill scripts                                                   | Use absolute paths like `/skills/pptx/scripts/office/validate.py`.                                                                                                                |
| `soffice` hangs                                                                  | Use the skill's `scripts/office/soffice.py` wrapper, or try `HOME=/tmp soffice ...`.                                                                                              |
| Fonts look wrong in renders                                                      | Add the font files to `fonts/` and rebuild.                                                                                                                                       |
| Sandbox disappears mid-run                                                       | Sandboxes expire. The `opensandbox.io/expires-at` label on the container (`docker inspect`) showed about 10 minutes in testing. Check the SDK's `create()` options for a timeout. |
| Output file missing                                                              | Download from `/workspace/output` before `sandbox.destroy()`. While a sandbox is alive, you can also use `docker cp <container>:/workspace/output/<file> .`                       |

## Security notes

- The local OpenSandbox server was started without an API key. Keep it bound to `127.0.0.1`, and set
  `server.api_key` before exposing it anywhere.
- Don't remove `no-new-privileges` or other restrictions from the server config to make things work; fix the Docker install instead.
