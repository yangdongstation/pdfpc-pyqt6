#!/usr/bin/env python3
"""
Test script to debug PDF rendering with verbose logging
"""

import sys
import logging
from pathlib import Path

# Configure logging BEFORE importing Qt
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/pdfpc_test.log')
    ]
)

logger = logging.getLogger(__name__)

# Now import Qt and other modules
from PyQt6.QtWidgets import QApplication
from pdfpc_pyqt6.core.state_manager import AppState
from pdfpc_pyqt6.core.pdf_processor import PDFProcessor
from pdfpc_pyqt6.core.threading_manager import RenderThreadPool
from pdfpc_pyqt6.config import config

def test_rendering():
    """Test the rendering pipeline"""
    logger.info("="*60)
    logger.info("Starting PDF rendering test")
    logger.info("="*60)

    # Create Qt application (required for threading)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Create components
    state = AppState()
    pdf_processor = PDFProcessor()
    render_pool = RenderThreadPool(pdf_processor, state, max_threads=2)

    # Find a test PDF
    test_pdfs = list(Path.home().glob("*.pdf")) + list(Path("/tmp").glob("*.pdf"))
    if not test_pdfs:
        logger.error("No PDF files found in home directory or /tmp")
        return False

    pdf_path = str(test_pdfs[0])
    logger.info(f"Using PDF: {pdf_path}")

    # Load PDF
    logger.info("Loading PDF...")
    if not pdf_processor.load_pdf(pdf_path):
        logger.error("Failed to load PDF")
        return False

    page_count = pdf_processor.get_page_count()
    logger.info(f"PDF loaded with {page_count} pages")

    # Set state
    state.set_total_pages(page_count)
    logger.info(f"State total_pages set to {page_count}")

    # Trigger rendering
    logger.info("Calling render_priority_pages(0)")
    render_pool.render_priority_pages(0)

    # Wait for rendering to complete - need to run event loop for threads to work
    logger.info("Running event loop to process worker threads...")
    import time
    from PyQt6.QtCore import QTimer

    # Process events in a loop until rendering completes
    max_wait_time = 10  # seconds
    start_time = time.time()
    last_count = -1

    while time.time() - start_time < max_wait_time:
        app.processEvents()

        # Check cache periodically
        cache_dir = config.CACHE_DIR
        if cache_dir.exists():
            files = list(cache_dir.glob("*.png"))
            if len(files) != last_count:
                logger.info(f"Rendered {len(files)} pages so far")
                last_count = len(files)

            # If we've rendered all pages, we can stop waiting
            if len(files) >= 8:
                logger.info("All pages rendered!")
                break

        time.sleep(0.1)

    # Final check
    cache_dir = config.CACHE_DIR
    logger.info(f"Checking final results in cache directory: {cache_dir}")

    if cache_dir.exists():
        files = list(cache_dir.glob("*.png"))
        logger.info(f"Found {len(files)} PNG files in cache")
        for f in sorted(files):
            logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")
    else:
        logger.error(f"Cache directory does not exist: {cache_dir}")

    logger.info("="*60)
    logger.info("Test complete")
    logger.info("="*60)

    return True

if __name__ == "__main__":
    success = test_rendering()
    sys.exit(0 if success else 1)
