# Security

This skill is plain text and open source: Markdown instructions plus a few Python tools
for working with Excel files. This document describes what the tools do, so your security
team can verify it's safe before allowing its use.

## What the bundled tools do

| Tool | What it does | Network | Filesystem |
|------|--------------|---------|------------|
| `inspect_excel.py` | Reads a `.xlsx` and prints cell values, formulas, colors, charts, and dependency analysis | None | Reads the file you pass it |
| `validate.py` | Reads a built Molnify app `.xlsx` and reports common issues | None | Reads the file you pass it |
| `molnify_builder.py` | Library for constructing a Molnify `.xlsx` programmatically | None | Writes the `.xlsx` you ask it to build |
| `setup.sh` | Creates a local Python virtualenv and installs `requirements.txt` (`openpyxl`) via pip | pip downloads `openpyxl` | Creates a `.venv/` directory |

The tools:

- **Make no network calls** (other than `setup.sh` invoking `pip` to install `openpyxl`,
  which you can skip if `openpyxl` is already available).
- **Send no telemetry** and collect no usage data.
- **Access no credentials, environment secrets, or files** beyond the spreadsheet paths
  you explicitly pass on the command line.
- **Are read-only** except `molnify_builder.py`, which writes the `.xlsx` you ask it to
  produce, and `setup.sh`, which creates a local `.venv/`.

The Markdown guides are documentation only. They contain instructions for an AI agent
and do not execute anything by themselves.

## Verifying integrity

- Every release ships a `SHA256SUMS` file. Verify an extracted tree with
  `sha256sum -c SHA256SUMS`.
- The Agent Skills discovery manifest at
  `https://app.molnify.com/.well-known/agent-skills/index.json` carries a
  `digest: "sha256:…"` of the release archive. Compliant clients must verify the
  download against it before use.
- Pin to a release tag (e.g. `v1.0.0`) for reproducible, auditable behavior.

## Reporting a vulnerability

Please report security concerns to **security@molnify.com**. We aim to acknowledge
reports within a few business days.
