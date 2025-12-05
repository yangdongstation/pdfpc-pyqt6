# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pdfpc_pyqt6/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['fitz'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['Pillow', 'PyQt6.QtSql', 'PyQt6.QtNetwork', 'PyQt6.QtDBus', 'PyQt6.QtMultimedia', 'PyQt6.QtWebEngineWidgets'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    exclude_binaries=True,
    name='pdfpc-pyqt6',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='pdfpc-pyqt6',
)
