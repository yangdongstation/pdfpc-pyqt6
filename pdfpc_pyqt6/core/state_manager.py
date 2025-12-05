"""
Global application state management using Qt signals
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty
from typing import Dict, Optional


class AppState(QObject):
    """
    Central state management for the PDF presenter application.
    All UI components subscribe to signals to stay synchronized.
    """

    # Signals for state changes
    currentPageChanged = pyqtSignal(int)  # Emitted when current page changes
    totalPagesChanged = pyqtSignal(int)  # Emitted when PDF page count is set
    viewModeChanged = pyqtSignal(str)    # Emitted when view mode switches
    pageImagesUpdated = pyqtSignal(int, str)  # (page_idx, image_path)
    projectorStatusChanged = pyqtSignal(bool)  # (is_open)
    pdfLoadingStarted = pyqtSignal()
    pdfLoadingFinished = pyqtSignal()
    pdfLoadingError = pyqtSignal(str)  # error message

    def __init__(self):
        super().__init__()
        self._current_page = 0
        self._total_pages = 0
        self._view_mode = "OVERVIEW"  # "OVERVIEW" or "PRESENTER"
        self._doc_images: Dict[int, str] = {}  # {page_idx: image_path}
        self._pdf_path: Optional[str] = None
        self._is_pdf_loaded = False
        self._projector_window = None
        self._is_projector_open = False

    # Properties and methods for current page
    @pyqtProperty(int, notify=currentPageChanged)
    def current_page(self) -> int:
        return self._current_page

    def set_current_page(self, page_idx: int) -> None:
        """Set the current page and emit signal if changed"""
        if page_idx != self._current_page:
            # Clamp to valid range
            page_idx = max(0, min(page_idx, self._total_pages - 1))
            self._current_page = page_idx
            self.currentPageChanged.emit(page_idx)

    # Properties and methods for total pages
    @pyqtProperty(int, notify=totalPagesChanged)
    def total_pages(self) -> int:
        return self._total_pages

    def set_total_pages(self, count: int) -> None:
        """Set the total page count"""
        if count != self._total_pages:
            self._total_pages = count
            self._doc_images = {}  # Clear cached images
            self._current_page = 0  # Reset to first page
            self.totalPagesChanged.emit(count)

    # Properties and methods for view mode
    @pyqtProperty(str, notify=viewModeChanged)
    def view_mode(self) -> str:
        return self._view_mode

    def set_view_mode(self, mode: str) -> None:
        """Switch between OVERVIEW and PRESENTER modes"""
        if mode in ("OVERVIEW", "PRESENTER") and mode != self._view_mode:
            self._view_mode = mode
            self.viewModeChanged.emit(mode)

    def toggle_view_mode(self) -> None:
        """Toggle between overview and presenter modes"""
        new_mode = "PRESENTER" if self._view_mode == "OVERVIEW" else "OVERVIEW"
        self.set_view_mode(new_mode)

    # Properties and methods for PDF path
    @pyqtProperty(str)
    def pdf_path(self) -> Optional[str]:
        return self._pdf_path

    def set_pdf_path(self, path: str) -> None:
        """Set the current PDF file path"""
        self._pdf_path = path

    # Properties and methods for PDF loaded state
    @pyqtProperty(bool)
    def is_pdf_loaded(self) -> bool:
        return self._is_pdf_loaded

    def set_pdf_loaded(self, loaded: bool) -> None:
        """Update PDF loaded state"""
        self._is_pdf_loaded = loaded

    # Page image management
    def set_page_image(self, page_idx: int, image_path: str) -> None:
        """Register a rendered page image"""
        if page_idx < self._total_pages:
            self._doc_images[page_idx] = image_path
            self.pageImagesUpdated.emit(page_idx, image_path)

    def get_page_image(self, page_idx: int) -> Optional[str]:
        """Get the image path for a page, or None if not rendered"""
        return self._doc_images.get(page_idx)

    def has_page_image(self, page_idx: int) -> bool:
        """Check if a page image is cached"""
        return page_idx in self._doc_images

    def clear_page_images(self) -> None:
        """Clear all cached page images"""
        self._doc_images = {}

    # Projector window management
    def set_projector_window(self, window) -> None:
        """Register the projector window"""
        self._projector_window = window
        is_open = window is not None
        if is_open != self._is_projector_open:
            self._is_projector_open = is_open
            self.projectorStatusChanged.emit(is_open)

    def get_projector_window(self):
        """Get the projector window reference"""
        return self._projector_window

    def is_projector_open(self) -> bool:
        """Check if projector window is open"""
        return self._is_projector_open

    # Utility methods
    def next_page(self) -> None:
        """Move to next page"""
        self.set_current_page(self._current_page + 1)

    def prev_page(self) -> None:
        """Move to previous page"""
        self.set_current_page(self._current_page - 1)

    def reset(self) -> None:
        """Reset all state"""
        self._current_page = 0
        self._total_pages = 0
        self._view_mode = "OVERVIEW"
        self._doc_images = {}
        self._pdf_path = None
        self._is_pdf_loaded = False
        self._projector_window = None
        self._is_projector_open = False
