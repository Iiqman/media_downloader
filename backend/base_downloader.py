import yt_dlp
from pathlib import Path
from abc import ABC, abstractmethod


class BaseDownloader(ABC):
    """Base class untuk semua downloader platform"""
    
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'retries': 3,  # Menambahkan retries untuk mencoba ulang jika gagal
            'socket_timeout': 10,  # Timeout untuk koneksi
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',  # User-Agent agar YouTube menganggap permintaan sah
        }
    
    @abstractmethod
    def get_platform_name(self):
        """Nama platform"""
        pass
    
    def extract_info(self, url, extract_flat=False):
        """Extract informasi dari URL tanpa download"""
        try:
            opts = self.ydl_opts.copy()
            opts['extract_flat'] = extract_flat
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            raise Exception(f"Error extracting info: {str(e)}")
    
    def get_formats(self, url):
        """Mendapatkan daftar format yang tersedia"""
        try:
            info = self.extract_info(url)
            return self._process_formats(info)
        except Exception as e:
            raise Exception(f"Error getting formats: {str(e)}")
    
    def _process_formats(self, info):
        """Memproses format dari info dict"""
        video_formats = []
        audio_formats = []
        
        if 'formats' in info:
            for fmt in info['formats']:
                # Video formats
                if fmt.get('vcodec') != 'none' and fmt.get('height'):
                    video_formats.append({
                        'format_id': fmt['format_id'],
                        'ext': fmt.get('ext', 'mp4'),
                        'quality': f"{fmt['height']}p",
                        'height': fmt['height'],
                        'filesize': fmt.get('filesize', 0),
                        'fps': fmt.get('fps', 30),
                    })
                
                # Audio formats
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    abr = fmt.get('abr', 0)
                    if abr:
                        audio_formats.append({
                            'format_id': fmt['format_id'],
                            'ext': fmt.get('ext', 'mp3'),
                            'quality': f"{int(abr)}kbps",
                            'abr': abr,
                            'filesize': fmt.get('filesize', 0),
                        })
        
        # Sort dan deduplikasi
        video_formats = self._deduplicate_formats(video_formats, 'height')
        audio_formats = self._deduplicate_formats(audio_formats, 'abr')
        
        return {
            'video': sorted(video_formats, key=lambda x: x['height'], reverse=True),
            'audio': sorted(audio_formats, key=lambda x: x['abr'], reverse=True),
            'thumbnail': info.get('thumbnail'),
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', 'Unknown'),
        }
    
    def _deduplicate_formats(self, formats, key):
        """Menghapus format duplikat berdasarkan key"""
        seen = set()
        unique = []
        for fmt in formats:
            if fmt[key] not in seen:
                seen.add(fmt[key])
                unique.append(fmt)
        return unique
    
    def download(self, url, output_path, format_id=None, download_type='video', progress_callback=None):
        """Download file dari URL"""
        try:
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = str(Path(output_path) / '%(title)s.%(ext)s')
            
            if download_type == 'audio':
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                if format_id:
                    opts['format'] = format_id
            else:
                if format_id:
                    opts['format'] = f"{format_id}+bestaudio/best"
                else:
                    opts['format'] = 'bestvideo+bestaudio/best'
                opts['merge_output_format'] = 'mp4'
            
            # Progress hook
            if progress_callback:
                opts['progress_hooks'] = [progress_callback]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Mendapatkan path file yang didownload
                filename = ydl.prepare_filename(info)
                if download_type == 'audio':
                    filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                return {
                    'success': True,
                    'filepath': filename,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_playlist_items(self, url):
        """Mendapatkan daftar item dalam playlist"""
        try:
            info = self.extract_info(url, extract_flat=True)
            
            if 'entries' not in info:
                return []
            
            items = []
            for entry in info['entries']:
                if entry:
                    items.append({
                        'id': entry.get('id'),
                        'title': entry.get('title', 'Unknown'),
                        'url': entry.get('url') or entry.get('webpage_url'),
                        'duration': entry.get('duration', 0),
                        'thumbnail': entry.get('thumbnail'),
                        'uploader': entry.get('uploader', 'Unknown'),
                    })
            
            return items
        except Exception as e:
            raise Exception(f"Error getting playlist: {str(e)}")
