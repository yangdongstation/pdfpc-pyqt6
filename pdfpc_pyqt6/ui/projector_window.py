"""
Fullscreen projector window for external display
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
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

        # Setup UI first (before window flags)
        self._setup_ui()
        self._connect_signals()
        self._setup_keyboard_shortcuts()

        # Set focus policy to receive keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Remove window decorations for cleaner presentation (after setup)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

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

        # Connect mouse click signals from page display
        self.page_display.leftClicked.connect(self.prev_page)
        self.page_display.rightClicked.connect(self.next_page)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for projector control"""
        # Note: We use keyPressEvent instead of QShortcut for better compatibility
        # with frameless windows. See keyPressEvent() method below.
        logger.info("Keyboard shortcuts ready - will be handled in keyPressEvent()")

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

    def _init_display(self) -> None:
        """Initialize the display with the current page (called asynchronously)"""
        try:
            logger.info(f"Initializing projector display with page {self.state.current_page}")
            self._update_display(self.state.current_page)
        except Exception as e:
            logger.error(f"Error initializing projector display: {e}", exc_info=True)

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

        # Show the window
        self.show()

        # Use full screen only if there are multiple screens
        if len(screens) > 1:
            QTimer.singleShot(50, self.showFullScreen)

        # Set focus to receive keyboard events
        logger.info("Setting focus to projector window for keyboard input")
        QTimer.singleShot(150, self.setFocus)

        # Initialize display with current page asynchronously to avoid blocking the event loop
        logger.info(f"Scheduling projector display initialization with page {self.state.current_page}")
        QTimer.singleShot(200, lambda: self._init_display())

    def keyPressEvent(self, event) -> None:
        """Handle keyboard events for projector control"""
        if event.isAutoRepeat():
            return

        key = event.key()
        logger.debug(f"Projector window received key: {key}")

        if key == Qt.Key.Key_Right:
            logger.info("Right arrow pressed - next page")
            self.next_page()
            event.accept()
        elif key == Qt.Key.Key_Left:
            logger.info("Left arrow pressed - previous page")
            self.prev_page()
            event.accept()
        elif key == Qt.Key.Key_Space:
            logger.info("Space pressed - next page")
            self.next_page()
            event.accept()
        elif key == Qt.Key.Key_Escape:
            logger.info("Escape pressed - closing projector")
            self.close()
            event.accept()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        """Handle window close"""
        logger.info("Projector window closed")
        self.state.set_projector_window(None)
        self.closed.emit()
        super().closeEvent(event)
