"""
PDF processing module using PyMuPDF for rendering
"""

import io
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal as pyqtSignal

from ..config import config

logger = logging.getLogger(__name__)


class PDFProcessor(QObject):
    """
    Handles PDF loading and page rendering to images
    """

    # Signals
    renderProgress = pyqtSignal(int, int)  # (current_page, total_pages)
    renderComplete = pyqtSignal(int, str)  # (page_idx, image_path)
    renderError = pyqtSignal(str)  # error message

    def __init__(self):
        super().__init__()
        self._pdf_document = None
        self._page_count = 0
        self._pdf_path: Optional[str] = None
        self._cache_dir = config.CACHE_DIR
        self._scale = config.DEFAULT_SCALE

    def load_pdf(self, pdf_path: str) -> bool:
        """
        Load a PDF file.
        Returns True if successful, False otherwise.
        """
        try:
            try:
                import fitz  # PyMuPDF
            except ModuleNotFoundError:
                import fitz_old as fitz

            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            # Close previous document if any
            if self._pdf_document:
                self._pdf_document.close()

            # Load new document
            self._pdf_document = fitz.open(str(pdf_path))
            self._page_count = self._pdf_document.page_count
            self._pdf_path = str(pdf_path)

            logger.info(f"Loaded PDF: {pdf_path} with {self._page_count} pages")
            return True

        except ImportError:
            logger.error(
                "PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF"
            )
            self.renderError.emit("PyMuPDF not available. Install: pip install PyMuPDF")
            return False
        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            self.renderError.emit(f"Failed to load PDF: {e}")
            return False

    def get_page_count(self) -> int:
        """Get the number of pages in the loaded PDF"""
        return self._page_count

    def render_page(
        self, page_index: int, scale: Optional[float] = None
    ) -> Optional[str]:
        """
        Render a single page to PNG image.
        Returns the path to the cached PNG file, or None if rendering failed.
        """
        logger.debug(f"render_page called with page_index={page_index}, scale={scale}")

        if not self._pdf_document:
            logger.error("No PDF document loaded")
            return None

        if page_index < 0 or page_index >= self._page_count:
            logger.error(
                f"Invalid page index: {page_index} (page_count={self._page_count})"
            )
            return None

        try:
            try:
                import fitz  # PyMuPDF
            except ModuleNotFoundError:
                import fitz_old as fitz

            # Use provided scale or default
            if scale is None:
                scale = self._scale

            logger.debug(f"Using scale: {scale}")

            # Generate cache filename
            cache_filename = f"page_{page_index:06d}_{scale}.png"
            cache_path = self._cache_dir / cache_filename

            logger.debug(f"Cache path: {cache_path}")
            logger.debug(f"Cache dir exists: {self._cache_dir.exists()}")

            # Return cached file if it exists
            if cache_path.exists():
                logger.debug(f"Using cached page: {cache_path}")
                return str(cache_path)

            # Render page
            logger.debug(f"Rendering page {page_index} from document")
            page = self._pdf_document[page_index]
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            logger.debug(f"Pixmap created: {pix}")

            # Save to cache
            logger.debug(f"Creating cache directory: {cache_path.parent}")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Saving to: {cache_path}")
            pix.save(str(cache_path))
            logger.debug(f"File saved successfully")

            # Verify file exists
            if cache_path.exists():
                file_size = cache_path.stat().st_size
                logger.info(
                    f"Rendered page {page_index} to {cache_path} ({file_size} bytes)"
                )
                return str(cache_path)
            else:
                logger.error(f"File not created after save: {cache_path}")
                return None

        except Exception as e:
            logger.error(f"Failed to render page {page_index}: {e}", exc_info=True)
            self.renderError.emit(f"Failed to render page {page_index}: {e}")
            return None

    def render_page_to_bytes(
        self, page_index: int, scale: Optional[float] = None
    ) -> Optional[bytes]:
        """
        Render a page directly to PNG bytes without saving to disk.
        Useful for immediate display without caching.
        """
        if not self._pdf_document:
            logger.error("No PDF document loaded")
            return None

        if page_index < 0 or page_index >= self._page_count:
            logger.error(f"Invalid page index: {page_index}")
            return None

        try:
            try:
                import fitz  # PyMuPDF
            except ModuleNotFoundError:
                import fitz_old as fitz

            if scale is None:
                scale = self._scale

            page = self._pdf_document[page_index]
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Return PNG bytes
            return pix.tobytes(output="png")

        except Exception as e:
            logger.error(f"Failed to render page {page_index} to bytes: {e}")
            return None

    def get_pdf_path(self) -> Optional[str]:
        """Get the currently loaded PDF path"""
        return self._pdf_path

    def set_render_scale(self, scale: float) -> None:
        """Set the rendering scale factor"""
        self._scale = max(0.5, min(4.0, scale))  # Clamp between 0.5 and 4.0

    def clear_cache(self) -> None:
        """Clear the image cache"""
        try:
            import shutil

            if self._cache_dir.exists():
                shutil.rmtree(self._cache_dir)
                self._cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    def close(self) -> None:
        """Close the PDF document"""
        if self._pdf_document:
            self._pdf_document.close()
            self._pdf_document = None
            self._page_count = 0
            logger.info("PDF closed")
