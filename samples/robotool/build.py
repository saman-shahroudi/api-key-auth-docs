#!/usr/bin/env python3
"""
Fedshi Integration Tool - Build Script
=====================================

This script builds a standalone executable for the Fedshi Integration Tool
using PyInstaller. It packages all necessary files and creates a distribution
package for easy deployment.

Usage:
    python3 build.py

Requirements:
    - Python 3.6+
    - PyInstaller (will be installed automatically if missing)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("🔨 Fedshi Integration Tool - Build Script")
    print("=" * 60)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for path in ['build', 'dist', '*.spec']:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyInstaller: {e}")
            sys.exit(1)
    
    # Build executable
    print("🔨 Building executable...")
    try:
        subprocess.check_call([
            "pyinstaller", "--onefile", "--console", "server.py"
        ])
        print("✅ Executable built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)
    
    # Create distribution package
    print("📦 Creating distribution package...")
    dist_dir = Path("dist")
    package_dir = dist_dir / "FedshiIntegrationTool"
    
    # Create package directory
    dist_dir.mkdir(exist_ok=True)
    package_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_path = dist_dir / "server"
    if exe_path.exists():
        if os.name == 'nt':  # Windows
            shutil.copy2(exe_path, package_dir / "FedshiIntegrationTool.exe")
        else:  # Linux/Mac
            shutil.copy2(exe_path, package_dir / "FedshiIntegrationTool")
        print("✅ Copied executable to package")
    else:
        print("❌ Executable not found after build")
        sys.exit(1)
    
    # Copy static files
    files_to_copy = ["index.html", "app.js", "styles.css", "config.json", "README.md"]
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, package_dir)
            print(f"✅ Copied {file_name}")
    
    # Copy lib directory
    if Path("lib").exists():
        shutil.copytree("lib", package_dir / "lib", dirs_exist_ok=True)
        print("✅ Copied lib directory")
    
    # Create Windows launcher script
    windows_launcher_content = '''@echo off
echo ========================================
echo Fedshi Integration Tool
echo ========================================
echo.
echo Starting the server...
echo.
FedshiIntegrationTool.exe
echo.
echo Press any key to exit...
pause > nul
'''
    windows_launcher_file = package_dir / "run.bat"
    with open(windows_launcher_file, 'w') as f:
        f.write(windows_launcher_content)
    print("✅ Created Windows launcher script (run.bat)")
    
    # Create Linux/Mac launcher script
    linux_launcher_content = '''#!/bin/bash
echo "========================================"
echo "Fedshi Integration Tool"
echo "========================================"
echo
echo "Starting the server..."
echo
./FedshiIntegrationTool
echo
echo "Press Enter to exit..."
read
'''
    linux_launcher_file = package_dir / "run.sh"
    with open(linux_launcher_file, 'w') as f:
        f.write(linux_launcher_content)
    os.chmod(linux_launcher_file, 0o755)
    print("✅ Created Linux/Mac launcher script (run.sh)")
    
    # Create ZIP archive
    shutil.make_archive("FedshiIntegrationTool", 'zip', package_dir)
    print("✅ Created FedshiIntegrationTool.zip")
    
    print("=" * 60)
    print("🎉 Build completed successfully!")
    print("=" * 60)
    print(f"📁 Package location: {package_dir}")
    print(f"📦 Distribution file: FedshiIntegrationTool.zip")
    print("=" * 60)
    print("📋 For clients:")
    print("   1. Send FedshiIntegrationTool.zip to clients")
    print("   2. Clients extract the ZIP file")
    print("   3. Clients run run.bat (Windows) or ./run.sh (Linux/Mac)")
    print("   4. Tool opens in browser at http://localhost:8080")
    print("=" * 60)

if __name__ == "__main__":
    main() 