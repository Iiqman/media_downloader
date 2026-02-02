"""
Simple Launcher - No debug output
"""
import sys
import os

# Suppress debug output
os.environ['QT_LOGGING_RULES'] = '*.debug=false'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui import MainWindow

if __name__ == '__main__':
    # High DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create app
    app = QApplication(sys.argv)
    app.setApplicationName("Media Downloader")
    
    # Create and show window
    window = MainWindow()
    window.show()
    
    # Run
    sys.exit(app.exec_())