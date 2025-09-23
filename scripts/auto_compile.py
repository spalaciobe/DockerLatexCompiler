#!/usr/bin/env python3
"""
Cross-platform LaTeX compilation script
Automatically detects and compiles LaTeX projects using Docker

Usage: python auto_compile.py [tex_file_path]
Examples:
  python auto_compile.py                                    # Search .tex in current directory
  python auto_compile.py /path/to/file.tex                # Detect folder from file
  python auto_compile.py ws_latex/master-thesis/main.tex  # Detect folder from file
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
import platform

class CrossPlatformLaTeXCompiler:
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
    
    def show_help(self):
        """Display help information"""
        print("Usage: python auto_compile.py [tex_file_path]")
        print("")
        print("If no path provided, searches for .tex files in current directory")
        print("If path provided, automatically detects project folder")
        print("")
        print("Examples:")
        print("  python auto_compile.py                                    # Search .tex in current directory")
        print("  python auto_compile.py /path/to/file.tex                # Detect folder from file")
        print("  python auto_compile.py ws_latex/master-thesis/main.tex  # Detect folder from file")

    def find_tex_files(self, search_dir):
        """Find .tex files in the specified directory"""
        search_path = Path(search_dir)
        return list(search_path.glob("*.tex"))

    def select_tex_file(self, tex_files):
        """Select tex file when multiple are found"""
        if len(tex_files) == 1:
            return tex_files[0]
            
        print(f"[INFO] Found {len(tex_files)} .tex files:")
        print("")
        
        for i, file in enumerate(tex_files, 1):
            print(f"  {i}) {file.name}")
            
        print("")
        
        while True:
            try:
                choice = input(f"Select file to compile (1-{len(tex_files)}): ")
                selection = int(choice)
                if 1 <= selection <= len(tex_files):
                    return tex_files[selection - 1]
                else:
                    print(f"[ERROR] Invalid selection. Please choose 1-{len(tex_files)}")
            except (ValueError, KeyboardInterrupt):
                print("[ERROR] Invalid selection. Using first file by default.")
                return tex_files[0]

    def detect_project_folder(self, tex_file):
        """Detect the project folder from tex file path"""
        tex_path = Path(tex_file).resolve()
        
        # Find ws_latex in the path
        path_parts = tex_path.parts
        try:
            ws_latex_index = path_parts.index("ws_latex")
            if ws_latex_index + 1 < len(path_parts):
                return path_parts[ws_latex_index + 1]
        except ValueError:
            pass
            
        return None

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

    def compile_project(self, project_folder, tex_file=None):
        """Compile the LaTeX project using Docker"""
        print(f"[INFO] Detected project: {project_folder}")
        
        # Verify project folder exists
        project_path = self.project_root / "ws_latex" / project_folder
        if not project_path.exists():
            print(f"[ERROR] Directory 'ws_latex/{project_folder}' does not exist")
            print("   Available projects:")
            ws_latex_path = self.project_root / "ws_latex"
            if ws_latex_path.exists():
                for item in ws_latex_path.iterdir():
                    if item.is_dir():
                        print(f"   - {item.name}")
            return False
            
        print(f"[COMPILE] LaTeX in ws_latex/{project_folder}/")
        
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
        cmd.append(project_folder)
        
        # Add specific tex file if provided
        if tex_file:
            tex_filename = Path(tex_file).name
            print(f"[FILE] Compiling specific file: {tex_filename}")
            cmd.append(tex_filename)
            
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
    parser = argparse.ArgumentParser(description="Cross-platform LaTeX compiler using Docker")
    parser.add_argument("tex_file", nargs="?", help="Path to .tex file (optional)")
    parser.add_argument("--help-detailed", action="store_true", help="Show detailed help")
    
    args = parser.parse_args()
    
    compiler = CrossPlatformLaTeXCompiler()
    
    if args.help_detailed:
        compiler.show_help()
        return
        
    # If tex file is provided as argument
    if args.tex_file:
        tex_file_path = Path(args.tex_file)
        
        # Convert to absolute path if relative
        if not tex_file_path.is_absolute():
            tex_file_path = Path.cwd() / tex_file_path
            
        # Verify file exists
        if not tex_file_path.exists():
            print(f"[ERROR] File '{tex_file_path}' does not exist")
            sys.exit(1)
            
        # Verify it's within ws_latex
        if "ws_latex" not in str(tex_file_path):
            print("[ERROR] File must be within the ws_latex directory")
            print(f"   Current file: {tex_file_path}")
            sys.exit(1)
            
        # Detect project folder
        project_folder = compiler.detect_project_folder(tex_file_path)
        
        if not project_folder:
            print("[ERROR] Could not detect project folder")
            sys.exit(1)
            
        success = compiler.compile_project(project_folder, tex_file_path)
        
    else:
        # Search for tex files in current directory
        current_dir = Path.cwd()
        tex_files = compiler.find_tex_files(current_dir)
        
        if not tex_files:
            print(f"[ERROR] No .tex files found in current directory: {current_dir}")
            print("")
            print("Usage: python auto_compile.py <tex_file_path>")
            print("Or run from a directory containing .tex files")
            sys.exit(1)
            
        # Select tex file if multiple found
        selected_tex = compiler.select_tex_file(tex_files)
        print(f"[FILE] Using file: {selected_tex.name}")
        
        # Detect project folder
        project_folder = compiler.detect_project_folder(selected_tex)
        
        if not project_folder:
            print("[ERROR] Could not detect project folder")
            sys.exit(1)
            
        success = compiler.compile_project(project_folder, selected_tex)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
