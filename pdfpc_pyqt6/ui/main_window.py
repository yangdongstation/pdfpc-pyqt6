"""
Main application window
"""

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QLabel,
    QFileDialog, QMessageBox, QProgressDialog
)
from PyQt6.QtGui import QKeySequence, QShortcut

from ..core.state_manager import AppState
from ..core.pdf_processor import PDFProcessor
from ..core.threading_manager import RenderThreadPool
from ..config import config
from .widgets.page_display import PageDisplay
from .presenter_view import PresenterView
from .overview_view import OverviewView
from .projector_window import ProjectorWindow


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window with PDF viewing and navigation
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Presenter Console")
        self.setGeometry(100, 100, config.DEFAULT_WINDOW_WIDTH, config.DEFAULT_WINDOW_HEIGHT)

        # Core components
        self.state = AppState()
        self.pdf_processor = PDFProcessor()
        self.render_thread_pool = RenderThreadPool(
            self.pdf_processor,
            self.state,
            max_threads=config.MAX_RENDER_THREADS
        )

        # UI setup
        self._setup_ui()
        self._connect_signals()
        self._setup_keyboard_shortcuts()

        self.progress_dialog = None

    def _setup_ui(self) -> None:
        """Setup main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create stacked widget for view switching
        self.stacked_widget = QStackedWidget()

        # Create welcome screen
        self.welcome_label = QLabel()
        self.welcome_label.setText(
            "Welcome to PDF Presenter Console\n\n"
            "Open a PDF file to get started\n\n"
            "Ctrl+O: Open PDF file"
        )
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #888;
                background-color: #1a1a1a;
            }
        """)

        # Create views
        self.overview_view = OverviewView(self.state, self.pdf_processor)
        self.presenter_view = PresenterView(self.state, self.pdf_processor)

        # Add all to stacked widget
        self.stacked_widget.addWidget(self.welcome_label)
        self.stacked_widget.addWidget(self.overview_view)
        self.stacked_widget.addWidget(self.presenter_view)

        layout.addWidget(self.stacked_widget)
        central_widget.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect signals and slots"""
        # PDF processor signals
        self.pdf_processor.renderError.connect(self._on_render_error)

        # State signals
        self.state.pdfLoadingStarted.connect(self._on_pdf_loading_started)
        self.state.pdfLoadingFinished.connect(self._on_pdf_loading_finished)
        self.state.pdfLoadingError.connect(self._on_pdf_loading_error)
        self.state.pageImagesUpdated.connect(self._on_page_image_updated)
        self.state.viewModeChanged.connect(self._on_view_mode_changed)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts"""
        # File operations
        QShortcut(QKeySequence.StandardKey.Open, self, self.open_pdf)

        # Navigation
        QShortcut(Qt.Key.Key_Right, self, self.next_page)
        QShortcut(Qt.Key.Key_Left, self, self.prev_page)
        QShortcut(Qt.Key.Key_Space, self, self.next_page)

        # View switching
        QShortcut(Qt.Key.Key_O, self, lambda: self.set_view_mode("OVERVIEW"))
        QShortcut(Qt.Key.Key_P, self, lambda: self.set_view_mode("PRESENTER"))
        QShortcut(Qt.Key.Key_Tab, self, self.toggle_view_mode)

        # Projector control
        QShortcut(Qt.Key.Key_F, self, self.toggle_projector)

    def open_pdf(self) -> None:
        """Open a PDF file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )

        if not file_path:
            return

        self._load_pdf(file_path)

    def _load_pdf(self, pdf_path: str) -> None:
        """Load a PDF file"""
        try:
            logger.info(f"_load_pdf called with {pdf_path}")
            self.state.pdfLoadingStarted.emit()

            # Wait for old rendering tasks to complete
            logger.debug("Waiting for old render tasks to complete")
            self.render_thread_pool.wait_for_all()

            # Clear old cache and state before loading new PDF
            logger.debug("Clearing old PDF cache and state")
            self.pdf_processor.clear_cache()
            self.state.clear_page_images()
            self.state.set_current_page(0)
            self.render_thread_pool.clear()

            # Load PDF
            logger.debug("Calling pdf_processor.load_pdf()")
            if not self.pdf_processor.load_pdf(pdf_path):
                logger.error("pdf_processor.load_pdf returned False")
                self.state.pdfLoadingError.emit("Failed to load PDF")
                return

            # Update state
            page_count = self.pdf_processor.get_page_count()
            logger.debug(f"Page count: {page_count}")
            self.state.set_total_pages(page_count)
            self.state.set_pdf_path(pdf_path)
            self.state.set_pdf_loaded(True)

            logger.info(f"Loaded PDF: {pdf_path} with {page_count} pages")

            # Start rendering
            logger.info("Calling render_thread_pool.render_priority_pages(0)")
            self.render_thread_pool.render_priority_pages(0)
            logger.info("render_priority_pages call completed")

            self.state.pdfLoadingFinished.emit()
            logger.info("pdfLoadingFinished signal emitted")

        except Exception as e:
            logger.error(f"Error loading PDF: {e}", exc_info=True)
            self.state.pdfLoadingError.emit(str(e))

    def next_page(self) -> None:
        """Move to next page"""
        if self.state.is_pdf_loaded and self.state.current_page < self.state.total_pages - 1:
            self.state.next_page()
            # Prioritize rendering nearby pages
            self.render_thread_pool.render_priority_pages(self.state.current_page)

    def prev_page(self) -> None:
        """Move to previous page"""
        if self.state.is_pdf_loaded and self.state.current_page > 0:
            self.state.prev_page()
            # Prioritize rendering nearby pages
            self.render_thread_pool.render_priority_pages(self.state.current_page)

    def _on_render_error(self, error_msg: str) -> None:
        """Handle render errors"""
        logger.error(f"Render error: {error_msg}")
        QMessageBox.warning(self, "Render Error", error_msg)

    def _on_pdf_loading_started(self) -> None:
        """Handle PDF loading start"""
        self.welcome_label.setText("Loading PDF...")

    def _on_pdf_loading_finished(self) -> None:
        """Handle PDF loading completion"""
        # Switch to overview mode automatically
        self.set_view_mode("OVERVIEW")

        self.welcome_label.setText(
            f"Loaded: {Path(self.state.pdf_path).name}\n\n"
            f"Pages: {self.state.total_pages}\n\n"
            "Use arrow keys to navigate\n"
            "Phase 1: Basic functionality working!"
        )

    def _on_pdf_loading_error(self, error_msg: str) -> None:
        """Handle PDF loading errors"""
        logger.error(f"PDF loading error: {error_msg}")
        self.welcome_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "PDF Loading Error", error_msg)

    def _on_page_image_updated(self, page_idx: int, image_path: str) -> None:
        """Handle page image update"""
        logger.debug(f"Page {page_idx} rendered: {image_path}")

    def set_view_mode(self, mode: str) -> None:
        """Switch to a specific view mode"""
        if not self.state.is_pdf_loaded:
            return

        self.state.set_view_mode(mode)

    def toggle_view_mode(self) -> None:
        """Toggle between overview and presenter modes"""
        if not self.state.is_pdf_loaded:
            return

        self.state.toggle_view_mode()

    def _on_view_mode_changed(self, mode: str) -> None:
        """Handle view mode change"""
        if mode == "OVERVIEW":
            self.stacked_widget.setCurrentWidget(self.overview_view)
            logger.info("Switched to overview mode")
        elif mode == "PRESENTER":
            self.stacked_widget.setCurrentWidget(self.presenter_view)
            logger.info("Switched to presenter mode")

    def toggle_projector(self) -> None:
        """Toggle projector window open/close"""
        if not self.state.is_pdf_loaded:
            QMessageBox.warning(self, "No PDF", "Please open a PDF file first")
            return

        if self.state.is_projector_open():
            self.close_projector()
        else:
            self.open_projector()

    def open_projector(self) -> None:
        """Open projector window on secondary display"""
        try:
            from PyQt6.QtWidgets import QApplication

            projector = ProjectorWindow(self.state, self.pdf_processor, self)
            self.state.set_projector_window(projector)

            # Try to show on secondary screen
            screens = QApplication.screens()
            screen_idx = 1 if len(screens) > 1 else 0

            projector.show_on_screen(screen_idx)
            logger.info(f"Projector opened on screen {screen_idx}")

            # Connect close signal
            projector.closed.connect(self._on_projector_closed)

        except Exception as e:
            logger.error(f"Failed to open projector: {e}")
            QMessageBox.critical(self, "Projector Error", f"Failed to open projector: {e}")

    def close_projector(self) -> None:
        """Close projector window"""
        if self.state.is_projector_open():
            projector = self.state.get_projector_window()
            if projector:
                projector.close()
            self.state.set_projector_window(None)
            logger.info("Projector closed")

    def _on_projector_closed(self) -> None:
        """Handle projector window close"""
        self.state.set_projector_window(None)
        logger.info("Projector window closed by user")

    def closeEvent(self, event) -> None:
        """Handle window close"""
        self.pdf_processor.close()
        self.render_thread_pool.wait_for_all()
        super().closeEvent(event)
