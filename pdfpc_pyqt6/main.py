"""
Main entry point for PDF Presenter Console application
"""

import sys
import logging

from PyQt6.QtWidgets import QApplication

from pdfpc_pyqt6.ui.main_window import MainWindow


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Application entry point"""
    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("Application started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
