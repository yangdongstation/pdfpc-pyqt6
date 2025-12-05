# Distribution Guide - PDF Presenter Console

## Quick Download & Install

### For Linux Users

```bash
# Download the package
wget https://[your-server]/pdfpc-pyqt6-linux-x86_64.tar.gz
# or
curl -O https://[your-server]/pdfpc-pyqt6-linux-x86_64.tar.gz

# Extract
tar -xzf pdfpc-pyqt6-linux-x86_64.tar.gz

# Run
./pdfpc-pyqt6/pdfpc-pyqt6

# Optional: Create alias for easy access
alias pdfpc-pyqt6="~/path/to/pdfpc-pyqt6/pdfpc-pyqt6"
```

### For Windows Users

```powershell
# Download: pdfpc-pyqt6-windows-x86_64.zip
# Extract the ZIP file
# Double-click pdfpc-pyqt6\pdfpc-pyqt6.exe

# Or from PowerShell:
Expand-Archive -Path pdfpc-pyqt6-windows-x86_64.zip
.\pdfpc-pyqt6\pdfpc-pyqt6.exe
```

### For macOS Users

```bash
# Download: pdfpc-pyqt6-macos-x86_64.zip
# Extract
unzip pdfpc-pyqt6-macos-x86_64.zip

# Run
./pdfpc-pyqt6/pdfpc-pyqt6

# Note: First launch may show security warning
# Right-click the app and select "Open" to allow
```

---

## System Requirements

### Linux
- **OS:** Ubuntu 20.04+, Debian 11+, Fedora 35+, CentOS 8+
- **Display:** X11 or Wayland
- **RAM:** 256 MB minimum, 1 GB recommended
- **Disk:** 20 MB for installation + cache

### Windows
- **OS:** Windows 7 SP1 or later, Windows 10/11 recommended
- **RAM:** 256 MB minimum, 1 GB recommended
- **Disk:** 20 MB for installation + cache

### macOS
- **OS:** macOS 10.13 (High Sierra) or later, Monterey/Ventura recommended
- **RAM:** 256 MB minimum, 1 GB recommended
- **Disk:** 25 MB for installation + cache

---

## Installation Methods

### Method 1: Extract & Run (Simplest)

```bash
tar -xzf pdfpc-pyqt6-linux-x86_64.tar.gz
cd pdfpc-pyqt6
./pdfpc-pyqt6
```

**Advantages:**
- No installation needed
- Portable (run from USB, cloud storage, etc.)
- Easy to uninstall (just delete the folder)

### Method 2: Create Desktop Shortcut

**Linux (GNOME/KDE):**
```bash
# Create .desktop file
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/pdfpc-pyqt6.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=PDF Presenter Console
Comment=Present PDF slides with speaker notes
Exec=/home/username/pdfpc-pyqt6/pdfpc-pyqt6
Icon=presentation
MimeType=application/pdf
Categories=Office;Presentation;
EOF

# Make it executable
chmod +x ~/.local/share/applications/pdfpc-pyqt6.desktop
```

**Windows (shortcut):**
1. Right-click on `pdfpc-pyqt6.exe`
2. Select "Send to" → "Desktop (create shortcut)"
3. The shortcut will be created on your desktop

### Method 3: Create System-Wide Alias

**Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias pdfpc='/home/username/pdfpc-pyqt6/pdfpc-pyqt6'

# Then reload:
source ~/.bashrc

# Now you can run from anywhere:
pdfpc ~/Documents/presentation.pdf
```

---

## Usage

### Opening a PDF
1. Launch the application
2. Press `Ctrl+O` to open a PDF file
3. Or drag and drop a PDF onto the window

### Navigation
| Key | Action |
|-----|--------|
| `→` | Next page |
| `←` | Previous page |
| `Space` | Next page |
| `O` | Overview mode |
| `P` | Presenter mode |
| `Tab` | Toggle view mode |
| `F` | Toggle projector window |

### Presenter Mode Features
- **Left panel:** Speaker notes (left half of PDF)
- **Center panel:** Current slide (full page)
- **Right panel:** Next slide preview (left half of page)

### Projector Mode
- Full-screen display on external monitor
- Same keyboard controls work in projector window
- Press `Escape` to close projector

---

## Troubleshooting

### Problem: Application won't start

**Linux:**
```bash
# Check for missing libraries
ldd ./pdfpc-pyqt6/pdfpc-pyqt6 | grep "not found"

# Check for permission issues
chmod +x ./pdfpc-pyqt6/pdfpc-pyqt6

# Run with debug info
LD_DEBUG=libs ./pdfpc-pyqt6/pdfpc-pyqt6 2>&1 | head -20
```

**Windows:**
- Ensure you're running on a supported Windows version
- Try running as Administrator
- Check if MSVC runtime is installed

### Problem: Display issues

**No window appears:**
```bash
# Linux - check DISPLAY variable
echo $DISPLAY

