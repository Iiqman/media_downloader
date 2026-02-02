"""
History Manager
Mengelola riwayat download
"""
import json
from pathlib import Path
from datetime import datetime


class HistoryManager:
    def __init__(self):
        self.history_file = Path.home() / ".media_downloader" / "history.json"
        self.history_file.parent.mkdir(exist_ok=True)
        self.history = self.load_history()
    
    def load_history(self):
        """Load histori dari file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_history(self):
        """Simpan histori ke file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def add_entry(self, platform, title, url, file_path, thumbnail=None, 
                  duration=None, item_count=1, quality=None):
        """Tambah entry baru ke histori"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform,
            'title': title,
            'url': url,
            'file_path': file_path,
            'thumbnail': thumbnail,
            'duration': duration,
            'item_count': item_count,
            'quality': quality
        }
        self.history.insert(0, entry)  # Tambah di awal
        
        # Batasi histori maksimal 100 item
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        self.save_history()
    
    def get_history(self, limit=None):
        """Ambil histori"""
        if limit:
            return self.history[:limit]
        return self.history
    
    def clear_history(self):
        """Hapus semua histori"""
        self.history = []
        self.save_history()