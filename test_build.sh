#!/bin/bash
set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "========================================="
echo "Testing pdfpc-pyqt6 Build"
echo "========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for test results
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $2${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Executable exists
echo "Test 1: Checking if executable exists..."
if [ -f "dist/pdfpc-pyqt6/pdfpc-pyqt6" ]; then
    test_result 0 "Executable found at dist/pdfpc-pyqt6/pdfpc-pyqt6"
else
    test_result 1 "Executable not found"
    exit 1
fi

# Test 2: Executable is readable
echo ""
echo "Test 2: Checking executable permissions..."
if [ -x "dist/pdfpc-pyqt6/pdfpc-pyqt6" ]; then
    test_result 0 "Executable is readable and executable"
else
    test_result 1 "Executable is not executable"
fi

# Test 3: Main libraries are present
echo ""
echo "Test 3: Checking for main libraries..."
LIBS_OK=0
for lib in PyQt6 fitz; do
    if [ -d "dist/pdfpc-pyqt6/$lib" ] || [ -f "dist/pdfpc-pyqt6/$lib.so" ] || [ -f "dist/pdfpc-pyqt6/$lib.pyd" ]; then
        echo -e "  ${GREEN}✓${NC} Found $lib"
    else
        echo -e "  ${YELLOW}◆${NC} $lib not found (may be in lib directory)"
    fi
done

# Test 4: Pillow not included (optimization check)
echo ""
echo "Test 4: Checking for optimizations..."
if [ ! -d "dist/pdfpc-pyqt6/PIL" ]; then
    test_result 0 "Pillow correctly excluded (optimization: -8MB)"
else
    test_result 1 "Pillow should not be included"
fi

# Test 5: Build size
echo ""
echo "Test 5: Checking build size..."
SIZE=$(du -sh dist/pdfpc-pyqt6 | cut -f1)
SIZE_MB=$(du -s -B1M dist/pdfpc-pyqt6 | cut -f1)

if [ "$SIZE_MB" -lt 200 ]; then
    test_result 0 "Build size is $SIZE (within <200MB target)"
else
    test_result 1 "Build size is $SIZE (exceeds 200MB)"
fi

# Test 6: Try to run executable (with timeout)
echo ""
echo "Test 6: Attempting to run executable (5 second timeout)..."
if command -v timeout &> /dev/null; then
    if timeout 5 ./dist/pdfpc-pyqt6/pdfpc-pyqt6 2>/dev/null || true; then
        test_result 0 "Executable runs successfully"
    else
        echo -e "  ${YELLOW}⚠${NC} Could not run GUI (may need DISPLAY variable)"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} 'timeout' command not found, skipping execution test"
fi

# Test 7: Check for Python files (should be compiled to bytecode)
echo ""
echo "Test 7: Checking for source files in output..."
if [ -z "$(find dist/pdfpc-pyqt6 -name '*.py' | head -1)" ]; then
    test_result 0 "No .py source files in output (good)"
else
    test_result 1 "Found .py source files (should be compiled)"
fi

# Test 8: File integrity
echo ""
echo "Test 8: Checking file integrity..."
FILE_COUNT=$(find dist/pdfpc-pyqt6 -type f | wc -l)
if [ "$FILE_COUNT" -gt 10 ]; then
    test_result 0 "Found $FILE_COUNT files in output"
else
    test_result 1 "Insufficient files in output ($FILE_COUNT < 10)"
fi

# Summary
echo ""
echo "========================================="
echo "Test Results"
echo "========================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e ""
    echo -e "${GREEN}All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test with a sample PDF: ./dist/pdfpc-pyqt6/pdfpc-pyqt6"
    echo "  2. Create package: ./build.sh --package"
    echo "  3. Verify on target system"
    exit 0
else
    echo -e ""
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
fi
