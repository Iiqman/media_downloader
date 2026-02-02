"""
Settings Dialog - Dialog untuk pengaturan aplikasi
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFileDialog, QComboBox,
                             QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
    """Dialog untuk settings aplikasi"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Inisialisasi UI"""
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Download folder section
        folder_group = QGroupBox("Download Folder")
        folder_layout = QVBoxLayout(folder_group)
        
        folder_desc = QLabel("Pilih folder untuk menyimpan hasil download:")
        folder_desc.setWordWrap(True)
        folder_layout.addWidget(folder_desc)
        
        folder_input_layout = QHBoxLayout()
        
        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        folder_input_layout.addWidget(self.folder_input)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setMaximumWidth(100)
        browse_btn.clicked.connect(self.browse_folder)
        folder_input_layout.addWidget(browse_btn)
        
        folder_layout.addLayout(folder_input_layout)
        
        layout.addWidget(folder_group)
        
        # Theme section
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_desc = QLabel("Pilih tema aplikasi:")
        theme_layout.addWidget(theme_desc)
        
        theme_input_layout = QHBoxLayout()
        theme_input_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Dark', 'Light'])
        self.theme_combo.setMinimumWidth(150)
        theme_input_layout.addWidget(self.theme_combo)
        
        theme_input_layout.addStretch()
        theme_layout.addLayout(theme_input_layout)
        
        layout.addWidget(theme_group)
        
        # Default quality section
        quality_group = QGroupBox("Default Quality")
        quality_layout = QVBoxLayout(quality_group)
        
        video_layout = QHBoxLayout()
        video_layout.addWidget(QLabel("Video Quality:"))
        
        self.video_quality_combo = QComboBox()
        self.video_quality_combo.addItems(['1080p', '720p', '480p', '360p'])
        self.video_quality_combo.setMinimumWidth(150)
        video_layout.addWidget(self.video_quality_combo)
        
        video_layout.addStretch()
        quality_layout.addLayout(video_layout)
        
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel("Audio Quality:"))
        
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(['320kbps', '192kbps', '128kbps', '64kbps'])
        self.audio_quality_combo.setMinimumWidth(150)
        audio_layout.addWidget(self.audio_quality_combo)
        
        audio_layout.addStretch()
        quality_layout.addLayout(audio_layout)
        
        layout.addWidget(quality_group)
        
        layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMaximumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setObjectName("primaryButton")
        save_btn.setMaximumWidth(100)
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_settings(self):
        """Load settings saat ini"""
        self.folder_input.setText(self.config.get('download_folder'))
        
        theme = self.config.get('theme', 'dark')
        index = 0 if theme.lower() == 'dark' else 1
        self.theme_combo.setCurrentIndex(index)
        
        video_quality = self.config.get('default_quality', '720p')
        audio_quality = self.config.get('default_audio_quality', '192kbps')
        
        self.video_quality_combo.setCurrentText(video_quality)
        self.audio_quality_combo.setCurrentText(audio_quality)
    
    def browse_folder(self):
        """Browse folder untuk download"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Pilih Folder Download",
            self.folder_input.text()
        )
        
        if folder:
            self.folder_input.setText(folder)
    
    def save_settings(self):
        """Simpan settings"""
        # Validasi folder
        folder = self.folder_input.text()
        if not folder:
            QMessageBox.warning(self, "Error", "Pilih folder download terlebih dahulu!")
            return
        
        # Save ke config
        self.config.set('download_folder', folder)
        
        theme = 'dark' if self.theme_combo.currentIndex() == 0 else 'light'
        self.config.set('theme', theme)
        
        self.config.set('default_quality', self.video_quality_combo.currentText())
        self.config.set('default_audio_quality', self.audio_quality_combo.currentText())
        
        QMessageBox.information(self, "Success", "Settings berhasil disimpan!")
        self.accept()