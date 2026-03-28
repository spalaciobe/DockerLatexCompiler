# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Build the Docker image** (required once before first use):
```bash
python scripts/build.py
```

**Compile a specific .tex file** (auto-detects project folder from path):
```bash
python scripts/auto_compile.py ws_latex/master-thesis/main.tex
```

**Compile all files in a directory** (directory is relative to `ws_latex/`):
```bash
python scripts/compile.py master-thesis
```

**Run `auto_compile.py` without arguments** (searches for `.tex` files in the current directory, useful when `cd`'d into a project):
```bash
python scripts/auto_compile.py
```

## VSCode Integration

Three build tasks are pre-configured in `.vscode/tasks.json`:

- **Compile LaTeX (Auto-detect)** (default build, `Ctrl+Shift+B`): runs `auto_compile.py` against the currently open file.
- **Build LaTeX Docker Image**: runs `build.py`.
- **Compile LaTeX Directory**: prompts for a directory name (relative to `ws_latex/`) then runs `compile.py`.

## Architecture

This project wraps `pdflatex` in an Alpine-based Docker container so that LaTeX can be compiled without a local TeX installation.

**Execution flow:**

1. Host Python scripts (`scripts/*.py`) build a `docker run` command that volume-mounts `ws_latex/` into the container at `/home/dockeruser/ws_latex`.
2. The Docker container's entrypoint (`/usr/local/bin/compile_article.sh`) invokes `compile_latex.py` (copied into the image at build time).
3. `compile_latex.py` runs inside the container and executes: `pdflatex` → `bibtex` (if `.bib` files exist) → `pdflatex` → `pdflatex`.

**Key distinction:** `compile_latex.py` at the repo root runs **inside Docker**. The scripts under `scripts/` run **on the host** and orchestrate Docker.

**Windows path handling:** On Windows, `scripts/auto_compile.py` and `scripts/compile.py` convert Windows-style paths (`C:\path`) to Docker Desktop's expected format (`/c/path`) for volume mounts. Host networking (`--network host`) is skipped on Windows since Docker Desktop doesn't support it.

**Configuration:** `config.json` controls the Docker image name, container name, and network. All Python scripts load this file at runtime with fallback defaults.

**LaTeX workspace:** All LaTeX projects live under `ws_latex/`. Each subdirectory is an independent project. The scripts detect the project folder from the path segment immediately after `ws_latex/`.

**LaTeX packages:** The image includes `texmf-dist-latexextra` and `texmf-dist-fontsextra`. To add more Alpine TeX packages, add `apk add --no-cache <package>` to the `Dockerfile` and rebuild.

**Auxiliary file cleanup:** `compile_latex.py` deletes `.aux`, `.log`, `.bbl`, and other build artifacts after each successful compilation. Pass `--no-clean-after` to the in-container script to retain them for debugging (not exposed by the host scripts directly).

**Legacy bash scripts** (`scripts/*.sh`) are Linux-only and kept for backwards compatibility. Prefer the Python equivalents.
