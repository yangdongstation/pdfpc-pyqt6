"""
Configuration constants for PDF Presenter Console
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class Config:
    """Application configuration"""

    # PDF Rendering
    DEFAULT_SCALE: float = 2.0
    MAX_RENDER_THREADS: int = 4
    ENABLE_RENDER_CACHE: bool = True

    # Image Cache
    CACHE_DIR: Path = Path.home() / ".cache" / "pdfpc-pyqt6" / "page_cache"
    MAX_MEMORY_CACHE_PAGES: int = 50  # Maximum pages to keep in memory

    # UI
    DEFAULT_WINDOW_WIDTH: int = 1600
    DEFAULT_WINDOW_HEIGHT: int = 900
    THUMBNAIL_GRID_COLUMNS: int = 3
    THUMBNAIL_SIZE_WIDTH: int = 200
    THUMBNAIL_SIZE_HEIGHT: int = 150

    # View Modes
    VIEW_MODE_OVERVIEW = "OVERVIEW"
    VIEW_MODE_PRESENTER = "PRESENTER"

    # Keyboard Shortcuts
    KEYBOARD_SHORTCUTS: Dict[str, str] = None  # Will be populated at runtime

    def __post_init__(self):
        """Initialize defaults after dataclass init"""
        if self.KEYBOARD_SHORTCUTS is None:
            self.KEYBOARD_SHORTCUTS = {
                "next_page": "Right",
                "prev_page": "Left",
                "next_page_space": "Space",
                "close_projector": "Escape",
                "overview_mode": "O",
                "presenter_mode": "P",
                "toggle_fullscreen": "F",
                "goto_page": "G",
            }

        # Ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
