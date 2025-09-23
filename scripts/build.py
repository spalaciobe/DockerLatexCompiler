#!/usr/bin/env python3
"""
Cross-platform Docker build script
Builds the LaTeX Docker image

Usage: python build.py
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
import platform

class DockerBuilder:
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

    def build_image(self):
        """Build the Docker image"""
        print(f"[BUILD] Building Docker image: {self.config['docker_image_name']}")
        
        # Build Docker command
        cmd = ["docker", "build"]
        
        # Add network configuration for build (Linux only)
        if not self.is_windows:
            cmd.extend(["--network=host"])
            
        cmd.extend(["-t", self.config["docker_image_name"], str(self.project_root)])
        
        try:
            print(f"[DOCKER] Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True)
            print("[SUCCESS] Docker image built successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Docker build failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            print("[ERROR] Docker is not installed or not in PATH")
            print("   Please install Docker Desktop and make sure it's running")
            return False

def main():
    parser = argparse.ArgumentParser(description="Build LaTeX Docker image")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    builder = DockerBuilder()
    success = builder.build_image()
    
    if success:
        print(f"[SUCCESS] Image '{builder.config['docker_image_name']}' is ready to use!")
        print("   You can now compile LaTeX documents using:")
        print("   python scripts/compile.py <directory>")
        print("   or")
        print("   python scripts/auto_compile.py <file.tex>")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
