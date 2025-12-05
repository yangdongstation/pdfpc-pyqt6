# PDF Presenter Console - PyQt6 Edition

A desktop application for presenting PDF presentations with speaker notes support.

## Features

- **PDF Viewing**: Open and view PDF files
- **Presenter View**: 3-column layout showing speaker notes, current slide, and next slide
- **Overview Mode**: Thumbnail grid view for quick navigation
- **Keyboard Navigation**: Arrow keys and space for navigation
- **Projector Support**: Separate fullscreen window for external display
- **Multi-threading**: Background PDF rendering for smooth UI
- **Smart Caching**: Intelligent image caching for performance

## Installation

### From Source

1. Clone the repository:
```bash
git clone <repository-url>
cd pdfpc-pyqt6
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use setup.py:
```bash
pip install -e .
```

3. Run the application:
```bash
python -m pdfpc_pyqt6.main
```

Or if installed with setup.py:
```bash
pdfpc-pyqt6
```

## Requirements

- Python 3.8 or higher
- PyQt6
- PyMuPDF (fitz)
- Pillow

## Usage

### Opening a PDF
- Use **Ctrl+O** to open a PDF file
- Or drag and drop a PDF file into the window (when implemented)

### Navigation
- **Arrow Keys** (← →): Previous/Next page
- **Space**: Next page
- **Escape**: Close projector window (when open)

### Views
- **Overview Mode**: Shows all pages as thumbnails in a grid
- **Presenter Mode**: Shows speaker notes, current slide, and next slide
  - Left column: Speaker notes (left half of PDF page)
  - Middle column: Current slide (full page)
  - Right column: Next slide and notes preview (left half of page)

### Projector
- Press the projector button to open fullscreen presentation view on external display

## Project Structure

```
pdfpc-pyqt6/
├── pdfpc_pyqt6/
│   ├── core/              # Core PDF processing and state management
│   │   ├── pdf_processor.py      # PDF loading and rendering
│   │   ├── state_manager.py      # Global state (Qt signals)
│   │   └── threading_manager.py  # Background rendering threads
│   ├── ui/                # User interface components
│   │   ├── main_window.py        # Main application window
│   │   ├── presenter_view.py     # Presenter 3-column view
│   │   ├── overview_view.py      # Thumbnail grid view
│   │   ├── projector_window.py   # Fullscreen projector window
│   │   └── widgets/              # Reusable UI widgets
│   │       └── page_display.py   # Page image display
│   └── utils/             # Utility modules
│       ├── image_cache.py        # Image caching
│       └── keyboard_handler.py   # Keyboard shortcut management
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
└── README.md             # This file
```

## Development

### Current Phase: Phase 1 - Basic Framework

✅ Completed:
- Project structure and initialization
- PDF loading and single-page rendering
- Global state management with Qt signals
- Main window with file selection
- Basic keyboard navigation

🔄 In Progress:
- Phase 2: Core UI features (Presenter view, Overview view)
- Phase 3: Projector window support
- Phase 4: Performance optimization and testing

### Running Tests

```bash
python -m pytest tests/
```

## Architecture

### State Management

The application uses a **signal-driven architecture** based on Qt's signal/slot mechanism:

```
AppState (QObject)
  └── Signals: currentPageChanged, pageImagesUpdated, viewModeChanged, etc.
      └── All UI windows subscribe to these signals
          └── UI updates automatically when state changes
```

This ensures:
- All windows stay synchronized automatically
- No manual communication code between components
- Easy to test each component independently
- Clean separation of concerns

### Rendering Pipeline

1. User opens PDF → PDFProcessor.load_pdf()
2. PDF loads → State emits totalPagesChanged signal
3. RenderThreadPool.render_priority_pages() called
4. Pages render in background:
   - Current page (highest priority)
   - Adjacent pages (+/- 3)
   - All other pages
5. When page renders → renderFinished signal
6. Signal handler → AppState.set_page_image()
7. All subscribed UI views update automatically

### Threading Model

- **Main thread**: UI and event loop (Qt)
- **Worker threads**: PDF page rendering (QThreadPool)
- **Communication**: Qt signals (thread-safe)

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Original pdfpc-ts project for architectural inspiration
- PyQt6 for the GUI framework
- PyMuPDF for PDF rendering
