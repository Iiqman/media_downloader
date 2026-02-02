"""
Configuration Manager
Mengelola pengaturan aplikasi (folder download, preferensi)
"""
import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_file = Path.home() / ".media_downloader" / "config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.config = self.load_config()
    
    def load_config(self):
        """Load konfigurasi dari file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default config
        return {
            'download_folder': str(Path.home() / "Downloads" / "MediaDownloader"),
            'theme': 'dark',
            'default_quality': '720p',
            'default_audio_quality': '192kbps'
        }
    
    def save_config(self):
        """Simpan konfigurasi ke file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Ambil nilai konfigurasi"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set nilai konfigurasi"""
        self.config[key] = value
        self.save_config()
    
    def get_download_folder(self):
        """Ambil folder download dan buat jika belum ada"""
        folder = self.config.get('download_folder')
        Path(folder).mkdir(parents=True, exist_ok=True)
        return folder