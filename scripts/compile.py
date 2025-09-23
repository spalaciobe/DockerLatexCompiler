#!/usr/bin/env python3
"""
Cross-platform LaTeX compilation script
Compiles LaTeX files in a specified directory using Docker

Usage: python compile.py <article_directory>
Example: python compile.py master-thesis
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
                print("⚠️  Warning: Could not read config.json, using defaults")
                
        return default_config

    def get_docker_volume_mount(self):
        """Get the appropriate Docker volume mount syntax for the current OS"""
        ws_latex_path = self.project_root / "ws_latex"
        
        if self.is_windows:
            # Windows Docker Desktop format
            windows_path = str(ws_latex_path).replace("\\", "/")
            if windows_path[1] == ":":
                # Convert C:\path to /c/path format for Docker Desktop
                windows_path = f"/{windows_path[0].lower()}{windows_path[2:]}"
            return f"{windows_path}:/home/dockeruser/ws_latex"
        else:
            # Linux/Mac format
            return f"{ws_latex_path}:/home/dockeruser/ws_latex"

    def compile_article(self, article_dir):
        """Compile LaTeX files in the specified article directory"""
        
        # Check if article directory exists
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
            
        print(f"[COMPILE] LaTeX files in ws_latex/{article_dir}/")
        
        # Build Docker command
        cmd = [
            "docker", "run", "--rm",
            "--volume", self.get_docker_volume_mount(),
            "--dns=8.8.8.8"
        ]
        
        # Add network configuration (not supported on Windows Docker Desktop with host network)
        if not self.is_windows and self.config["docker_network"] != "host":
            cmd.extend(["--network", self.config["docker_network"]])
        elif not self.is_windows:
            cmd.extend(["--network", "host"])
            
        cmd.append(self.config["docker_image_name"])
        cmd.append(article_dir)
        
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
    parser.add_argument("article_directory", help="Directory containing LaTeX files (relative to ws_latex/)")
    
    args = parser.parse_args()
    
    if not args.article_directory:
        print("Usage: python compile.py <article_directory>")
        print("Example: python compile.py master-thesis")
        print("This will compile the LaTeX files in ws_latex/<article_directory>/")
        sys.exit(1)
        
    compiler = LaTeXCompiler()
    success = compiler.compile_article(args.article_directory)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
