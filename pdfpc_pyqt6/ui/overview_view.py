"""
Overview view with thumbnail grid for quick navigation
"""

import logging
from typing import Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QFrame, QVBoxLayout, QLabel
)

from ..core.state_manager import AppState
from ..core.pdf_processor import PDFProcessor
from ..config import config


logger = logging.getLogger(__name__)


class ThumbnailWidget(QFrame):
    """
    Individual thumbnail widget showing a single PDF page
    """

    clicked = pyqtSignal(int)  # Emitted with page index when clicked

    def __init__(self, page_idx: int, state: AppState, parent=None):
        super().__init__(parent)
        self.page_idx = page_idx
        self.state = state
        self.is_current = False

        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(
            config.THUMBNAIL_SIZE_WIDTH,
            config.THUMBNAIL_SIZE_HEIGHT
        )
        self.image_label.setText(f"Page {page_idx + 1}")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #666;
                font-size: 12px;
            }
        """)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Initial style
        self.setStyleSheet("""
            ThumbnailWidget {
                border: 2px solid #444;
                border-radius: 4px;
            }
        """)

        # Connect to state changes
        self.state.currentPageChanged.connect(self._on_current_page_changed)

    def set_image(self, image_path: str) -> None:
        """Load and display thumbnail image"""
        if not image_path:
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setText(f"Failed to load")
            return

        # Scale to thumbnail size
        scaled = pixmap.scaledToWidth(
            config.THUMBNAIL_SIZE_WIDTH,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

    def mousePressEvent(self, event) -> None:
        """Handle click on thumbnail"""
        self.clicked.emit(self.page_idx)

    def _on_current_page_changed(self, current_page: int) -> None:
        """Update highlighting when current page changes"""
        is_current = (current_page == self.page_idx)
        if is_current != self.is_current:
            self.is_current = is_current
            if is_current:
                self.setStyleSheet("""
                    ThumbnailWidget {
                        border: 4px solid #00a8ff;
                        border-radius: 4px;
                    }
                """)
            else:
                self.setStyleSheet("""
                    ThumbnailWidget {
                        border: 2px solid #444;
                        border-radius: 4px;
                    }
                """)


class OverviewView(QWidget):
    """
    Overview view showing a grid of thumbnail images for all pages
    """

    pageSelected = pyqtSignal(int)  # Emitted when user selects a page

    def __init__(self, state: AppState, pdf_processor: PDFProcessor, parent=None):
        super().__init__(parent)
        self.state = state
        self.pdf_processor = pdf_processor
        self.thumbnails: Dict[int, ThumbnailWidget] = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup scrollable thumbnail grid"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Create scroll area for grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create grid widget
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)

        # Create thumbnails for all pages
        self._create_thumbnails()

        self.grid_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(self.grid_widget)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def _create_thumbnails(self) -> None:
        """Create thumbnail widgets for all pages"""
        cols = config.THUMBNAIL_GRID_COLUMNS
        total = self.state.total_pages

        for page_idx in range(total):
            row = page_idx // cols
            col = page_idx % cols

            # Create thumbnail
            thumbnail = ThumbnailWidget(page_idx, self.state)
            thumbnail.clicked.connect(self._on_thumbnail_clicked)

            self.grid_layout.addWidget(thumbnail, row, col)
            self.thumbnails[page_idx] = thumbnail

    def _on_thumbnail_clicked(self, page_idx: int) -> None:
        """Handle thumbnail click"""
        self.state.set_current_page(page_idx)
        self.pageSelected.emit(page_idx)

    def _connect_signals(self) -> None:
        """Connect state signals"""
        self.state.pageImagesUpdated.connect(self._on_page_image_updated)
        self.state.totalPagesChanged.connect(self._on_total_pages_changed)

    def _on_page_image_updated(self, page_idx: int, image_path: str) -> None:
        """Update thumbnail when page image is rendered"""
        if page_idx in self.thumbnails:
            self.thumbnails[page_idx].set_image(image_path)

    def _on_total_pages_changed(self, total: int) -> None:
        """Recreate grid when PDF is loaded"""
        # Clear old thumbnails
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.thumbnails.clear()

        # Create new thumbnails
        if total > 0:
            self._create_thumbnails()

    def get_thumbnail(self, page_idx: int) -> Optional[ThumbnailWidget]:
        """Get a specific thumbnail widget"""
        return self.thumbnails.get(page_idx)
