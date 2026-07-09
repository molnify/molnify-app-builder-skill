# Molnify App Builder - Agent Skill

The official [Agent Skill](https://agentskills.io) for building **Molnify apps** -
spreadsheet-driven web apps where Excel or Google Sheets formulas do the calculation and
colored cells define the inputs, outputs, charts, and actions.

It covers the whole job: building an app from scratch, converting an existing
spreadsheet into one, validating it, and styling it. Inside are a `SKILL.md` entry
point, companion reference guides, worked examples, and Python tools for inspecting and
validating `.xlsx` files.

It's plain text and Apache-2.0 licensed, so there's nothing to take on trust: every
instruction the agent follows and every line the Python tools run is readable right
here.

## What you can build

Calculators and quoting tools, ROI and pricing models, dashboards, multi-step forms and
wizards, inspection and field-report apps with PDF output, internal tools backed by a
database. If you can model it in a spreadsheet, you can ship it as an app.

## Use it with any AI

It's an open Agent Skill, so it works the same in Claude Code, OpenAI Codex, Cursor,
Gemini CLI, GitHub Copilot, and the other skills-compatible agents. Add it once and build
Molnify apps from whichever one you already use. Any other AI works too: just point it at
`SKILL.md`.

### Discover & install from molnify.com

```bash
npx skills add https://app.molnify.com
```

This reads the discovery manifest at
`https://app.molnify.com/.well-known/agent-skills/index.json`, verifies the download
against its published SHA-256 digest, and installs the skill into the right place for
your agent (e.g. `~/.claude/skills/` for Claude Code).

### Claude Code (manual)

```bash
# Personal (all projects):
git clone https://github.com/molnify/molnify-app-builder-skill ~/.claude/skills/molnify-app-builder

# Or per-project:
git clone https://github.com/molnify/molnify-app-builder-skill .claude/skills/molnify-app-builder
```

### Claude.ai

Download a release `.zip` (below) and upload it as a skill in Settings → Capabilities.

### Any other AI (web or CLI)

Download or clone the repo and give the assistant `SKILL.md` as context; it links to
the companion guides as it needs them.

## Updating

Installs are **version-pinned**: the skills CLI records the exact release it downloaded,
and `npx skills update` does not check skills installed from a discovery manifest (it
lists them under "cannot be checked automatically"). To update, re-run the install
command - the manifest always points at the latest release:

```bash
npx skills add https://app.molnify.com
```

If you cloned the repo instead, run `git pull` in the skill directory. On Claude.ai,
download the latest release `.zip` and upload it again.

Your installed version is in the `VERSION` file (and `SKILL.md` frontmatter); compare
with the [latest release](https://github.com/molnify/molnify-app-builder-skill/releases/latest).

## Pin a version

Releases follow [semantic versioning](https://semver.org). Pin to a tag for
reproducible behavior:

```bash
# Clone a specific version:
git clone --branch v1.0.0 https://github.com/molnify/molnify-app-builder-skill

# Or download an immutable release asset:
#   https://github.com/molnify/molnify-app-builder-skill/releases/tag/v1.0.0
```

The `latest` discovery manifest always points at the most recent release; pin via tag
when you need a fixed version.

## Verify what you downloaded

Each release ships a `SHA256SUMS` file, and the discovery manifest carries a
`digest: "sha256:…"` of the release archive that compliant clients **must** verify
before use.

```bash
# Verify a cloned/extracted tree:
sha256sum -c SHA256SUMS
```

See [`SECURITY.md`](SECURITY.md) for what the bundled Python tools do (and do not do)
and how to report a concern.

## What's inside

| File | Purpose |
|------|---------|
| `SKILL.md` | Entry point - metadata + the primary build reference |
| `creating-from-scratch.md`, `converting-excel.md` | Step-by-step build workflows |
| `patterns.md`, `design.md`, `styling.md`, `styling-examples.md` | UX, design, and CSS |
| `database.md`, `custom-frontend.md`, `report-templates.md`, `advanced-topics.md`, `python.md` | Deeper topics |
| `examples/` | Worked example apps |
| `molnify_inspect_excel.py` | Analyze a plain `.xlsx` before conversion |
| `molnify_validate.py` | Check a built Molnify app for common issues |
| `molnify_builder.py` | Programmatic app construction (`AppBuilder`) |
| `molnify_app_builder-*.whl`, `pyproject.toml` | Install the tools into a Python environment (`pip install …whl`) |

## License

[Apache-2.0](LICENSE). Copyright Molnify.
