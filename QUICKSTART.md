# Quick Start Guide - PDF Presenter Console

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Navigate to the project directory:**
```bash
cd pdfpc-pyqt6
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Direct Python Module
```bash
python -m pdfpc_pyqt6.main
```

### Method 2: Using setup.py
```bash
pip install -e .
pdfpc-pyqt6
```

## Usage

### Basic Workflow

1. **Open a PDF file:**
   - Press `Ctrl+O` to open the file dialog
   - Select a PDF file

2. **Navigate pages:**
   - **Right arrow (→)**: Next page
   - **Left arrow (←)**: Previous page
   - **Space**: Next page

3. **Switch views:**
   - **O**: Overview mode (thumbnail grid)
   - **P**: Presenter mode (3-column layout)
   - **Tab**: Toggle between modes

4. **Open projector window:**
   - **F**: Toggle fullscreen projector on secondary display
   - **Escape**: Close projector window

### View Modes

#### Overview Mode
- Shows all pages as a grid of thumbnails (3 columns)
- Click any thumbnail to jump to that page
- Current page is highlighted in blue

#### Presenter Mode
- **Left column (1/3):** Speaker notes (left half of PDF page)
- **Center column (1/3):** Current slide (full page)
- **Right column (1/3):** Next slide preview (left half of page)

#### Projector Mode
- Fullscreen window on external display
- Shows only the current slide (right half of page for clean presentation)
- All keyboard navigation works in projector window too

## Project Structure

```
pdfpc-pyqt6/
├── pdfpc_pyqt6/              # Main package
│   ├── core/                 # Core logic
│   │   ├── state_manager.py  # Global state & signals
│   │   ├── pdf_processor.py  # PDF rendering
│   │   └── threading_manager.py  # Background rendering
│   ├── ui/                   # User interface
│   │   ├── main_window.py    # Main application window
│   │   ├── presenter_view.py # 3-column presenter layout
│   │   ├── overview_view.py  # Thumbnail grid
│   │   ├── projector_window.py # Fullscreen projector
│   │   └── widgets/          # Reusable components
│   └── utils/                # Utilities
├── requirements.txt          # Dependencies
├── setup.py                  # Package configuration
└── README.md                 # Full documentation
```

## Architecture Overview

### Signal-Driven Architecture
The application uses Qt's signal/slot system for state management:

```
AppState (single instance)
  ↓
  Emits signals when state changes
  ↓
  All UI windows listen to signals
  ↓
  UI updates automatically
```

This ensures all windows (main + projector) stay synchronized without explicit communication.

### Threading Model
- **Main Thread:** UI and event loop
- **Worker Threads:** PDF page rendering (runs in QThreadPool)
- **Thread-Safe Communication:** Qt signals

### Rendering Pipeline
1. User opens PDF → PDFProcessor loads file
2. RenderThreadPool starts rendering with priority queue:
   - Current page (highest)
   - Adjacent pages (medium)
   - Remaining pages (lowest)
3. When rendering completes → signal emitted
4. AppState.set_page_image() stores image
5. All subscribed views update automatically

## Development

### Adding a Feature
1. Identify the component responsible (core, ui, utils)
2. Implement the feature
3. Connect signals/slots if needed
4. Test with a sample PDF

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
- Follow PEP 8 conventions
- Use type hints for function arguments
- Document public methods with docstrings

## Troubleshooting

### PyMuPDF Import Error
```
ImportError: No module named 'fitz'
```
**Solution:** Install PyMuPDF:
```bash
pip install PyMuPDF
```

### Black Screen in Projector
- Ensure a PDF is loaded and current page is rendered
- Check that secondary display is detected
- Try closing and reopening projector (F key)

### Slow Rendering
- This is normal for the first load of a large PDF
- Pages are cached, subsequent loads are instant
- Rendering happens in background, UI should remain responsive

## Features Status

### ✅ Implemented (Phase 1-3)
- PDF loading and rendering
- Multi-threaded page rendering with priority queue
- Overview mode with thumbnail grid
- Presenter mode with 3-column layout (notes, current, next)
- Fullscreen projector window with multi-display support
- Keyboard navigation (arrows, space)
- View switching (O, P, Tab)
- State synchronization between windows

### 🔄 In Development (Phase 4)
- Advanced caching strategies
- Performance optimizations for large PDFs
- Comprehensive unit tests
- Error handling and logging

### 📋 Future Features
- Virtual scrolling for large PDFs
- Presentation timer
- Laser pointer tool
- Speaker notes editing
- Page bookmarks and annotations
- Custom keyboard shortcut configuration

## Performance Tips

1. **First load:** Large PDFs may take time to render all pages. This is normal.
2. **Subsequent loads:** Images are cached locally, loads are instant.
3. **Memory:** Currently keeps rendered pages in memory. For very large PDFs (1000+ pages), consider implementing virtual scrolling.
4. **Rendering:** Adjustable in config.py with `DEFAULT_SCALE` and `MAX_RENDER_THREADS`.

## Support & Documentation

- Full documentation: See [README.md](README.md)
- Implementation plan: See [../plans/streamed-jingling-feigenbaum.md](../plans/streamed-jingling-feigenbaum.md)
- Report issues: Check existing code and logs

## License

MIT License - Free to use and modify

## Acknowledgments

- Inspired by original pdfpc-ts project (TypeScript/Solid.js)
- Uses PyQt6 for GUI
- Uses PyMuPDF for PDF rendering
