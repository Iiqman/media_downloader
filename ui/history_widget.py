"""
History Widget - Menampilkan riwayat download
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QLabel, QPushButton, QFrame, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl
import os
from datetime import datetime

from utils import HistoryManager


class HistoryItemWidget(QFrame):
    """Widget untuk satu item history"""
    
    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.network_manager = QNetworkAccessManager()
        self.init_ui()
    
    def init_ui(self):
        """Inisialisasi UI"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMaximumHeight(150)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(120, 90)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setStyleSheet("border: 1px solid #3d3d3d; border-radius: 4px;")
        
        if self.entry.get('thumbnail'):
            self.load_thumbnail(self.entry['thumbnail'])
        else:
            self.thumbnail_label.setText("No\nPreview")
            self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.thumbnail_label)
        
        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Title
        title = self.entry.get('title', 'Unknown')
        if len(title) > 60:
            title = title[:60] + "..."
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)
        
        # Platform & Date
        platform = self.entry.get('platform', 'Unknown')
        timestamp = self.entry.get('timestamp', '')
        try:
            date_obj = datetime.fromisoformat(timestamp)
            date_str = date_obj.strftime("%d %b %Y, %H:%M")
        except:
            date_str = "Unknown date"
        
        meta_label = QLabel(f"📁 {platform} | 📅 {date_str}")
        meta_label.setStyleSheet("color: gray; font-size: 9pt;")
        info_layout.addWidget(meta_label)
        
        # Duration / Item count
        details = []
        if self.entry.get('duration'):
            duration = self.entry['duration']
            minutes = duration // 60
            seconds = duration % 60
            details.append(f"⏱️ {minutes}:{seconds:02d}")
        
        item_count = self.entry.get('item_count', 1)
        if item_count > 1:
            details.append(f"📦 {item_count} items")
        
        if self.entry.get('quality'):
            details.append(f"🎥 {self.entry['quality']}")
        
        if details:
            details_label = QLabel(" | ".join(details))
            details_label.setStyleSheet("font-size: 9pt;")
            info_layout.addWidget(details_label)
        
        info_layout.addStretch()
        
        layout.addLayout(info_layout, 1)
        
        # Actions
        actions_layout = QVBoxLayout()
        
        open_btn = QPushButton("📂 Open")
        open_btn.setMaximumWidth(100)
        open_btn.clicked.connect(self.open_file)
        actions_layout.addWidget(open_btn)
        
        open_folder_btn = QPushButton("📁 Folder")
        open_folder_btn.setMaximumWidth(100)
        open_folder_btn.clicked.connect(self.open_folder)
        actions_layout.addWidget(open_folder_btn)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
    
    def load_thumbnail(self, url):
        """Load thumbnail dari URL"""
        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.on_thumbnail_loaded(reply))
    
    def on_thumbnail_loaded(self, reply):
        """Handler ketika thumbnail selesai diload"""
        if reply.error() == reply.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            scaled_pixmap = pixmap.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumbnail_label.setPixmap(scaled_pixmap)
        reply.deleteLater()
    
    def open_file(self):
        """Buka file yang didownload"""
        file_path = self.entry.get('file_path', '')
        if file_path and os.path.exists(file_path):
            os.startfile(file_path) if os.name == 'nt' else os.system(f'xdg-open "{file_path}"')
        else:
            QMessageBox.warning(self, "Error", "File tidak ditemukan")
    
    def open_folder(self):
        """Buka folder tempat file disimpan"""
        file_path = self.entry.get('file_path', '')
        if file_path:
            folder = os.path.dirname(file_path)
            if os.path.exists(folder):
                os.startfile(folder) if os.name == 'nt' else os.system(f'xdg-open "{folder}"')
            else:
                QMessageBox.warning(self, "Error", "Folder tidak ditemukan")


class HistoryWidget(QWidget):
    """Widget utama untuk history"""
    
    def __init__(self):
        super().__init__()
        self.history = HistoryManager()
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """Inisialisasi UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📜 Download History")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setMaximumWidth(120)
        self.refresh_btn.clicked.connect(self.refresh_history)
        header_layout.addWidget(self.refresh_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.setMaximumWidth(120)
        self.clear_btn.clicked.connect(self.clear_history)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Scroll area untuk history items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setSpacing(10)
        self.history_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.history_container)
        layout.addWidget(scroll)
    
    def load_history(self):
        """Load dan tampilkan history"""
        # Clear existing items
        while self.history_layout.count():
            child = self.history_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get history
        entries = self.history.get_history(50)  # Limit 50 items
        
        if not entries:
            empty_label = QLabel("Belum ada riwayat download")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 12pt; color: gray; padding: 50px;")
            self.history_layout.addWidget(empty_label)
        else:
            for entry in entries:
                item_widget = HistoryItemWidget(entry)
                self.history_layout.addWidget(item_widget)
        
        self.history_layout.addStretch()
    
    def refresh_history(self):
        """Refresh history display"""
        self.history = HistoryManager()  # Reload from file
        self.load_history()
    
    def clear_history(self):
        """Clear semua history"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Hapus semua riwayat download?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history.clear_history()
            self.load_history()