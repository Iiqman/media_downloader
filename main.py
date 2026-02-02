"""
Media Downloader - Multi Platform Desktop Application
Mendukung: YouTube, Instagram, TikTok, Facebook
"""
import os
import sys
import traceback
import faulthandler
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer, qInstallMessageHandler, QStandardPaths


# ---------------------------
# Logging utilities
# ---------------------------
def _log_path():
    try:
        base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if base:
            os.makedirs(base, exist_ok=True)
            return os.path.join(base, "media_downloader.log")
    except Exception:
        pass
    # fallback: current directory
    return os.path.abspath("media_downloader.log")


LOG_FILE = _log_path()


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        # last fallback: print
        print(line, end="")


def qt_message_handler(mode, context, message):
    # mode: QtMsgType (Debug/Info/Warning/Critical/Fatal)
    try:
        log(f"[Qt] {message}")
    except Exception:
        pass


def excepthook(exc_type, exc_value, exc_tb):
    # Log full traceback
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log("=== UNCAUGHT PYTHON EXCEPTION ===")
    log(tb)

    # Show error dialog if possible
    try:
        QMessageBox.critical(None, "Crash", f"Aplikasi error:\n{exc_value}\n\nLog: {LOG_FILE}")
    except Exception:
        pass

    # Call default hook
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    # Enable faulthandler for native crashes (segfault etc.)
    try:
        faulthandler.enable(all_threads=True)
        log("Faulthandler enabled.")
    except Exception as e:
        log(f"Faulthandler enable failed: {e}")

    # Capture Qt logs (warnings, etc.) to file
    try:
        qInstallMessageHandler(qt_message_handler)
        log("Qt message handler installed.")
    except Exception as e:
        log(f"Qt message handler install failed: {e}")

    # Capture uncaught Python exceptions to file + dialog
    sys.excepthook = excepthook
    log("App starting...")

    # High DPI attributes MUST be set before QApplication instance
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Media Downloader")
    app.setOrganizationName("MediaDownloader")

    # Import here so failures are logged
    try:
        from ui import MainWindow
        log("Imported ui.MainWindow successfully.")
    except Exception:
        tb = traceback.format_exc()
        log("=== ERROR IMPORTING ui ===")
        log(tb)
        QMessageBox.critical(None, "Import Error", f"Gagal import UI.\n\nLog: {LOG_FILE}")
        return

    window_holder = {"win": None}

    def start_ui():
        try:
            log("Creating MainWindow() ...")
            window_holder["win"] = MainWindow()
            window_holder["win"].show()
            log("MainWindow shown.")
        except Exception:
            tb = traceback.format_exc()
            log("=== ERROR CREATING/SHOWING MainWindow ===")
            log(tb)
            QMessageBox.critical(None, "Startup Error", f"Gagal membuka window.\n\nLog: {LOG_FILE}")
            app.quit()

    # Defer UI creation until event loop is ready (helps diagnose freezes)
    QTimer.singleShot(0, start_ui)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
