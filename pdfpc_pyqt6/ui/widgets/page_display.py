"""
Page display widget for showing PDF pages
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout


class PageDisplay(QWidget):
    """
    Widget for displaying a single PDF page image with proper scaling
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_path: Optional[str] = None
        self.current_pixmap: Optional[QPixmap] = None

        # Create label for image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 1px solid #444;
            }
        """)
        self.image_label.setMinimumSize(200, 150)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def set_image(self, image_path: str) -> None:
        """Load and display an image from file path"""
        if not image_path:
            self.image_label.clear()
            return

        path = Path(image_path)
        if not path.exists():
            self.image_label.setText(f"Image not found: {image_path}")
            return

        try:
            pixmap = QPixmap(str(path))
            if pixmap.isNull():
                self.image_label.setText(f"Failed to load image: {image_path}")
                return

            self.image_path = image_path
            self.current_pixmap = pixmap
            self._update_display()

        except Exception as e:
            self.image_label.setText(f"Error loading image: {e}")

    def set_image_crop(self, image_path: str, crop_rect: tuple) -> None:
        """
        Load image and display a cropped region.
        crop_rect: (left_ratio, top_ratio, width_ratio, height_ratio)
                   where values are in range [0, 1]
        """
        if not image_path:
            self.image_label.clear()
            return

        path = Path(image_path)
        if not path.exists():
            self.image_label.setText(f"Image not found: {image_path}")
            return

        try:
            pixmap = QPixmap(str(path))
            if pixmap.isNull():
                self.image_label.setText(f"Failed to load image: {image_path}")
                return

            # Apply crop
            w = pixmap.width()
            h = pixmap.height()
            left_ratio, top_ratio, width_ratio, height_ratio = crop_rect

            rect = QRect(
                int(left_ratio * w),
                int(top_ratio * h),
                int(width_ratio * w),
                int(height_ratio * h)
            )

            cropped = pixmap.copy(rect)
            self.image_path = image_path
            self.current_pixmap = cropped
            self._update_display()

        except Exception as e:
            self.image_label.setText(f"Error loading image: {e}")

    def _update_display(self) -> None:
        """Update the displayed image with proper scaling"""
        if not self.current_pixmap or self.current_pixmap.isNull():
            return

        # Scale to fit the label while maintaining aspect ratio
        label_size = self.image_label.size()
        if label_size.width() > 0 and label_size.height() > 0:
            scaled = self.current_pixmap.scaledToWidth(
                label_size.width(),
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

    def resizeEvent(self, event) -> None:
        """Update image when widget is resized"""
        super().resizeEvent(event)
        self._update_display()

    def clear(self) -> None:
        """Clear the displayed image"""
        self.image_label.clear()
        self.image_path = None
        self.current_pixmap = None

    def get_image_path(self) -> Optional[str]:
        """Get the currently displayed image path"""
        return self.image_path
