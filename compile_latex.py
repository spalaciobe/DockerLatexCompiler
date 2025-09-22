#!/usr/bin/env python3
"""
LaTeX document compilation automator
Usage: python compile_latex.py [directory]
Example: python compile_latex.py class01
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time

class LaTeXCompiler:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        
    def find_main_tex(self, target_dir, specific_file=None):
        """Searches for main.tex file in the specified directory, or uses specific file if provided"""
        if specific_file:
            # Use the specific file if provided
            tex_path = self.base_dir / target_dir / specific_file
            if tex_path.exists():
                return tex_path
            else:
                print(f"❌ Error: Specified file '{specific_file}' not found in '{target_dir}'")
                return None
        
        # Original behavior: look for main.tex first
        tex_path = self.base_dir / target_dir / "main.tex"
        if tex_path.exists():
            return tex_path
        
        # If main.tex is not found, search for any .tex file
        tex_files = list((self.base_dir / target_dir).glob("*.tex"))
        if tex_files:
            print(f"⚠️  main.tex not found, using {tex_files[0].name}")
            return tex_files[0]
        
        return None
    
    def clean_aux_files(self, tex_file):
        """Cleans auxiliary files from previous compilations"""
        base_name = tex_file.stem
        aux_extensions = ['.aux', '.log', '.out', '.toc', '.fdb_latexmk', '.fls', '.synctex.gz', '.bbl', '.blg', '.nav', '.snm', '.vrb']
        
        for ext in aux_extensions:
            aux_file = tex_file.parent / f"{base_name}{ext}"
            if aux_file.exists():
                aux_file.unlink()
                print(f"🧹 Deleted: {aux_file.name}")
    
    def compile_latex(self, tex_file, clean_first=True, clean_after=True):
        """Compiles the LaTeX file with bibliography support"""
        if clean_first:
            self.clean_aux_files(tex_file)
        
        print(f"📄 Compiling: {tex_file}")
        
        # Change to the file directory
        original_dir = Path.cwd()
        os.chdir(tex_file.parent)
        
        try:
            base_name = tex_file.stem
            
            # First pdflatex pass
            print("🔄 First pass: pdflatex")
            result1 = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_file.name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result1.returncode != 0:
                print(f"❌ Error in first pdflatex pass")
                self._show_latex_errors(result1)
                return False
            
            # Check if there's a .bib file and run bibtex if necessary
            bib_files = list(tex_file.parent.glob("*.bib"))
            if bib_files:
                print("📚 Processing bibliography: bibtex")
                result_bib = subprocess.run(
                    ['bibtex', base_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result_bib.returncode != 0:
                    print("⚠️  Warning in bibtex (may be normal if there are no citations)")
                    # Don't return False here, bibtex may fail if there are no citations
                
                # Second pdflatex pass (to resolve references)
                print("🔄 Second pass: pdflatex")
                result2 = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file.name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result2.returncode != 0:
                    print(f"❌ Error in second pdflatex pass")
                    self._show_latex_errors(result2)
                    return False
                
                # Third pdflatex pass (to finalize cross-references)
                print("🔄 Third pass: pdflatex")
                result3 = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file.name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                final_result = result3
            else:
                # If there are no .bib files, use the first pass result
                final_result = result1
            
            # Check if PDF was generated
            pdf_file = tex_file.with_suffix('.pdf')
            
            if final_result.returncode == 0 and pdf_file.exists():
                print(f"✅ Compilation successful: {pdf_file}")
                print(f"📊 PDF size: {pdf_file.stat().st_size:,} bytes")
                
                # Show warnings if any
                if "Overfull" in final_result.stdout or "Underfull" in final_result.stdout:
                    print("⚠️  Some formatting warnings found (non-critical)")
                
                # Clean auxiliary files after successful compilation
                if clean_after:
                    self.clean_aux_files(tex_file)
                
                return True
            else:
                print(f"❌ Error in final compilation:")
                self._show_latex_errors(final_result)
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout: Compilation took more than 60 seconds")
            return False
        except FileNotFoundError:
            print("❌ Error: pdflatex is not installed or not in PATH")
            return False
        finally:
            os.chdir(original_dir)
    
    def _show_latex_errors(self, result):
        """Shows LaTeX errors in a readable format"""
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            # Show only lines with errors
            error_lines = [line for line in result.stdout.split('\n') 
                         if '!' in line or 'Error' in line or 'Undefined' in line]
            for line in error_lines[:5]:  # Show maximum 5 errors
                print(f"  {line}")
    
    def watch_and_compile(self, tex_file, clean_after=True):
        """Watch mode: automatically recompiles when file changes"""
        print(f"👀 Watch mode activated for {tex_file}")
        print("Press Ctrl+C to exit")
        
        last_modified = tex_file.stat().st_mtime
        
        try:
            while True:
                current_modified = tex_file.stat().st_mtime
                if current_modified > last_modified:
                    print(f"\n🔄 File modified, recompiling...")
                    self.compile_latex(tex_file, clean_first=False, clean_after=clean_after)
                    last_modified = current_modified
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Watch mode terminated")

def main():
    parser = argparse.ArgumentParser(description='Automatic LaTeX compiler')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory containing the LaTeX file (default: current directory)')
    parser.add_argument('specific_file', nargs='?', default=None,
                       help='Specific .tex file to compile (optional)')
    parser.add_argument('--clean', '-c', action='store_true',
                       help='Clean auxiliary files before compiling')
    parser.add_argument('--no-clean-after', action='store_true',
                       help='Do not clean auxiliary files after compiling (default is to clean them)')
    parser.add_argument('--watch', '-w', action='store_true',
                       help='Watch mode: automatically recompile when file changes')
    
    args = parser.parse_args()
    
    compiler = LaTeXCompiler()
    
    # Search for LaTeX file
    tex_file = compiler.find_main_tex(args.directory, args.specific_file)
    
    if not tex_file:
        if args.specific_file:
            print(f"❌ Specified file '{args.specific_file}' not found in '{args.directory}'")
        else:
            print(f"❌ No .tex file found in '{args.directory}'")
        sys.exit(1)
    
    if args.watch:
        # Compile once first
        compiler.compile_latex(tex_file, clean_first=args.clean, clean_after=not args.no_clean_after)
        # Then enter watch mode
        compiler.watch_and_compile(tex_file, clean_after=not args.no_clean_after)
    else:
        # Single compilation
        success = compiler.compile_latex(tex_file, clean_first=args.clean, clean_after=not args.no_clean_after)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
