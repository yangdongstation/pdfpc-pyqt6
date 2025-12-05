"""
Setup configuration for PDF Presenter Console
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="pdfpc-pyqt6",
    version="0.1.0",
    description="PDF Presenter Console - Desktop application for presenting with speaker notes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PDF Presenter",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "PyMuPDF>=1.23.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pdfpc-pyqt6=pdfpc_pyqt6.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Viewers",
    ],
)
