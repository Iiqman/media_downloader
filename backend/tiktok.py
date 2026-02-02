"""
TikTok Downloader Backend
Support: yt-dlp (primary), gallery-dl (fallback)
"""
import os
import json
import subprocess


class TikTokDownloader:
    def __init__(self):
        self.platform = "TikTok"
    
    def extract_user_posts(self, username):
        """Extract posts dari username"""
        try:
            return self._extract_user_posts_ytdlp(username)
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return self._extract_user_posts_gallerydl(username)
    
    def _extract_user_posts_ytdlp(self, username):
        """Extract menggunakan yt-dlp"""
        import yt_dlp
        
        # TikTok user URL format
        url = f"https://www.tiktok.com/@{username}"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            posts = []
            entries = info.get('entries', [])
            
            for entry in entries[:20]:  # Limit 20 posts
                if entry:
                    posts.append({
                        'id': entry.get('id'),
                        'title': entry.get('title', 'TikTok Video')[:50],
                        'thumbnail': entry.get('thumbnail'),
                        'url': entry.get('webpage_url') or entry.get('url'),
                        'duration': entry.get('duration')
                    })
            
            return {
                'username': username,
                'profile_pic': info.get('thumbnail'),
                'posts': posts
            }
    
    def _extract_user_posts_gallerydl(self, username):
        """Fallback: extract menggunakan gallery-dl"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            
            result = subprocess.run(
                ['gallery-dl', '--dump-json', '--range', '1-20', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"gallery-dl failed: {result.stderr}")
            
            posts = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        posts.append({
                            'id': data.get('id'),
                            'title': data.get('description', 'TikTok Video')[:50],
                            'thumbnail': data.get('thumbnail'),
                            'url': f"https://www.tiktok.com/@{username}/video/{data.get('id')}",
                            'duration': data.get('duration')
                        })
                    except:
                        pass
            
            return {
                'username': username,
                'profile_pic': None,
                'posts': posts
            }
        
        except Exception as e:
            print(f"gallery-dl error: {e}")
            raise Exception(f"Failed to extract user posts: {e}")
    
    def extract_video_info(self, url):
        """Extract informasi dari single video"""
        try:
            return self._extract_video_info_ytdlp(url)
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return self._extract_video_info_gallerydl(url)
    
    def _extract_video_info_ytdlp(self, url):
        """Extract video info menggunakan yt-dlp"""
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'type': 'video',
                'title': info.get('title', 'TikTok Video'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'author': info.get('uploader'),
            }
    
    def _extract_video_info_gallerydl(self, url):
        """Fallback: extract video info menggunakan gallery-dl"""
        try:
            result = subprocess.run(
                ['gallery-dl', '--dump-json', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"gallery-dl failed: {result.stderr}")
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        return {
                            'type': 'video',
                            'title': data.get('description', 'TikTok Video')[:50],
                            'thumbnail': data.get('thumbnail'),
                            'duration': data.get('duration'),
                            'author': data.get('author', {}).get('nickname'),
                        }
                    except:
                        pass
            
            raise Exception("Failed to parse video info")
        
        except Exception as e:
            print(f"gallery-dl error: {e}")
            raise Exception(f"Failed to extract video info: {e}")
    
    def download(self, url, output_path, quality='best', progress_callback=None):
        """Download video"""
        try:
            return self._download_ytdlp(url, output_path, quality, progress_callback)
        except Exception as e:
            print(f"yt-dlp download failed: {e}")
            return self._download_gallerydl(url, output_path, progress_callback)
    
    def _download_ytdlp(self, url, output_path, quality, progress_callback):
        """Download menggunakan yt-dlp"""
        import yt_dlp
        
        output_template = os.path.join(output_path, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'outtmpl': output_template,
            'format': 'best',
        }
        
        if progress_callback:
            ydl_opts['progress_hooks'] = [progress_callback]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            return {
                'success': True,
                'file_path': filename,
                'title': info.get('title', 'TikTok Video'),
                'thumbnail': info.get('thumbnail')
            }
    
    def _download_gallerydl(self, url, output_path, progress_callback):
        """Fallback: download menggunakan gallery-dl"""
        try:
            result = subprocess.run(
                ['gallery-dl', '--destination', output_path, url],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise Exception(f"gallery-dl failed: {result.stderr}")
            
            return {
                'success': True,
                'file_path': output_path,
                'title': 'TikTok Video',
            }
        
        except Exception as e:
            raise Exception(f"Download failed: {e}")