# Should show something like :0 or :1
# If empty, try:
export DISPLAY=:0
./pdfpc-pyqt6/pdfpc-pyqt6
```

**Over SSH:**
```bash
# Enable X11 forwarding
ssh -X user@host
./pdfpc-pyqt6/pdfpc-pyqt6
```

### Problem: Projector not working

1. Ensure external display is connected
2. Press `F` to toggle projector
3. If it opens on the wrong screen, close and try again
4. Use system display settings to configure monitors

### Problem: Slow PDF loading

**Large PDFs may take time to render initially:**
- First load renders all pages in background
- Subsequent loads use cached images
- Cache is stored in `~/.cache/pdfpc-pyqt6/`
- If cache is full, clear old files

---

## Advanced Configuration

### Cache Management

**View cache location:**
```bash
ls ~/.cache/pdfpc-pyqt6/page_cache/
```

**Clear cache (if needed):**
```bash
rm -rf ~/.cache/pdfpc-pyqt6/page_cache/
# Cache will be recreated next time you open a PDF
```

### Performance Tuning

**For slower systems:**
- Use Overview mode instead of Presenter mode (lower memory usage)
- Open smaller PDFs first to test performance
- Close other applications to free memory

**For faster systems:**
- All settings are already optimized
- No configuration needed

### Display Configuration

**Multi-monitor setup:**
1. Set up displays in your OS display settings
2. Open PDF Presenter Console
3. Press `F` to open projector on secondary display
4. The app will automatically detect and use the secondary monitor

---

## Uninstallation

### Linux/macOS
```bash
# Simply delete the folder
rm -rf ~/pdfpc-pyqt6

# Clean up cache (optional)
rm -rf ~/.cache/pdfpc-pyqt6

# Remove desktop shortcut (if created)
rm ~/.local/share/applications/pdfpc-pyqt6.desktop
```

### Windows
```powershell
# Delete the folder via File Explorer
# or from PowerShell:
Remove-Item -Recurse -Force pdfpc-pyqt6

# Clean up cache
Remove-Item -Recurse -Force $env:APPDATA\..\Local\pdfpc-pyqt6
```

---

## Verification & Checksums

### File Verification

To verify you downloaded the correct file:

```bash
# Calculate checksum of downloaded file
sha256sum pdfpc-pyqt6-linux-x86_64.tar.gz

# Compare with official checksum
cat checksums.sha256
```

### Expected Checksums

```
pdfpc-pyqt6-linux-x86_64.tar.gz: [SHA256 hash]
pdfpc-pyqt6-windows-x86_64.zip:  [SHA256 hash]
pdfpc-pyqt6-macos-x86_64.zip:    [SHA256 hash]
```

---

## Support

### Getting Help

1. **Check documentation:**
   - `README.md` - Feature overview
   - `QUICKSTART.md` - Quick start guide
   - `BUILD.md` - Build instructions

2. **Common issues:** See Troubleshooting section above

3. **Report bugs:**
   - Check GitHub issues first
   - Provide: OS, PDF sample (if possible), error message

### Version Information

To check your version:
```bash
./pdfpc-pyqt6 --version
# or check the About dialog in the app
```

---

## Upgrade Instructions

### From Older Versions

1. **Download new version**
2. **Extract to a new location** (or backup old version first)
3. **Delete old folder** (optional - new version can coexist)
4. **Run new version**

**Note:** Settings and cache are preserved in `~/.cache/pdfpc-pyqt6/`

---

## Privacy & Safety

### What the Application Does
- ✅ Opens PDF files from your computer
- ✅ Renders pages to images (cached locally)
- ✅ Manages keyboard input and display
- ❌ Does NOT connect to the internet
- ❌ Does NOT collect any usage data
- ❌ Does NOT modify your files

### Data Storage
- PDF files are not modified or copied
- Rendered pages are cached in `~/.cache/pdfpc-pyqt6/`
- Cache is only on your local machine

### Security
- Application is bundled with all dependencies (no external downloads during runtime)
- No external API calls
- All processing is local

---

## System Integration (Optional)

### Create Application Menu Entry

**Linux:**
```bash
# GNOME/KDE - file manager will detect .desktop file automatically
mkdir -p ~/.local/share/applications
# (see Method 2 above)
```

### File Association

**Linux:**
```bash
# Associate PDF files with this app
xdg-mime default pdfpc-pyqt6.desktop application/pdf
```

**Windows:**
1. Right-click on a PDF file
2. Select "Open with" → "Choose another app"
3. Browse to `pdfpc-pyqt6.exe`
4. Check "Always use this app"

---

## Feedback

We'd love to hear from you!

- ⭐ Star the project on GitHub
- 💬 Share your feedback
- 🐛 Report bugs
- 💡 Suggest features

---

## License

PDF Presenter Console is released under the **MIT License**.

You are free to:
- ✅ Use commercially
- ✅ Modify the source code
- ✅ Distribute
- ✅ Use privately

See `LICENSE` file for full terms.

---

## Frequently Asked Questions (FAQ)

### Q: Do I need Python installed?
**A:** No! Python is bundled with the application.

### Q: Can I run this on a Raspberry Pi?
**A:** No, this build is for x86_64 processors. ARM64 build would be needed.

### Q: Is there a portable version (USB)?
**A:** Yes! Just extract to a USB drive and run. Everything is self-contained.

### Q: Can I edit PDFs with this?
**A:** No, this is a viewer/presenter tool only. Use a PDF editor for modifications.

### Q: How do I connect to a projector?
**A:** Press `F` to open the projector window. Use your OS display settings to configure the external monitor.

### Q: Can I use this for presentations online (Zoom, Teams)?
**A:** Yes! Use your OS screen sharing to share the presenter view. The projector window will show the slide only.

### Q: How large a PDF can it handle?
**A:** Tested up to 500+ pages. Very large PDFs (1000+ pages) may take longer to render initially.

### Q: Can I use this in fullscreen?
**A:** Yes, the projector window is already fullscreen on secondary displays.

### Q: How do I save the presentation?
**A:** PDFs are not modified. To save notes, take screenshots or use the Notes feature in Presenter mode.

---

**Download & enjoy! 🎉**

For latest version and updates, visit: [project repository]
