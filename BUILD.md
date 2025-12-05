# Build Instructions for PDF Presenter Console (PyQt6)

## Overview

This document explains how to compile the PDF Presenter Console into a standalone executable using PyInstaller.

## Prerequisites

- **Python 3.8+** - Already installed
- **pip** - Python package manager
- **PyInstaller 6.0+** - Will be installed automatically
- **Git** (optional) - For version control
- **~500MB free disk space** - For build artifacts

## Quick Start (2 minutes)

```bash
cd /home/donz/pdfpc-pyqt6

# Make build script executable
chmod +x build.sh test_build.sh

# Run the build
./build.sh

# The executable will be at: dist/pdfpc-pyqt6/pdfpc-pyqt6
```

## Detailed Build Process

### Step 1: Prepare Environment

```bash
cd /home/donz/pdfpc-pyqt6

# Install PyInstaller
pip install pyinstaller==6.1.0

# Verify installation
pyinstaller --version
```

### Step 2: Build with PyInstaller

#### Automatic (Recommended)
```bash
./build.sh
```

#### Manual
```bash
pyinstaller \
    --name=pdfpc-pyqt6 \
    --onedir \
    --windowed \
    --hidden-import=fitz \
    --optimize=2 \
    --exclude-module=Pillow \
    --exclude-module=PyQt6.QtSql \
    --exclude-module=PyQt6.QtNetwork \
    --exclude-module=PyQt6.QtDBus \
    --exclude-module=PyQt6.QtMultimedia \
    --strip \
    pdfpc_pyqt6/main.py
```

### Step 3: Verify Build

```bash
# Run automated tests
./test_build.sh

# Or manually test
./dist/pdfpc-pyqt6/pdfpc-pyqt6
```

### Step 4: Create Distribution Package

```bash
# Automatic packaging
./build.sh --package

# Manual packaging (Linux)
cd dist
tar -czf ../pdfpc-pyqt6-linux-x86_64.tar.gz pdfpc-pyqt6/
cd ..
```

## Build Output

### Directory Structure
```
dist/pdfpc-pyqt6/
├── pdfpc-pyqt6          (Main executable)
├── PyQt6/               (GUI framework libraries)
├── fitz/                (PDF rendering library)
├── encodings/           (Python encoding files)
└── ... (other libraries)
```

### File Size Expectations

| Configuration | Size |
|---------------|------|
| Unoptimized PyInstaller | 140-150MB |
| With Pillow removed | 130-140MB |
| With module exclusions | 100-120MB |
| With UPX compression | 70-85MB |

## Platform-Specific Instructions

### Linux

**Build on Linux:**
```bash
./build.sh
```

**Distribution:**
```bash
./build.sh --package
# Creates: pdfpc-pyqt6-linux-x86_64.tar.gz

# Extract on target system
tar -xzf pdfpc-pyqt6-linux-x86_64.tar.gz
cd pdfpc-pyqt6
./pdfpc-pyqt6
```

**Dependencies on Target System:**
- Libraries: None (everything is bundled)
- Python: Not required
- GUI libraries: Bundled in the executable

### Windows

**Build on Windows (PowerShell):**
```powershell
./build.sh
```

Or manually:
```powershell
pyinstaller --onedir --windowed --hidden-import=fitz `
  --exclude-module=Pillow pdfpc_pyqt6/main.py
```

**Distribution:**
```powershell
# Create ZIP file
cd dist
Compress-Archive -Path pdfpc-pyqt6 -DestinationPath ../pdfpc-pyqt6-windows.zip
cd ..
```

**Running on Target:**
- Extract the ZIP file
- Double-click `pdfpc-pyqt6/pdfpc-pyqt6.exe`
- Or drag PDF files onto the executable

### macOS

**Build on macOS:**
```bash
./build.sh
```

**Distribution:**
```bash
./build.sh --package
# Creates: pdfpc-pyqt6-macos-x86_64.zip

# Extract and run
unzip pdfpc-pyqt6-macos-x86_64.zip
cd pdfpc-pyqt6
./pdfpc-pyqt6
```

**Note:** First run may trigger Gatekeeper security prompt. Right-click the executable and select "Open" to allow.

## Advanced Build Options

### Option 1: Smaller Output with UPX Compression

```bash
# Install UPX (optional compression tool)
sudo apt-get install upx  # Linux
brew install upx          # macOS
# Windows: Download from https://upx.github.io/

# Build with UPX enabled (already in .spec file)
pyinstaller pdfpc-pyqt6.spec
```

**Results:**
- Size reduction: 30-40%
- Startup: +1-2 seconds (decompression)
- Trade-off: Smaller file size vs. slightly slower startup

### Option 2: Custom Module Exclusions

Edit `pdfpc-pyqt6.spec` and modify the `excluded_modules` list to exclude more PyQt6 modules:

```python
excluded_modules = [
    'PyQt6.QtSql',
    'PyQt6.QtNetwork',
    'PyQt6.QtDBus',
    # Add more as needed
]
```

### Option 3: One-File Executable

For a single `.exe` file instead of a directory:

```bash
pyinstaller --onefile \
    --name=pdfpc-pyqt6 \
    --windowed \
    pdfpc_pyqt6/main.py
