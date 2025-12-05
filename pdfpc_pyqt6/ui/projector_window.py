"""
Fullscreen projector window for external display
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QKeySequence, QShortcut

from ..core.state_manager import AppState
from ..core.pdf_processor import PDFProcessor
from .widgets.page_display import PageDisplay


logger = logging.getLogger(__name__)


class ProjectorWindow(QMainWindow):
    """
    Fullscreen projector window for displaying slides on external display.
    Synchronized with main window through shared AppState.
    """

    closed = pyqtSignal()  # Emitted when window is closed

    def __init__(self, state: AppState, pdf_processor: PDFProcessor, parent=None):
        super().__init__(parent)
        self.state = state
        self.pdf_processor = pdf_processor
        self.setWindowTitle("PDF Presenter - Projector")

        # Remove window decorations for cleaner presentation
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._setup_keyboard_shortcuts()

    def _setup_ui(self) -> None:
        """Setup the projector window UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Page display (full screen)
        self.page_display = PageDisplay()
        self.page_display.image_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: none;
            }
        """)

        layout.addWidget(self.page_display)
        central_widget.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect to state signals"""
        self.state.currentPageChanged.connect(self._on_page_changed)
        self.state.pageImagesUpdated.connect(self._on_page_image_updated)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for projector control"""
        # Navigation in projector window
        QShortcut(Qt.Key.Key_Right, self, self.next_page)
        QShortcut(Qt.Key.Key_Left, self, self.prev_page)
        QShortcut(Qt.Key.Key_Space, self, self.next_page)

        # Close projector with Escape
        QShortcut(Qt.Key.Key_Escape, self, self.close)

    def _on_page_changed(self, page_idx: int) -> None:
        """Handle page change from main window"""
        self._update_display(page_idx)

    def _on_page_image_updated(self, page_idx: int, image_path: str) -> None:
        """Handle page image update"""
        if page_idx == self.state.current_page:
            self.page_display.set_image(image_path)

    def _update_display(self, page_idx: int) -> None:
        """Update the displayed page"""
        if self.state.has_page_image(page_idx):
            image_path = self.state.get_page_image(page_idx)
            self.page_display.set_image(image_path)
        else:
            # Page not yet rendered, show black screen
            self.page_display.clear()

    def next_page(self) -> None:
        """Move to next page"""
        if self.state.current_page < self.state.total_pages - 1:
            self.state.next_page()

    def prev_page(self) -> None:
        """Move to previous page"""
        if self.state.current_page > 0:
            self.state.prev_page()

    def show_on_screen(self, screen_index: int = 1) -> None:
        """
        Show projector window on specified screen.
        screen_index: 0 = main screen, 1 = secondary screen, etc.
        """
        from PyQt6.QtWidgets import QApplication

        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            screen = screens[screen_index]
            self.setGeometry(screen.geometry())
            logger.info(f"Showing projector on screen {screen_index}: {screen.geometry()}")
        else:
            logger.warning(f"Screen {screen_index} not available, using screen 0")
            if screens:
                screen = screens[0]
                self.setGeometry(screen.geometry())

        self.showFullScreen()

        # Initialize display with current page
        logger.info(f"Initializing projector display with page {self.state.current_page}")
        self._update_display(self.state.current_page)

    def closeEvent(self, event) -> None:
        """Handle window close"""
        logger.info("Projector window closed")
        self.state.set_projector_window(None)
        self.closed.emit()
        super().closeEvent(event)
