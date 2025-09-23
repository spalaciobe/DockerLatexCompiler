# Cross-Platform LaTeX Docker Compiler

This project provides a cross-platform solution for compiling LaTeX documents using Docker. It works on both Windows and Linux/Mac systems.

## Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Python 3.6+** (usually pre-installed on Linux/Mac, needs installation on Windows)

### Windows Setup
1. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. Install [Python](https://www.python.org/downloads/windows/) if not already installed
3. Make sure Docker Desktop is running

### Linux/Mac Setup
1. Install Docker Engine following [official instructions](https://docs.docker.com/engine/install/)
2. Python is usually pre-installed, verify with `python3 --version`

## Quick Start

1. **Build the Docker image** (first time only):
   ```bash
   python scripts/build.py
   ```

2. **Compile a specific LaTeX file**:
   ```bash
   python scripts/auto_compile.py ws_latex/master-thesis/presentation.tex
   ```

3. **Compile all files in a directory**:
   ```bash
   python scripts/compile.py master-thesis
   ```

## Usage

### Auto-Compile (Recommended)
Automatically detects the project folder from a .tex file path:

```bash
# Compile specific file
python scripts/auto_compile.py ws_latex/master-thesis/main.tex

# Search for .tex files in current directory
cd ws_latex/master-thesis
python ../../scripts/auto_compile.py
```

### Manual Directory Compilation
Compile all LaTeX files in a specific directory:

```bash
python scripts/compile.py master-thesis
python scripts/compile.py test
```

### VSCode Integration
The project includes VSCode tasks for easy compilation:

1. Open a `.tex` file in VSCode
2. Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac)
3. Select "Compile LaTeX (Auto-detect)" to compile the current file

Available tasks:
- **Compile LaTeX (Auto-detect)**: Compiles the currently open .tex file
- **Build LaTeX Docker Image**: Builds/rebuilds the Docker image
- **Compile LaTeX Directory**: Prompts for a directory to compile

## Configuration

Edit `config.json` to customize Docker settings:

```json
{
    "docker_image_name": "docker_latex_image",
    "docker_container_name": "docker_latex_container",
    "docker_network": "host"
}
```

## Cross-Platform Features

### Windows Compatibility
- Automatic Docker Desktop volume mount path conversion
- Windows-style path handling
- No bash script dependencies

### Linux/Mac Compatibility  
- Native Docker volume mounting
- Host network support
- Optimal performance

## Project Structure

```
DockerLatexCompiler/
├── scripts/
│   ├── auto_compile.py     # Cross-platform auto-detection compiler
│   ├── compile.py          # Cross-platform directory compiler
│   ├── build.py           # Cross-platform Docker image builder
│   ├── auto_compile.sh    # Legacy bash script (Linux only)
│   ├── compile.sh         # Legacy bash script (Linux only)
│   └── build.sh           # Legacy bash script (Linux only)
├── ws_latex/              # LaTeX projects directory
│   ├── master-thesis/     # Example project
│   └── test/              # Example project
├── .vscode/
│   ├── tasks.json         # VSCode tasks configuration
│   └── keybindings.json   # VSCode key bindings
├── config.json            # Cross-platform configuration
├── config_docker.sh       # Legacy bash configuration
├── Dockerfile             # Docker image definition
└── compile_latex.py       # Internal LaTeX compiler script
```

## Troubleshooting

### Docker Issues
- **Windows**: Ensure Docker Desktop is running and WSL2 backend is enabled
- **Linux**: Make sure your user is in the `docker` group: `sudo usermod -aG docker $USER`
- **All platforms**: Test Docker with: `docker run hello-world`

### Python Issues
- **Windows**: Make sure Python is in your PATH
- **All platforms**: Use `python3` instead of `python` if you get "command not found"

### Volume Mount Issues
- **Windows**: The scripts automatically handle path conversion for Docker Desktop
- **Linux**: Make sure the `ws_latex` directory exists and has proper permissions

## Legacy Support

The original bash scripts are still available for Linux users:
- `scripts/auto_compile.sh`
- `scripts/compile.sh`
- `scripts/build.sh`

However, we recommend using the Python scripts for better cross-platform compatibility.

## Contributing

When adding new features, please ensure they work on both Windows and Linux/Mac platforms. Test your changes on multiple operating systems when possible.
