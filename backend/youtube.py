"""
YouTube Downloader Backend
Support: pytube (primary), yt-dlp (fallback)
"""
import os
import subprocess
from pathlib import Path


class YouTubeDownloader:
    def __init__(self):
        self.platform = "YouTube"
    
    def extract_info(self, url):
        """Extract informasi video menggunakan pytube (primary)"""
        try:
            return self._extract_info_pytube(url)
        except Exception as e:
            print(f"pytube error: {e}, trying yt-dlp...")
            # Fallback ke yt-dlp
            return self._extract_info_ytdlp(url)
    
    def _extract_info_pytube(self, url):
        """Extract info menggunakan pytube - PRIMARY METHOD"""
        try:
            from pytube import YouTube, Playlist
        except ImportError:
            raise Exception("pytube not installed. Install with: pip install pytube")
        
        try:
            # Cek apakah playlist
            if 'playlist' in url.lower() or '/playlist?' in url:
                try:
                    playlist = Playlist(url)
                    videos = []
                    for video_url in playlist.video_urls[:20]:  # Limit 20 video
                        try:
                            yt = YouTube(video_url)
                            videos.append({
                                'id': yt.video_id,
                                'title': yt.title,
                                'thumbnail': yt.thumbnail_url,
                                'duration': yt.length,
                                'channel': yt.author,
                                'url': video_url
                            })
                        except:
                            pass
                    
                    return {
                        'type': 'playlist',
                        'title': playlist.title or 'Playlist',
                        'videos': videos,
                        'thumbnail': videos[0]['thumbnail'] if videos else None
                    }
                except:
                    pass
            
            # Single video
            yt = YouTube(url)
            
            # Get available formats/qualities
            formats = self._get_pytube_formats(yt)
            
            return {
                'type': 'video',
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'duration': yt.length,
                'channel': yt.author,
                'view_count': yt.views,
                'formats': formats,
                'description': yt.description[:200] if yt.description else ''
            }
        
        except Exception as e:
            raise Exception(f"pytube extraction failed: {str(e)}")
    
    def _extract_info_ytdlp(self, url):
        """Fallback: Extract menggunakan yt-dlp"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Cek apakah playlist
                if 'entries' in info:
                    # Playlist
                    videos = []
                    for entry in info['entries']:
                        if entry:
                            videos.append({
                                'id': entry.get('id'),
                                'title': entry.get('title', 'Unknown'),
                                'thumbnail': entry.get('thumbnail'),
                                'duration': entry.get('duration'),
                                'channel': entry.get('uploader', 'Unknown'),
                                'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            })
                    
                    return {
                        'type': 'playlist',
                        'title': info.get('title', 'Playlist'),
                        'videos': videos,
                        'thumbnail': info.get('thumbnail')
                    }
                else:
                    # Single video
                    return {
                        'type': 'video',
                        'title': info.get('title', 'Unknown'),
                        'thumbnail': info.get('thumbnail'),
                        'duration': info.get('duration'),
                        'channel': info.get('uploader', 'Unknown'),
                        'view_count': info.get('view_count', 0),
                        'formats': self._get_available_formats(info)
                    }
        
        except Exception as e:
            print(f"yt-dlp error: {e}")
            raise Exception(f"Failed to extract info: {e}")
    
    def _get_pytube_formats(self, yt):
        """Ambil format dari pytube - semua resolusi"""
        formats = {
            'video': [],
            'audio': ['128kbps']
        }
        
        # Get all progressive streams (video+audio)
        progressive_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        
        for stream in progressive_streams:
            if stream.resolution and stream.resolution not in formats['video']:
                formats['video'].append(stream.resolution)
        
        # Jika tidak ada progressive, get adaptive video streams
        if not formats['video']:
            video_streams = yt.streams.filter(adaptive=True, type='video').order_by('resolution').desc()
            for stream in video_streams:
                if stream.resolution and stream.resolution not in formats['video']:
                    formats['video'].append(stream.resolution)
        
        # Default jika kosong
        if not formats['video']:
            formats['video'] = ['720p', '480p', '360p']
        
        return formats
    
    def _get_available_formats(self, info):
        """Ambil format video dan audio yang tersedia dari yt-dlp"""
        formats = {
            'video': [],
            'audio': []
        }
        
        for fmt in info.get('formats', []):
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                # Video dengan audio
                height = fmt.get('height')
                if height:
                    label = f"{height}p"
                    if label not in formats['video']:
                        formats['video'].append(label)
            elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                # Audio only
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
            formats['audio'] = ['320kbps', '192kbps', '128kbps', '64kbps']
        
        return formats
    
    def download(self, url, output_path, quality='720p', download_type='video', 
                 progress_callback=None, start_time=None, end_time=None):
        """Download video/audio - pytube primary"""
        try:
            result = self._download_pytube(url, output_path, quality, download_type, progress_callback)
            
            # Jika ada trim request, cut video
            if start_time is not None or end_time is not None:
                result = self._trim_video(result['file_path'], start_time, end_time, output_path)
            
            return result
        except Exception as e:
            print(f"pytube download failed: {e}, trying yt-dlp...")
            # Fallback ke yt-dlp
            return self._download_ytdlp(url, output_path, quality, download_type, progress_callback)
    
    def _download_pytube(self, url, output_path, quality, download_type, progress_callback):
        """Download menggunakan pytube - PRIMARY METHOD"""
        try:
            from pytube import YouTube
        except ImportError:
            raise Exception("pytube not installed. Please install: pip install pytube")
        
        try:
            yt = YouTube(url)
            
            if download_type == 'audio':
                # Audio only
                stream = yt.streams.filter(only_audio=True).first()
                if not stream:
                    stream = yt.streams.get_audio_only()
                
                filename = stream.download(output_path=output_path)
                
                # Convert to mp3 menggunakan ffmpeg
                mp3_file = os.path.splitext(filename)[0] + '.mp3'
                try:
                    subprocess.run(['ffmpeg', '-i', filename, '-vn', '-ar', '44100', 
                                  '-ac', '2', '-b:a', '192k', 
                                  mp3_file, '-y'], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 check=True)
                    
                    if os.path.exists(mp3_file):
                        os.remove(filename)
                        filename = mp3_file
                except subprocess.CalledProcessError:
                    # Jika ffmpeg gagal, tetap gunakan file original
                    pass
            else:
                # Video
                # Coba progressive (video+audio) dulu
                stream = yt.streams.filter(progressive=True, resolution=quality, file_extension='mp4').first()
                
                if not stream:
                    # Fallback ke resolusi terdekat
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                
                if not stream:
                    # Last resort: adaptive video + merge dengan audio
                    video_stream = yt.streams.filter(adaptive=True, resolution=quality, type='video').first()
                    if not video_stream:
                        video_stream = yt.streams.filter(adaptive=True, type='video').order_by('resolution').desc().first()
                    
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    
                    if video_stream and audio_stream:
                        # Download both
                        video_file = video_stream.download(output_path=output_path, filename_prefix='video_')
                        audio_file = audio_stream.download(output_path=output_path, filename_prefix='audio_')
                        
                        # Merge dengan ffmpeg
                        output_file = os.path.join(output_path, f"{yt.title}.mp4")
                        try:
                            subprocess.run([
                                'ffmpeg', '-i', video_file, '-i', audio_file,
                                '-c:v', 'copy', '-c:a', 'aac', output_file, '-y'
                            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                            
                            # Hapus temp files
                            os.remove(video_file)
                            os.remove(audio_file)
                            filename = output_file
                        except:
                            # Jika merge gagal, gunakan video only
                            filename = video_file
                            if os.path.exists(audio_file):
                                os.remove(audio_file)
                    else:
                        stream = yt.streams.first()
                        filename = stream.download(output_path=output_path)
                else:
                    filename = stream.download(output_path=output_path)
            
            return {
                'success': True,
                'file_path': filename,
                'title': yt.title,
                'thumbnail': yt.thumbnail_url
            }
        except Exception as e:
            raise Exception(f"pytube download failed: {str(e)}")
    
    def _trim_video(self, input_file, start_time, end_time, output_path):
        """Cut/trim video menggunakan ffmpeg"""
        if not os.path.exists(input_file):
            raise Exception("Input file not found")
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        ext = os.path.splitext(input_file)[1]
        output_file = os.path.join(output_path, f"{base_name}_trimmed{ext}")
        
        # Build ffmpeg command
        cmd = ['ffmpeg', '-i', input_file]
        
        if start_time is not None:
            cmd.extend(['-ss', str(start_time)])
        
        if end_time is not None:
            if start_time is not None:
                duration = end_time - start_time
                cmd.extend(['-t', str(duration)])
            else:
                cmd.extend(['-to', str(end_time)])
        
        cmd.extend(['-c', 'copy', output_file, '-y'])
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # Hapus file original jika trim sukses
            if os.path.exists(output_file):
                os.remove(input_file)
                return {
                    'success': True,
                    'file_path': output_file,
                    'title': base_name + '_trimmed',
                    'thumbnail': None
                }
        except subprocess.CalledProcessError as e:
            raise Exception(f"Video trimming failed: {str(e)}")
    
    def _download_ytdlp(self, url, output_path, quality, download_type, progress_callback):
        """Fallback: Download menggunakan yt-dlp"""
        import yt_dlp
        
        output_template = os.path.join(output_path, '%(title)s.%(ext)s')
        
        # Base options
        base_opts = {
            'outtmpl': output_template,
            'nocheckcertificate': True,
        }
        
        if download_type == 'audio':
            ydl_opts = {
                **base_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            # Video
            height = quality.replace('p', '')
            ydl_opts = {
                **base_opts,
                'format': f'best[height<={height}]',
            }
        
        if progress_callback:
            ydl_opts['progress_hooks'] = [progress_callback]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Untuk audio, ganti ekstensi ke mp3
            if download_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return {
                'success': True,
                'file_path': filename,
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail')
            }
    
    def download_playlist(self, urls, output_path, quality='720p', download_type='video',
                         progress_callback=None):
        """Download multiple videos dari playlist"""
        results = []
        
        for i, url in enumerate(urls):
            try:
                if progress_callback:
                    progress_callback({'status': 'downloading', 'current': i + 1, 'total': len(urls)})
                
                result = self.download(url, output_path, quality, download_type, None)
                results.append(result)
            
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                results.append({'success': False, 'error': str(e), 'url': url})
        
        return results