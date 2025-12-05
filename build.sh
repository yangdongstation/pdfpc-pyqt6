#!/bin/bash
set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "========================================="
echo "PDF Presenter Console - Build Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check if PyInstaller is installed
echo "Step 1: Checking dependencies..."
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing PyInstaller...${NC}"
    pip install pyinstaller==6.1.0 -q
fi
echo -e "${GREEN}✓ PyInstaller ready${NC}"

# 2. Clean previous builds
echo ""
echo "Step 2: Cleaning previous builds..."
rm -rf build dist *.spec __pycache__
echo -e "${GREEN}✓ Clean complete${NC}"

# 3. Build with PyInstaller
echo ""
echo "Step 3: Building with PyInstaller (this may take 30-60 seconds)..."
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
    --exclude-module=PyQt6.QtWebEngineWidgets \
    --exclude-module=PyQt6.QtPrintSupport \
    --strip \
    pdfpc_pyqt6/main.py > /dev/null 2>&1

if [ -f "dist/pdfpc-pyqt6/pdfpc-pyqt6" ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# 4. Output information
echo ""
echo "========================================="
echo "Build Complete!"
echo "========================================="

SIZE=$(du -sh dist/pdfpc-pyqt6 | cut -f1)
echo -e "Output directory: ${GREEN}dist/pdfpc-pyqt6${NC}"
echo -e "Size: ${GREEN}$SIZE${NC}"
echo ""
echo "To run the application:"
echo "  ./dist/pdfpc-pyqt6/pdfpc-pyqt6"
echo ""
echo "To create a distribution package:"
echo "  ./build.sh --package"
echo ""

# 5. Optional: Package for distribution
if [ "$1" == "--package" ]; then
    echo "Step 4: Creating distribution package..."

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="linux-x86_64"
        ARCHIVE="pdfpc-pyqt6-${PLATFORM}.tar.gz"
        cd dist
        tar -czf "../$ARCHIVE" pdfpc-pyqt6/
        cd ..
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos-$(uname -m)"
        ARCHIVE="pdfpc-pyqt6-${PLATFORM}.zip"
        cd dist
        zip -r "../$ARCHIVE" pdfpc-pyqt6/
        cd ..
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        PLATFORM="windows-x86_64"
        ARCHIVE="pdfpc-pyqt6-${PLATFORM}.zip"
        cd dist
        powershell -Command "Compress-Archive -Path pdfpc-pyqt6 -DestinationPath ../$ARCHIVE"
        cd ..
    fi

    ARCHIVE_SIZE=$(du -sh "$ARCHIVE" | cut -f1)
    echo -e "${GREEN}✓ Package created: $ARCHIVE ($ARCHIVE_SIZE)${NC}"
fi

echo ""
echo "Build and packaging complete!"