```

**Note:** Startup is slower (~5-10 seconds) due to extraction.

### Option 4: Add Custom Icon

```bash
# Create or use an existing icon file
# Icon must be in .ico format (Windows) or .png (Linux/macOS)

pyinstaller --onedir \
    --windowed \
    --icon=./icon.ico \
    pdfpc_pyqt6/main.py
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'fitz'"

**Solution:**
```bash
# Ensure PyMuPDF is installed in development environment
pip install PyMuPDF

# Add hidden import to build command
pyinstaller ... --hidden-import=fitz pdfpc_pyqt6/main.py
```

### Problem: "QXcbConnection: Could not connect to display" (Linux)

**Solution:**
```bash
# Test requires X11 or Wayland display
# If testing over SSH, set:
export DISPLAY=:0

# Or run in background
./dist/pdfpc-pyqt6/pdfpc-pyqt6 &
```

### Problem: Build size exceeds 200MB

**Solution:**

1. Verify Pillow is excluded:
```bash
# Check what's included
unzip -l dist/pdfpc-pyqt6.zip | grep -i pillow  # Should be empty
```

2. Check for unnecessary modules:
```bash
ls dist/pdfpc-pyqt6/
# Remove unused directories if present
rm -rf dist/pdfpc-pyqt6/some_unused_lib
```

3. Enable UPX compression:
```bash
# Install UPX first
upx --best dist/pdfpc-pyqt6/pdfpc-pyqt6
```

### Problem: Application crashes on startup

**Solution:**

1. Run from terminal to see error messages:
```bash
./dist/pdfpc-pyqt6/pdfpc-pyqt6 2>&1 | head -20
```

2. Check for missing dependencies:
```bash
ldd ./dist/pdfpc-pyqt6/pdfpc-pyqt6 | grep "not found"
```

3. Rebuild with verbose output:
```bash
pyinstaller --debug --console pdfpc_pyqt6/main.py
./dist/pdfpc-pyqt6/pdfpc-pyqt6
```

## Continuous Integration (CI/CD)

### GitHub Actions Example

```yaml
name: Build and Release

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build executable
        run: |
          pyinstaller pdfpc-pyqt6.spec

      - name: Test build
        run: |
          bash test_build.sh

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: pdfpc-pyqt6-${{ runner.os }}
          path: dist/pdfpc-pyqt6
```

## Performance Optimization

### Startup Time Optimization

**Current:** 2-4 seconds

**Improvements:**
1. Use `--onedir` mode (faster) instead of `--onefile` (slower)
2. Use SSD instead of HDD for better I/O
3. Profile with:
   ```bash
   time ./dist/pdfpc-pyqt6/pdfpc-pyqt6 &
   kill $!
   ```

### Binary Size Optimization

**Current:** 100-140MB

**Improvements:**
1. **Remove Pillow** (8MB) ✓ Already done
2. **Use UPX compression** (30-40% reduction)
3. **Remove platform-specific modules:**
   ```bash
   # Remove Windows DLLs on Linux build
   rm dist/pdfpc-pyqt6/PyQt6/plugins/platforms/qwindows.dll
   ```

## Testing the Build

### Functional Test Checklist

- [ ] Open PDF file (Ctrl+O)
- [ ] Navigate pages (← → Space)
- [ ] Switch views (O, P, Tab)
- [ ] Open projector (F)
- [ ] All keyboard shortcuts work
- [ ] Cache directory is created
- [ ] No crashes or error messages

### Test with Different PDFs

```bash
# Small PDF (test basic functionality)
./dist/pdfpc-pyqt6/pdfpc-pyqt6 sample_small.pdf &

# Large PDF (test performance)
./dist/pdfpc-pyqt6/pdfpc-pyqt6 sample_large.pdf &
```

## Distribution Checklist

Before releasing, verify:

- [ ] Build passes all tests (`./test_build.sh`)
- [ ] Tested on target platform
- [ ] File size within acceptable range (<200MB)
- [ ] No debug symbols in release build
- [ ] All keyboard shortcuts working
- [ ] Cache directory created correctly
- [ ] No Python installation required on target
- [ ] Readme and instructions included

## Version Management

### Update Build Version

Edit `pdfpc_pyqt6/__init__.py`:
```python
__version__ = "0.2.0"
```

### Tag Release

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push --tags
```

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [PyInstaller Hooks](https://github.com/pyinstaller/pyinstaller-hooks-contrib)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)

## Support

If you encounter build issues:

1. **Check this document** - Common solutions are listed above
2. **Check PyInstaller issues** - https://github.com/pyinstaller/pyinstaller/issues
3. **Check project issues** - GitHub project repository
4. **Enable debug mode** - Use `--debug=all` flag with PyInstaller

## License

Build scripts and configuration provided under MIT License, same as the main project.
