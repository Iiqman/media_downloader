"""
Instagram Downloader Backend
Support: yt-dlp (primary), gallery-dl (fallback)
"""
import os
import json
import subprocess


class InstagramDownloader:
    def __init__(self):
        self.platform = "Instagram"
    
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
        
        url = f"https://www.instagram.com/{username}/"
        
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
                        'title': entry.get('title', 'Instagram Post'),
                        'thumbnail': entry.get('thumbnail'),
                        'url': entry.get('webpage_url') or entry.get('url'),
                        'type': 'video' if entry.get('duration') else 'photo'
                    })
            
            return {
                'username': username,
                'profile_pic': info.get('thumbnail'),
                'posts': posts
            }
    
    def _extract_user_posts_gallerydl(self, username):
        """Fallback: extract menggunakan gallery-dl"""
        try:
            url = f"https://www.instagram.com/{username}/"
            
            # Gunakan gallery-dl untuk extract info
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
                            'id': data.get('post_id'),
                            'title': data.get('description', 'Instagram Post')[:50],
                            'thumbnail': data.get('thumbnail') or data.get('url'),
                            'url': data.get('post_url'),
                            'type': data.get('type', 'photo')
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
    
    def extract_post_info(self, url):
        """Extract informasi dari single post"""
        try:
            return self._extract_post_info_ytdlp(url)
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return self._extract_post_info_gallerydl(url)
    
    def _extract_post_info_ytdlp(self, url):
        """Extract post info menggunakan yt-dlp"""
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Cek apakah galeri (multiple photos/videos)
            if 'entries' in info:
                items = []
                for entry in info['entries']:
                    if entry:
                        items.append({
                            'thumbnail': entry.get('thumbnail'),
                            'url': entry.get('url'),
                            'type': 'video' if entry.get('duration') else 'photo'
                        })
                
                return {
                    'type': 'gallery',
                    'title': info.get('title', 'Instagram Post'),
                    'thumbnail': info.get('thumbnail'),
                    'items': items,
                    'count': len(items)
                }
            else:
                return {
                    'type': 'video' if info.get('duration') else 'photo',
                    'title': info.get('title', 'Instagram Post'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                }
    
    def _extract_post_info_gallerydl(self, url):
        """Fallback: extract post info menggunakan gallery-dl"""
        try:
            result = subprocess.run(
                ['gallery-dl', '--dump-json', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"gallery-dl failed: {result.stderr}")
            
            items = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        items.append({
                            'thumbnail': data.get('thumbnail') or data.get('url'),
                            'url': data.get('url'),
                            'type': data.get('type', 'photo')
                        })
                    except:
                        pass
            
            if len(items) > 1:
                return {
                    'type': 'gallery',
                    'title': 'Instagram Gallery',
                    'thumbnail': items[0]['thumbnail'] if items else None,
                    'items': items,
                    'count': len(items)
                }
            elif items:
                return {
                    'type': items[0]['type'],
                    'title': 'Instagram Post',
                    'thumbnail': items[0]['thumbnail'],
                }
            else:
                raise Exception("No items found")
        
        except Exception as e:
            print(f"gallery-dl error: {e}")
            raise Exception(f"Failed to extract post info: {e}")
    
    def extract_story(self, username):
        """Extract story dari username (tanpa login)"""
        try:
            import yt_dlp
            
            url = f"https://www.instagram.com/stories/{username}/"
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                stories = []
                entries = info.get('entries', [])
                
                for entry in entries:
                    if entry:
                        stories.append({
                            'id': entry.get('id'),
                            'thumbnail': entry.get('thumbnail'),
                            'url': entry.get('url'),
                            'type': 'video' if entry.get('duration') else 'photo'
                        })
                
                return {
                    'username': username,
                    'stories': stories
                }
        
        except Exception as e:
            print(f"Failed to extract story: {e}")
            return {'username': username, 'stories': []}
    
    def download(self, url, output_path, progress_callback=None):
        """Download post (foto/video)"""
        try:
            return self._download_ytdlp(url, output_path, progress_callback)
        except Exception as e:
            print(f"yt-dlp download failed: {e}")
            return self._download_gallerydl(url, output_path, progress_callback)
    
    def _download_ytdlp(self, url, output_path, progress_callback):
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
            
            files = []
            
            # Cek apakah multiple files (galeri)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        filename = ydl.prepare_filename(entry)
                        files.append(filename)
            else:
                filename = ydl.prepare_filename(info)
                files.append(filename)
            
            return {
                'success': True,
                'files': files,
                'title': info.get('title', 'Instagram Post'),
                'thumbnail': info.get('thumbnail'),
                'count': len(files)
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
            
            # Parse output untuk mendapatkan files yang didownload
            files = []
            for line in result.stdout.split('\n'):
                if 'Downloading' in line or output_path in line:
                    # Extract filename dari output
                    pass
            
            return {
                'success': True,
                'files': files or ['downloaded'],
                'title': 'Instagram Post',
                'count': len(files) or 1
            }
        
        except Exception as e:
            raise Exception(f"Download failed: {e}")