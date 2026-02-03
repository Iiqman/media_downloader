"""
Main Window - UI Utama Aplikasi (Responsive v2)
- Platform chooser auto-collapse after selection
- Button "Ganti Platform" to show chooser again
- Grid reflow on resize
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QTabWidget,
    QGridLayout, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt

from .platform_widget import PlatformWidget
from .history_widget import HistoryWidget
from .settings_dialog import SettingsDialog
from .styles import get_theme
from utils import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

        self._platform_cols = None
        self._platform_order = []
        self._current_platform = None

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("Media Downloader - Multi Platform")
        self.setMinimumSize(900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🎬 Media Downloader")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setMaximumWidth(150)
        self.settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(self.settings_btn)

        main_layout.addLayout(header_layout)

        # Tabs
        self.tab_widget = QTabWidget()

        # ----------------------------
        # Download tab
        # ----------------------------
        self.download_widget = QWidget()
        download_layout = QVBoxLayout(self.download_widget)
        download_layout.setSpacing(12)

        # Platform header row
        platform_header = QHBoxLayout()
        self.platform_label = QLabel("Pilih Platform:")
        self.platform_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        platform_header.addWidget(self.platform_label)
        platform_header.addStretch()

        self.change_platform_btn = QPushButton("🔁 Ganti Platform")
        self.change_platform_btn.setVisible(False)
        self.change_platform_btn.clicked.connect(self.show_platform_chooser)
        platform_header.addWidget(self.change_platform_btn)

        download_layout.addLayout(platform_header)

        platforms = [
            ("YouTube", "🎥"),
            ("Instagram", "📷"),
            ("TikTok", "🎵"),
            ("Facebook", "📘")
        ]
        self._platform_order = [p[0] for p in platforms]

        # Platform chooser container (GRID)
        self.platform_buttons_container = QWidget()
        self.platform_buttons_grid = QGridLayout(self.platform_buttons_container)
        self.platform_buttons_grid.setSpacing(15)
        self.platform_buttons_grid.setContentsMargins(0, 0, 0, 0)
        download_layout.addWidget(self.platform_buttons_container)

        self.platform_buttons = {}
        for platform_name, icon in platforms:
            btn = QPushButton(f"{icon}\n{platform_name}")
            btn.setObjectName("platformButton")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.clicked.connect(lambda checked, p=platform_name: self.select_platform(p))
            self.platform_buttons[platform_name] = btn

        # Stacked pages
        self.stacked_widget = QStackedWidget()

        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_label = QLabel("👆 Pilih platform di atas untuk memulai")
        welcome_label.setStyleSheet("font-size: 16pt; color: gray;")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        self.stacked_widget.addWidget(welcome_widget)

        self.platform_widgets = {}
        self.platform_pages = {}

        for platform_name, _ in platforms:
            widget = PlatformWidget(platform_name, self.config)
            widget.download_complete.connect(self.on_download_complete)
            self.platform_widgets[platform_name] = widget

            page_scroll = QScrollArea()
            page_scroll.setWidgetResizable(True)
            page_scroll.setFrameShape(QScrollArea.NoFrame)
            page_scroll.setObjectName("pageScrollArea")
            page_scroll.setWidget(widget)

            self.platform_pages[platform_name] = page_scroll
            self.stacked_widget.addWidget(page_scroll)

        download_layout.addWidget(self.stacked_widget, 1)

        self.tab_widget.addTab(self.download_widget, "📥 Download")

        # ----------------------------
        # History tab
        # ----------------------------
        self.history_widget = HistoryWidget()
        self.tab_widget.addTab(self.history_widget, "📜 History")

        main_layout.addWidget(self.tab_widget, 1)
        self.statusBar().showMessage("Ready")

        self._relayout_platform_buttons(force=True)

    # ----------------------------
    # Responsive: platform grid
    # ----------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout_platform_buttons()

    def _calc_platform_cols(self) -> int:
        w = self.download_widget.width()
        if w >= 980:
            return 4
        if w >= 700:
            return 2
        return 1

    def _clear_grid(self, grid: QGridLayout):
        while grid.count():
            item = grid.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)

    def _relayout_platform_buttons(self, force: bool = False):
        cols = self._calc_platform_cols()
        if (not force) and (cols == self._platform_cols):
            return
        self._platform_cols = cols

        self._clear_grid(self.platform_buttons_grid)
        for idx, name in enumerate(self._platform_order):
            btn = self.platform_buttons[name]
            r = idx // cols
            c = idx % cols
            self.platform_buttons_grid.addWidget(btn, r, c)

        for c in range(cols):
            self.platform_buttons_grid.setColumnStretch(c, 1)

    # ----------------------------
    # Actions
    # ----------------------------
    def select_platform(self, platform_name):
        self._current_platform = platform_name

        # highlight
        for name, btn in self.platform_buttons.items():
            if name == platform_name:
                btn.setStyleSheet("border: 3px solid #0078d4;")
            else:
                btn.setStyleSheet("")

        # show page
        self.stacked_widget.setCurrentWidget(self.platform_pages[platform_name])
        self.statusBar().showMessage(f"Platform: {platform_name}")

        # collapse chooser supaya tidak makan tempat (ini yang bikin “kepotong” saat window kecil)
        self.platform_buttons_container.setVisible(False)
        self.change_platform_btn.setVisible(True)
        self.platform_label.setText(f"Platform: {platform_name}")

    def show_platform_chooser(self):
        # tampilkan kembali pilihan platform
        self.platform_buttons_container.setVisible(True)
        self.change_platform_btn.setVisible(False)
        self.platform_label.setText("Pilih Platform:")
        self.statusBar().showMessage("Ready")

    def show_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            self.apply_theme()

    def apply_theme(self):
        theme = self.config.get("theme", "dark")
        stylesheet = get_theme(theme)
        self.setStyleSheet(stylesheet)

    def on_download_complete(self, data):
        if isinstance(data, dict):
            self.statusBar().showMessage(f"Download selesai: {data.get('title', 'Unknown')}", 5000)
        else:
            self.statusBar().showMessage("Download selesai", 5000)

        self.history_widget.refresh_history()
