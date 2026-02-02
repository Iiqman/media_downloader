DARK_THEME = """
QMainWindow {
    background-color: #1e1e2e;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton:disabled {
    background-color: #1e1e2e;
    color: #6c7086;
    border-color: #313244;
}

QPushButton#platformButton {
    min-height: 120px;
    font-size: 16px;
    background-color: #313244;
    border: 3px solid #45475a;
}

QPushButton#platformButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}

QPushButton#downloadButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    min-height: 45px;
    font-size: 15px;
}

QPushButton#downloadButton:hover {
    background-color: #74c7ec;
}

QPushButton#downloadButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
}

QLineEdit:focus {
    border-color: #89b4fa;
}

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 6px;
    padding: 8px;
    min-height: 30px;
}

QComboBox:hover {
    border-color: #585b70;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border: 2px solid #cdd6f4;
    width: 8px;
    height: 8px;
    border-left: none;
    border-top: none;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    border: 2px solid #45475a;
}

QProgressBar {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 6px;
    text-align: center;
    color: #cdd6f4;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 4px;
}

QLabel {
    color: #cdd6f4;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #89b4fa;
}

QLabel#statusLabel {
    font-size: 13px;
    color: #a6adc8;
    background-color: #313244;
    padding: 8px;
    border-radius: 4px;
}

QTabWidget::pane {
    border: 2px solid #45475a;
    border-radius: 8px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 10px 20px;
    border: 2px solid #45475a;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #45475a;
    border-color: #89b4fa;
    color: #89b4fa;
}

QTabBar::tab:hover {
    background-color: #45475a;
}

QScrollArea {
    border: none;
    background-color: #1e1e2e;
}

QScrollBar:vertical {
    background-color: #313244;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #313244;
}

QCheckBox::indicator:hover {
    border-color: #89b4fa;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QGroupBox {
    border: 2px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
    color: #cdd6f4;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #89b4fa;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #ffffff;
}

QWidget {
    background-color: #ffffff;
    color: #2c3e50;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

QPushButton {
    background-color: #f8f9fa;
    color: #2c3e50;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #e9ecef;
    border-color: #adb5bd;
}

QPushButton:pressed {
    background-color: #dee2e6;
}

QPushButton:disabled {
    background-color: #f8f9fa;
    color: #adb5bd;
    border-color: #dee2e6;
}

QPushButton#platformButton {
    min-height: 120px;
    font-size: 16px;
    background-color: #f8f9fa;
    border: 3px solid #dee2e6;
}

QPushButton#platformButton:hover {
    background-color: #e9ecef;
    border-color: #0d6efd;
}

QPushButton#downloadButton {
    background-color: #0d6efd;
    color: #ffffff;
    border: none;
    min-height: 45px;
    font-size: 15px;
}

QPushButton#downloadButton:hover {
    background-color: #0b5ed7;
}

QPushButton#downloadButton:disabled {
    background-color: #6c757d;
    color: #dee2e6;
}

QLineEdit {
    background-color: #f8f9fa;
    color: #2c3e50;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
}

QLineEdit:focus {
    border-color: #0d6efd;
}

QComboBox {
    background-color: #f8f9fa;
    color: #2c3e50;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    padding: 8px;
    min-height: 30px;
}

QComboBox:hover {
    border-color: #adb5bd;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border: 2px solid #2c3e50;
    width: 8px;
    height: 8px;
    border-left: none;
    border-top: none;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #2c3e50;
    selection-background-color: #e9ecef;
    border: 2px solid #dee2e6;
}

QProgressBar {
    background-color: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    text-align: center;
    color: #2c3e50;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #0d6efd;
    border-radius: 4px;
}

QLabel {
    color: #2c3e50;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #0d6efd;
}

QLabel#statusLabel {
    font-size: 13px;
    color: #6c757d;
    background-color: #f8f9fa;
    padding: 8px;
    border-radius: 4px;
}

QTabWidget::pane {
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f8f9fa;
    color: #2c3e50;
    padding: 10px 20px;
    border: 2px solid #dee2e6;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-color: #0d6efd;
    color: #0d6efd;
}

QTabBar::tab:hover {
    background-color: #e9ecef;
}

QScrollArea {
    border: none;
    background-color: #ffffff;
}

QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #dee2e6;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #adb5bd;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QCheckBox {
    color: #2c3e50;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #dee2e6;
    border-radius: 4px;
    background-color: #f8f9fa;
}

QCheckBox::indicator:hover {
    border-color: #0d6efd;
}

QCheckBox::indicator:checked {
    background-color: #0d6efd;
    border-color: #0d6efd;
}

QGroupBox {
    border: 2px solid #dee2e6;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
    color: #2c3e50;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #0d6efd;
}
"""


def get_theme(theme_name):
    """Mendapatkan stylesheet berdasarkan nama tema"""
    if theme_name == 'dark':
        return DARK_THEME
    return LIGHT_THEME