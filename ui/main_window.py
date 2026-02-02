"""
Main Window - UI Utama Aplikasi
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from .platform_widget import PlatformWidget
from .history_widget import HistoryWidget
from .settings_dialog import SettingsDialog
from .styles import get_theme
from utils import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        """Inisialisasi UI"""
        self.setWindowTitle("Media Downloader - Multi Platform")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🎬 Media Downloader")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Settings button
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setMaximumWidth(150)
        self.settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Download tab
        self.download_widget = QWidget()
        download_layout = QVBoxLayout(self.download_widget)
        download_layout.setSpacing(15)
        
        # Platform selection
        platform_label = QLabel("Pilih Platform:")
        platform_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        download_layout.addWidget(platform_label)
        
        # Platform buttons
        platform_buttons_layout = QHBoxLayout()
        platform_buttons_layout.setSpacing(15)
        
        platforms = [
            ("YouTube", "🎥"),
            ("Instagram", "📷"),
            ("TikTok", "🎵"),
            ("Facebook", "📘")
        ]
        
        self.platform_buttons = {}
        for platform_name, icon in platforms:
            btn = QPushButton(f"{icon}\n{platform_name}")
            btn.setObjectName("platformButton")
            btn.clicked.connect(lambda checked, p=platform_name: self.select_platform(p))
            self.platform_buttons[platform_name] = btn
            platform_buttons_layout.addWidget(btn)
        
        download_layout.addLayout(platform_buttons_layout)
        
        # Stacked widget untuk platform-specific content
        self.stacked_widget = QStackedWidget()
        
        # Welcome page (default)
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_label = QLabel("👆 Pilih platform di atas untuk memulai")
        welcome_label.setStyleSheet("font-size: 16pt; color: gray;")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        self.stacked_widget.addWidget(welcome_widget)
        
        # Platform widgets
        self.platform_widgets = {}
        for platform_name, _ in platforms:
            widget = PlatformWidget(platform_name, self.config)
            widget.download_complete.connect(self.on_download_complete)
            self.platform_widgets[platform_name] = widget
            self.stacked_widget.addWidget(widget)
        
        download_layout.addWidget(self.stacked_widget)
        
        self.tab_widget.addTab(self.download_widget, "📥 Download")
        
        # History tab
        self.history_widget = HistoryWidget()
        self.tab_widget.addTab(self.history_widget, "📜 History")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def select_platform(self, platform_name):
        """Pilih platform dan tampilkan widget yang sesuai"""
        # Highlight button yang dipilih
        for name, btn in self.platform_buttons.items():
            if name == platform_name:
                btn.setStyleSheet("border: 3px solid #0078d4;")
            else:
                btn.setStyleSheet("")
        
        # Tampilkan widget platform
        widget = self.platform_widgets[platform_name]
        self.stacked_widget.setCurrentWidget(widget)
        
        self.statusBar().showMessage(f"Platform: {platform_name}")
    
    def show_settings(self):
        """Tampilkan dialog settings"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            # Apply theme jika berubah
            self.apply_theme()
    
    def apply_theme(self):
        """Apply theme ke aplikasi"""
        theme = self.config.get('theme', 'dark')
        stylesheet = get_theme(theme)
        self.setStyleSheet(stylesheet)
    
    def on_download_complete(self, data):
        """Handler ketika download selesai"""
        self.statusBar().showMessage(f"Download selesai: {data.get('title', 'Unknown')}", 5000)
        
        # Refresh history
        self.history_widget.refresh_history()