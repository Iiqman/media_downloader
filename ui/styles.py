"""
Stylesheet untuk aplikasi
Support: Dark Mode & Light Mode
"""


DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QPushButton {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    min-height: 40px;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
}

QPushButton:pressed {
    background-color: #252525;
}

QPushButton#platformButton {
    min-height: 120px;
    font-size: 14pt;
    background-color: #2d2d2d;
    border: 2px solid #3d3d3d;
}

QPushButton#platformButton:hover {
    background-color: #3d3d3d;
    border: 2px solid #0078d4;
}

QPushButton#primaryButton {
    background-color: #0078d4;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #1084d8;
}

QPushButton#dangerButton {
    background-color: #d13438;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #e13438;
}

QLineEdit, QComboBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 10px;
    font-size: 10pt;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #e0e0e0;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #ffffff;
    selection-background-color: #0078d4;
    border: 1px solid #3d3d3d;
}

QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    text-align: center;
    height: 30px;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 5px;
}

QLabel {
    background-color: transparent;
    color: #e0e0e0;
}

QLabel#titleLabel {
    font-size: 24pt;
    font-weight: bold;
    color: #ffffff;
}

QLabel#statusLabel {
    font-size: 11pt;
    color: #a0a0a0;
}

QScrollArea {
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    background-color: #252525;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4d4d4d;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QTabWidget::pane {
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    background-color: #1e1e1e;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #a0a0a0;
    border: 1px solid #3d3d3d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover {
    background-color: #3d3d3d;
}

QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #3d3d3d;
    border-radius: 4px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

QCheckBox::indicator:hover {
    border-color: #0078d4;
}

QGroupBox {
    border: 2px solid #3d3d3d;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #ffffff;
}
"""


LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    background-color: #f5f5f5;
    color: #202020;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QPushButton {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    min-height: 40px;
}

QPushButton:hover {
    background-color: #e8e8e8;
    border: 1px solid #b0b0b0;
}

QPushButton:pressed {
    background-color: #d0d0d0;
}

QPushButton#platformButton {
    min-height: 120px;
    font-size: 14pt;
    background-color: #ffffff;
    border: 2px solid #d0d0d0;
}

QPushButton#platformButton:hover {
    background-color: #f0f0f0;
    border: 2px solid #0078d4;
}

QPushButton#primaryButton {
    background-color: #0078d4;
    color: #ffffff;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #1084d8;
}

QPushButton#dangerButton {
    background-color: #d13438;
    color: #ffffff;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #e13438;
}

QLineEdit, QComboBox {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 10px;
    font-size: 10pt;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #202020;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #202020;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
    border: 1px solid #d0d0d0;
}

QProgressBar {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    text-align: center;
    height: 30px;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 5px;
}

QLabel {
    background-color: transparent;
    color: #202020;
}

QLabel#titleLabel {
    font-size: 24pt;
    font-weight: bold;
    color: #000000;
}

QLabel#statusLabel {
    font-size: 11pt;
    color: #606060;
}

QScrollArea {
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    background-color: #ffffff;
}

QScrollBar:vertical {
    background-color: #f0f0f0;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QTabWidget::pane {
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    background-color: #f5f5f5;
}

QTabBar::tab {
    background-color: #ffffff;
    color: #606060;
    border: 1px solid #d0d0d0;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #f5f5f5;
    color: #000000;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover {
    background-color: #e8e8e8;
}

QCheckBox {
    spacing: 8px;
    color: #202020;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #d0d0d0;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

QCheckBox::indicator:hover {
    border-color: #0078d4;
}

QGroupBox {
    border: 2px solid #d0d0d0;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #000000;
}
"""


def get_theme(theme_name='dark'):
    """Ambil stylesheet berdasarkan nama theme"""
    if theme_name.lower() == 'light':
        return LIGHT_THEME
    return DARK_THEME