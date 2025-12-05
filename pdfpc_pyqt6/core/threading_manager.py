"""
Threading and background rendering management
"""

import logging
from collections import deque
from typing import List, Optional

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from .pdf_processor import PDFProcessor
from .state_manager import AppState
from ..config import config


logger = logging.getLogger(__name__)


class PDFRenderWorker(QRunnable):
    """
    Worker that runs in QThreadPool to render PDF pages.
    Uses callbacks instead of signals to avoid QObject thread affinity issues.
    """

    def __init__(self, pdf_processor: PDFProcessor, page_indices: List[int],
                 on_finished_callback=None, on_error_callback=None):
        super().__init__()
        self.pdf_processor = pdf_processor
        self.page_indices = page_indices
        self.on_finished_callback = on_finished_callback
        self.on_error_callback = on_error_callback

    def run(self):
        """Render pages in the thread pool"""
        logger.info(f"PDFRenderWorker.run() started for pages: {self.page_indices}")
        for page_idx in self.page_indices:
            try:
                logger.debug(f"Worker rendering page {page_idx}")
                image_path = self.pdf_processor.render_page(page_idx)
                logger.debug(f"render_page({page_idx}) returned: {image_path}")
                if image_path:
                    logger.info(f"Worker completed page {page_idx}: {image_path}")
                    if self.on_finished_callback:
                        self.on_finished_callback(page_idx, image_path)
                else:
                    logger.warning(f"render_page({page_idx}) returned None")
                    if self.on_error_callback:
                        self.on_error_callback(page_idx, "Failed to render page")
            except Exception as e:
                logger.error(f"Worker error rendering page {page_idx}: {e}", exc_info=True)
                if self.on_error_callback:
                    self.on_error_callback(page_idx, str(e))
        logger.info(f"PDFRenderWorker.run() completed for pages: {self.page_indices}")


class RenderThreadPool(QObject):
    """
    Manages PDF page rendering using QThreadPool with priority queue
    """

    renderFinished = pyqtSignal(int, str)  # (page_idx, image_path)
    renderError = pyqtSignal(int, str)  # (page_idx, error_message)
    renderProgress = pyqtSignal(int, int)  # (completed, total)

    def __init__(self, pdf_processor: PDFProcessor, state: AppState, max_threads: int = 4):
        super().__init__()
        self.pdf_processor = pdf_processor
        self.state = state
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_threads)
        self.max_threads = max_threads

        self.priority_queue = deque()  # Priority rendering queue
        self.rendered_pages = set()  # Track which pages are rendered
        self.total_pages = 0

        # Connect state signals
        self.state.totalPagesChanged.connect(self._on_total_pages_changed)

    def render_priority_pages(self, current_page: int) -> None:
        """
        Start rendering pages with priority queue strategy:
        1. Current page (highest priority)
        2. Adjacent pages (+/- 3 pages)
        3. All other pages (lowest priority)
        """
        logger.info(f"render_priority_pages called with current_page={current_page}")
        logger.debug(f"total_pages={self.total_pages}, already_rendered={len(self.rendered_pages)}")

        if self.total_pages <= 0:
            logger.warning("total_pages <= 0, skipping render")
            return

        # Build priority queue
        priority_queue = []

        # High priority: current and next pages
        for offset in [0, 1]:
            page_idx = current_page + offset
            if 0 <= page_idx < self.total_pages and page_idx not in self.rendered_pages:
                priority_queue.append(page_idx)

        # Medium priority: adjacent pages
        for offset in [-3, -2, -1, 2, 3]:
            page_idx = current_page + offset
            if (0 <= page_idx < self.total_pages and
                page_idx not in priority_queue and
                page_idx not in self.rendered_pages):
                priority_queue.append(page_idx)

        # Low priority: remaining pages
        for page_idx in range(self.total_pages):
            if (page_idx not in priority_queue and
                page_idx not in self.rendered_pages):
                priority_queue.append(page_idx)

        logger.info(f"Priority queue built with {len(priority_queue)} pages: {priority_queue[:10]}...")
        # Submit render tasks
        self._submit_render_tasks(priority_queue)

    def render_all_pages(self) -> None:
        """Render all pages in priority order"""
        if self.total_pages <= 0:
            return

        page_indices = [i for i in range(self.total_pages)
                       if i not in self.rendered_pages]
        self._submit_render_tasks(page_indices)

    def _submit_render_tasks(self, page_indices: List[int]) -> None:
        """Submit render tasks to thread pool"""
        if not page_indices:
            logger.info("No pages to render")
            return

        logger.info(f"_submit_render_tasks called with {len(page_indices)} pages: {page_indices}")

        # Split into batches to avoid too many workers
        batch_size = max(1, len(page_indices) // self.max_threads)
        batches = [page_indices[i:i + batch_size]
                  for i in range(0, len(page_indices), batch_size)]

        logger.info(f"Split into {len(batches)} batches (batch_size={batch_size})")

        for batch_idx, batch in enumerate(batches):
            logger.info(f"Creating worker for batch {batch_idx}: {batch}")
            worker = PDFRenderWorker(
                self.pdf_processor,
                batch,
                on_finished_callback=self._on_render_finished,
                on_error_callback=self._on_render_error
            )
            logger.info(f"Callbacks registered, starting worker for batch {batch_idx}")
            self.thread_pool.start(worker)

        logger.info(f"All {len(batches)} workers submitted to thread pool")

    def _on_render_finished(self, page_idx: int, image_path: str) -> None:
        """Handle successful render"""
        logger.info(f"_on_render_finished called: page_idx={page_idx}, image_path={image_path}")
        self.rendered_pages.add(page_idx)
        logger.debug(f"Added page {page_idx} to rendered_pages, now: {self.rendered_pages}")
        self.state.set_page_image(page_idx, image_path)
        self.renderFinished.emit(page_idx, image_path)

        # Emit progress
        progress = len(self.rendered_pages)
        logger.debug(f"Rendering progress: {progress}/{self.total_pages}")
        self.renderProgress.emit(progress, self.total_pages)

    def _on_render_error(self, page_idx: int, error_msg: str) -> None:
        """Handle render error"""
        logger.error(f"Render error for page {page_idx}: {error_msg}")
        self.renderError.emit(page_idx, error_msg)

    def _on_total_pages_changed(self, total: int) -> None:
        """Reset when PDF changes"""
        self.total_pages = total
        self.rendered_pages = set()

    def wait_for_all(self) -> None:
        """Wait for all threads to complete (blocking)"""
        self.thread_pool.waitForDone()

    def clear(self) -> None:
        """Clear the render queue and reset"""
        self.thread_pool.clear()
        self.rendered_pages = set()
        self.priority_queue.clear()

    def is_page_rendered(self, page_idx: int) -> bool:
        """Check if a page has been rendered"""
        return page_idx in self.rendered_pages
