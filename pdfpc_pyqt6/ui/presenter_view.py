"""
Presenter view with 3-column layout:
Left: Speaker notes | Center: Current slide | Right: Next slide
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..core.pdf_processor import PDFProcessor
from ..core.state_manager import AppState
from .widgets.page_display import PageDisplay

logger = logging.getLogger(__name__)


class PresenterView(QWidget):
    """
    3-column presenter view showing:
    - Left: Speaker notes (left half of PDF)
    - Center: Current slide (full page)
    - Right: Next slide preview (left half of PDF)
    """

    pageClicked = pyqtSignal(int)  # Emitted when user clicks on a page area

    def __init__(self, state: AppState, pdf_processor: PDFProcessor, parent=None):
        super().__init__(parent)
        self.state = state
        self.pdf_processor = pdf_processor

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup the 3-column layout"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left column: Speaker notes (1/3 width)
        self.notes_display = PageDisplay()
        self.notes_display.setStyleSheet("""
            PageDisplay {
                border: 2px solid #444;
                border-radius: 4px;
            }
        """)

        # Center-Right column
        center_right_layout = QVBoxLayout()
        center_right_layout.setSpacing(10)

        # Center: Current slide (1/3 width)
        self.current_display = PageDisplay()
        self.current_display.setStyleSheet("""
            PageDisplay {
                border: 2px solid #00a8ff;
                border-radius: 4px;
            }
        """)

        # Right: Next slide (1/3 width)
        self.next_display = PageDisplay()
        self.next_display.setStyleSheet("""
            PageDisplay {
                border: 2px solid #444;
                border-radius: 4px;
            }
        """)

        # Add center and right to vertical layout
        center_right_layout.addWidget(self.current_display, 1)
        center_right_layout.addWidget(self.next_display, 1)

        # Create a widget to hold center-right layout
        center_right_widget = QWidget()
        center_right_widget.setLayout(center_right_layout)

        # Add all columns to main layout with proportions
        # 3:5:5 ratio (notes:current:next)
        main_layout.addWidget(self.notes_display, 3)
        main_layout.addWidget(center_right_widget, 10)  # 5+5

        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        """Connect state signals to update displays"""
        self.state.currentPageChanged.connect(self._update_displays)
        self.state.pageImagesUpdated.connect(self._on_page_image_updated)
        self.state.totalPagesChanged.connect(self._on_total_pages_changed)

    def _update_displays(self, current_page: int) -> None:
        """Update all three displays when current page changes"""
        # Update notes display (left half of current page)
        if self.state.has_page_image(current_page):
            image_path = self.state.get_page_image(current_page)
            self.notes_display.set_image_crop(image_path, (0, 0, 0.5, 1.0))

        # Update current display (full current page)
        if self.state.has_page_image(current_page):
            image_path = self.state.get_page_image(current_page)
            self.current_display.set_image(image_path)

        # Update next display (left half of next page)
        next_page = current_page + 1
        if next_page < self.state.total_pages:
            if self.state.has_page_image(next_page):
                image_path = self.state.get_page_image(next_page)
                self.next_display.set_image_crop(image_path, (0, 0, 0.5, 1.0))
            else:
                self.next_display.clear()
        else:
            self.next_display.clear()

        logger.debug(f"Updated displays for page {current_page}")

    def _on_page_image_updated(self, page_idx: int, image_path: str) -> None:
        """Handle when a page image is rendered"""
        current = self.state.current_page
        # Only update if this page is currently visible
        if page_idx == current:
            self._update_displays(current)
        elif page_idx == current + 1:
            # Update next slide if its image just became available
            self.next_display.set_image_crop(image_path, (0, 0, 0.5, 1.0))

    def _on_total_pages_changed(self, total: int) -> None:
        """Handle when total page count changes (PDF opened)"""
        self.current_display.clear()
        self.next_display.clear()
        self.notes_display.clear()

    def get_current_display(self) -> PageDisplay:
        """Get the current slide display widget"""
        return self.current_display

    def get_next_display(self) -> PageDisplay:
        """Get the next slide display widget"""
        return self.next_display

    def get_notes_display(self) -> PageDisplay:
        """Get the notes display widget"""
        return self.notes_display
