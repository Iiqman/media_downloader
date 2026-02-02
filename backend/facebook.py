"""
Facebook Downloader Backend
Support: yt-dlp (primary), you-get (fallback)
"""
import os
import subprocess
import re


class FacebookDownloader:
    def __init__(self):
        self.platform = "Facebook"
    
    def extract_video_info(self, url):
        """Extract informasi video"""
        try:
            return self._extract_video_info_ytdlp(url)
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return self._extract_video_info_youget(url)
    
    def _extract_video_info_ytdlp(self, url):
        """Extract menggunakan yt-dlp"""
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'type': 'video',
                'title': info.get('title', 'Facebook Video'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'formats': self._get_available_formats(info)
            }
    
    def _extract_video_info_youget(self, url):
        """Fallback: extract menggunakan you-get"""
        try:
            result = subprocess.run(
                ['you-get', '--json', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"you-get failed: {result.stderr}")
            
            # Parse JSON output dari you-get
            import json
            data = json.loads(result.stdout)
            
            return {
                'type': 'video',
                'title': data.get('title', 'Facebook Video'),
                'thumbnail': data.get('thumbnail'),
                'duration': None,
                'formats': {
                    'video': ['720p', '480p', '360p'],
                    'audio': ['128kbps']
                }
            }
        
        except Exception as e:
            print(f"you-get error: {e}")
            # Return default
            return {
                'type': 'video',
                'title': 'Facebook Video',
                'thumbnail': None,
                'duration': None,
                'formats': {
                    'video': ['720p', '480p', '360p'],
                    'audio': ['128kbps']
                }
            }
    
    def _get_available_formats(self, info):
        """Ambil format video yang tersedia"""
        formats = {
            'video': [],
            'audio': []
        }
        
        for fmt in info.get('formats', []):
            if fmt.get('vcodec') != 'none':
                height = fmt.get('height')
                if height:
                    label = f"{height}p"
                    if label not in formats['video']:
                        formats['video'].append(label)
            
            if fmt.get('acodec') != 'none':
                abr = fmt.get('abr')
                if abr:
                    label = f"{int(abr)}kbps"
                    if label not in formats['audio']:
                        formats['audio'].append(label)
        
        # Sort
        if formats['video']:
            formats['video'].sort(key=lambda x: int(x.replace('p', '')), reverse=True)
        else:
            formats['video'] = ['720p', '480p', '360p']
        
        if formats['audio']:
            formats['audio'].sort(key=lambda x: int(x.replace('kbps', '')), reverse=True)
        else:
            formats['audio'] = ['128kbps', '64kbps']
        
        return formats
    
    def download(self, url, output_path, quality='720p', download_type='video',
                 progress_callback=None):
        """Download video/audio"""
        try:
            return self._download_ytdlp(url, output_path, quality, download_type, progress_callback)
        except Exception as e:
            print(f"yt-dlp download failed: {e}")
            return self._download_youget(url, output_path, progress_callback)
    
    def _download_ytdlp(self, url, output_path, quality, download_type, progress_callback):
        """Download menggunakan yt-dlp"""
        import yt_dlp
        
        output_template = os.path.join(output_path, '%(title)s.%(ext)s')
        
        if download_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality.replace('kbps', ''),
                }],
            }
        else:
            # Video
            format_str = f'best[height<={quality.replace("p", "")}]'
            ydl_opts = {
                'format': format_str,
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
            }
        
        if progress_callback:
            ydl_opts['progress_hooks'] = [progress_callback]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if download_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return {
                'success': True,
                'file_path': filename,
                'title': info.get('title', 'Facebook Video'),
                'thumbnail': info.get('thumbnail')
            }
    
    def _download_youget(self, url, output_path, progress_callback):
        """Fallback: download menggunakan you-get"""
        try:
            result = subprocess.run(
                ['you-get', '-o', output_path, url],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"you-get failed: {result.stderr}")
            
            # Parse output untuk mendapatkan filename
            filename = None
            for line in result.stdout.split('\n'):
                if 'Saving' in line or output_path in line:
                    match = re.search(r'Saving to: (.+)', line)
                    if match:
                        filename = match.group(1)
                        break
            
            if not filename:
                filename = os.path.join(output_path, 'facebook_video.mp4')
            
            return {
                'success': True,
                'file_path': filename,
                'title': 'Facebook Video',
            }
        
        except Exception as e:
            raise Exception(f"Download failed: {e}")