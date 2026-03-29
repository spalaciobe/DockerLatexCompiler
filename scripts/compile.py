#!/usr/bin/env python3
"""
Cross-platform LaTeX compilation script
Compiles LaTeX files in a specified directory using Docker

Usage: python compile.py <article_directory>
Examples:
  python compile.py master-thesis                # Compile ws_latex/master-thesis/
  python compile.py /path/to/any/latex/project   # Compile from any location
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
import platform

class LaTeXCompiler:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.resolve()
        self.config = self.load_config()
        self.is_windows = platform.system() == "Windows"

    def load_config(self):
        """Load Docker configuration from config file"""
        config_file = self.project_root / "config.json"

        # Default configuration
        default_config = {
            "docker_image_name": "docker_latex_image",
            "docker_container_name": "docker_latex_container",
            "docker_network": "host"
        }

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
            except (json.JSONDecodeError, IOError):
                print("Warning: Could not read config.json, using defaults")

        return default_config

    def _format_docker_path(self, host_path):
        """Convert a host path to Docker-compatible format"""
        path_str = str(host_path).replace("\\", "/")
        if self.is_windows and len(path_str) > 1 and path_str[1] == ":":
            path_str = f"/{path_str[0].lower()}{path_str[2:]}"
        return path_str

    def get_docker_volume_mount(self, host_path, container_dir_name=None):
        """Get the appropriate Docker volume mount syntax.

        Args:
            host_path: Path on the host to mount
            container_dir_name: If set, mount as /home/dockeruser/ws_latex/<name>.
                              If None, mount directly as /home/dockeruser/ws_latex.
        """
        docker_path = self._format_docker_path(host_path)

        container_target = "/home/dockeruser/ws_latex"
        if container_dir_name:
            container_target = f"/home/dockeruser/ws_latex/{container_dir_name}"

        return f"{docker_path}:{container_target}"

    def _is_external_path(self, article_dir):
        """Check if the argument is an external absolute/relative path rather than a ws_latex subfolder name."""
        p = Path(article_dir)
        return p.is_absolute() or os.sep in article_dir or "/" in article_dir

    def compile_article(self, article_dir):
        """Compile LaTeX files in the specified article directory"""

        if self._is_external_path(article_dir):
            # External directory
            dir_path = Path(article_dir).resolve()
            if not dir_path.exists():
                print(f"[ERROR] Directory '{dir_path}' does not exist")
                return False
            if not dir_path.is_dir():
                print(f"[ERROR] '{dir_path}' is not a directory")
                return False

            folder_name = dir_path.name
            volume_mount = self.get_docker_volume_mount(dir_path, folder_name)
            print(f"[COMPILE] LaTeX files in {dir_path}/")
        else:
            # Internal: relative to ws_latex/
            folder_name = article_dir
            article_path = self.project_root / "ws_latex" / article_dir
            if not article_path.exists():
                print(f"[ERROR] Directory 'ws_latex/{article_dir}' does not exist")
                print("   Available directories:")
                ws_latex_path = self.project_root / "ws_latex"
                if ws_latex_path.exists():
                    for item in ws_latex_path.iterdir():
                        if item.is_dir():
                            print(f"   - {item.name}")
                return False

            volume_mount = self.get_docker_volume_mount(self.project_root / "ws_latex")
            print(f"[COMPILE] LaTeX files in ws_latex/{article_dir}/")

        # Build Docker command
        cmd = [
            "docker", "run", "--rm",
            "--volume", volume_mount,
            "--dns=8.8.8.8"
        ]

        # Add network configuration (not supported on Windows Docker Desktop with host network)
        if not self.is_windows and self.config["docker_network"] != "host":
            cmd.extend(["--network", self.config["docker_network"]])
        elif not self.is_windows:
            cmd.extend(["--network", "host"])

        cmd.append(self.config["docker_image_name"])
        cmd.append(folder_name)

        try:
            print(f"[DOCKER] Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True)
            print("[SUCCESS] Compilation completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Docker compilation failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            print("[ERROR] Docker is not installed or not in PATH")
            print("   Please install Docker Desktop and make sure it's running")
            return False

def main():
    parser = argparse.ArgumentParser(description="Compile LaTeX files using Docker")
    parser.add_argument("article_directory", help="Directory name (relative to ws_latex/) or absolute path")

    args = parser.parse_args()

    if not args.article_directory:
        print("Usage: python compile.py <article_directory>")
        print("Example: python compile.py master-thesis")
        print("         python compile.py /path/to/latex/project")
        sys.exit(1)

    compiler = LaTeXCompiler()
    success = compiler.compile_article(args.article_directory)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
