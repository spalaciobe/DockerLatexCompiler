# Docker LaTeX Container

This project provides a Docker container that uses pdflatex to compile LaTeX projects. LaTeX projects should be organized as subfolders within the [`ws_latex`](./ws_latex/) directory.

## Prerequisites

- Docker installed on your system.
- Basic knowledge of LaTeX document structure.

## Setup

Build the Docker container (Required only once or if [Dockerfile](./Dockerfile) is modified):
   ```bash
   ./scripts/build.sh
   ```

## Usage

### Basic Compilation

1. **Create your LaTeX project** in the [`ws_latex`](./ws_latex/) directory
    ```
    ws_latex/
    ├── your_project/
    │   ├── main.tex          # Main LaTeX file (required)
    │   ├── references.bib    # Bibliography file (optional)
    │   ├── images/           # Images directory (optional)
    │   └── ...              # Other LaTeX files
    ```
2. **Compile your project:**
   ```bash
   ./scripts/compile.sh your_project
   ```

### Compile a specific .tex file (auto-detection)

Use the helper script to detect the project folder automatically from a `.tex` file path:

- From anywhere, passing a file path inside `ws_latex/`:
  ```bash
  ./scripts/auto_compile.sh ws_latex/your_project/main.tex
  ```

- From a directory that contains one or more `.tex` files (it will prompt you to select when multiple are found):
  ```bash
  cd ws_latex/your_project
  ../../scripts/auto_compile.sh
  ```

Notes:
- The script requires the `.tex` file to reside under `ws_latex/`.
- If there is more than one `.tex` file in the directory and no `main.tex`, the first one will be selected unless you choose otherwise in the prompt.

### VS Code: compile with Ctrl+Shift+B

This repository includes VS Code (and VS Code Forks) configuration to compile the current `.tex` file using `Ctrl+Shift+B` when a `.tex` editor is focused.

- `.vscode/tasks.json`: defines the task "Compile LaTeX (Auto-detect)" which calls `scripts/auto_compile.sh` with the current file.
- `.vscode/keybindings.json`: binds `Ctrl+Shift+B` to run that task only when a `.tex` file is focused.

How to use:
1. Open this folder in VS Code (or VS Code Forks).
2. Build the Docker image once: `./scripts/build.sh`.
3. Open any `.tex` file under `ws_latex/your_project/`.
4. Press `Ctrl+Shift+B` to compile. The output will appear in the VS Code terminal panel.

Alternative:
- Use the Command Palette → "Run Build Task" → "Compile LaTeX (Auto-detect)".

### Advanced: run the container directly

If you prefer to invoke Docker manually (same behavior as `compile.sh`), mount `ws_latex/` and pass the project folder name. Optionally pass a specific `.tex` filename as a second argument.

```bash
docker run --rm \
  --volume "$(pwd)/ws_latex:/home/dockeruser/ws_latex" \
  --network host \
  --dns=8.8.8.8 \
  docker_latex_image \
  "your_project"               # or: "your_project" "another.tex"
```

The image name and other parameters are defined in `config_docker.sh` and used by the scripts.

## Examples

Compiling the test project:
```bash
./scripts/compile.sh test
```

Compiling a specific file from its path:
```bash
./scripts/auto_compile.sh ws_latex/test/main.tex
```


## License

This project is licensed under a custom Academic/Personal Use License. See the [LICENSE](./LICENCE) file for details.

## Author

**Alejandro Daniel José Gómez Flórez**  
[LinkedIn](http://linkedin.com/in/aldajo92) | [GitHub](https://github.com/aldajo92)