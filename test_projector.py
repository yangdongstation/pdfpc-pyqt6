#!/usr/bin/env python3
"""
Test the projector window functionality
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

def test_projector():
    """Test the projector window functionality"""
    logger.info("="*60)
    logger.info("Testing Projector Window Functionality")
    logger.info("="*60)

    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Create main window
    window = MainWindow()
    window.show()
    logger.info("Main window created and shown")

    # Find test PDF
    pdf_path = Path.home() / "失声与回响：新传播生态下广播媒体融合转型的现状深描与困境解构.pdf"
    if not pdf_path.exists():
        logger.error(f"Test PDF not found: {pdf_path}")
        return False

    logger.info(f"Loading PDF: {pdf_path.name}")
    window._load_pdf(str(pdf_path))

    # Wait for rendering
    logger.info("Waiting for PDF rendering...")
    for i in range(30):
        app.processEvents()
        time.sleep(0.2)

    # Check that pages are rendered
    cache_dir = Path.home() / ".cache" / "pdfpc-pyqt6" / "page_cache"
    if not cache_dir.exists():
        logger.error("Cache directory not created")
        return False

    png_files = list(cache_dir.glob("*.png"))
    logger.info(f"✓ Found {len(png_files)} rendered pages")

    # Now test projector window
    logger.info("\nOpening projector window...")
    window.open_projector()

    # Process events to let projector initialize
    logger.info("Initializing projector display...")
    for i in range(10):
        app.processEvents()
        time.sleep(0.1)

    # Check if projector is open
    if window.state.is_projector_open():
        logger.info("✓ Projector window opened successfully")
        projector = window.state.get_projector_window()

        # Check if projector is displaying an image
        if projector.page_display.get_image_path():
            logger.info("✓ Projector displaying current page image")
            image_path = projector.page_display.get_image_path()
            logger.info(f"  Image: {Path(image_path).name}")
            return True
        else:
            logger.error("✗ Projector not displaying any image")
            return False
    else:
        logger.error("✗ Projector window failed to open")
        return False

if __name__ == "__main__":
    try:
        success = test_projector()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        sys.exit(1)
