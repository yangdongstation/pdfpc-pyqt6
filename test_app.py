#!/usr/bin/env python3
"""
Test the built application by simulating PDF loading
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

# Import Qt and app components
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from pdfpc_pyqt6.ui.main_window import MainWindow

def test_app():
    """Test the application with a PDF file"""
    logger.info("="*60)
    logger.info("Testing PDF Presenter Console Application")
    logger.info("="*60)

    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Create main window
    window = MainWindow()
    window.show()
    logger.info("Main window created and shown")

    # Find a test PDF
    pdf_path = Path.home() / "失声与回响：新传播生态下广播媒体融合转型的现状深描与困境解构.pdf"
    if not pdf_path.exists():
        logger.error(f"Test PDF not found: {pdf_path}")
        return False

    logger.info(f"Found test PDF: {pdf_path.name}")

    # Load PDF programmatically
    logger.info("Loading PDF...")
    window._load_pdf(str(pdf_path))

    # Process events to let rendering start
    logger.info("Processing Qt events to start rendering...")
    for i in range(50):  # Process events multiple times
        app.processEvents()
        time.sleep(0.1)

    # Check cache directory
    cache_dir = Path.home() / ".cache" / "pdfpc-pyqt6" / "page_cache"
    logger.info(f"Checking cache directory: {cache_dir}")

    if cache_dir.exists():
        png_files = list(cache_dir.glob("*.png"))
        logger.info(f"Found {len(png_files)} PNG files")
        for f in sorted(png_files)[:3]:  # Show first 3
            size_kb = f.stat().st_size / 1024
            logger.info(f"  ✓ {f.name} ({size_kb:.1f} KB)")

        if len(png_files) > 0:
            logger.info("✅ SUCCESS: PDF pages are being rendered!")
            return True
        else:
            logger.error("❌ FAILED: No PNG files found in cache")
            return False
    else:
        logger.error(f"❌ Cache directory does not exist: {cache_dir}")
        return False

if __name__ == "__main__":
    try:
        success = test_app()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        sys.exit(1)
