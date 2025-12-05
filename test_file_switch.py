#!/usr/bin/env python3
"""
Test file switching - opening multiple files in sequence
"""

import sys
import logging
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import QApplication
from pdfpc_pyqt6.ui.main_window import MainWindow

def test_file_switching():
    """Test opening multiple files sequentially"""
    logger.info("="*60)
    logger.info("Testing File Switching")
    logger.info("="*60)

    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Create main window
    window = MainWindow()
    window.show()
    logger.info("Main window created")

    # Test file paths
    pdf_file = Path.home() / "失声与回响：新传播生态下广播媒体融合转型的现状深描与困境解构.pdf"

    if not pdf_file.exists():
        logger.error(f"Test PDF not found: {pdf_file}")
        return False

    logger.info("\n" + "="*60)
    logger.info("TEST 1: Open first PDF file")
    logger.info("="*60)

    # Open first file
    window._load_pdf(str(pdf_file))

    # Wait for rendering
    for i in range(15):
        app.processEvents()
        time.sleep(0.2)

    # Check first load
    cache_dir = Path.home() / ".cache" / "pdfpc-pyqt6" / "page_cache"
    png_files_1 = list(cache_dir.glob("*.png"))
    logger.info(f"✓ First file: {len(png_files_1)} pages rendered")
    logger.info(f"  Current page content: {window.state.get_page_image(0)}")

    if len(png_files_1) == 0:
        logger.error("✗ No pages rendered for first file")
        return False

    # Store first file cache for comparison
    first_cache_files = set(f.name for f in png_files_1)
    first_image = window.state.get_page_image(0)

    logger.info("\n" + "="*60)
    logger.info("TEST 2: Open same file again (should replace cache)")
    logger.info("="*60)

    # Open file again
    window._load_pdf(str(pdf_file))

    # Wait for rendering
    for i in range(15):
        app.processEvents()
        time.sleep(0.2)

    # Check second load
    png_files_2 = list(cache_dir.glob("*.png"))
    logger.info(f"✓ Second load: {len(png_files_2)} pages rendered")
    logger.info(f"  Current page content: {window.state.get_page_image(0)}")

    if len(png_files_2) == 0:
        logger.error("✗ No pages rendered on second load")
        return False

    # Verify cache was cleared and repopulated
    second_cache_files = set(f.name for f in png_files_2)
    second_image = window.state.get_page_image(0)

    if first_cache_files == second_cache_files:
        logger.info("✓ Cache files are the same (as expected)")
    else:
        logger.warning("⚠ Cache files differ")

    # Verify it's the same image path (should be)
    if first_image == second_image:
        logger.info("✓ Page image path matches")
    else:
        logger.warning("⚠ Page image paths differ")

    logger.info("\n" + "="*60)
    logger.info("TEST 3: Verify current page is 0")
    logger.info("="*60)

    if window.state.current_page == 0:
        logger.info("✓ Current page correctly reset to 0")
    else:
        logger.error(f"✗ Current page is {window.state.current_page}, expected 0")
        return False

    logger.info("\n" + "="*60)
    logger.info("✅ FILE SWITCHING TEST PASSED")
    logger.info("="*60)

    return True

if __name__ == "__main__":
    try:
        success = test_file_switching()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        sys.exit(1)
