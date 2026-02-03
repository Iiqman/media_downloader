"""
Platform Widget - Widget untuk handle download per platform
UPDATED (Crash-safe + Responsive + Race-safe):
- Fix RuntimeError: wrapped C/C++ object ... has been deleted (ThumbThread)
- Avoid overriding QThread.finished (no custom signal named "finished")
- Thumbnail loader uses urllib thread, safe cleanup + late-signal ignore
- Multi-download threaded to avoid UI freeze
- Responsive thumbnail scaling and layout reflow
"""

import ssl
import urllib.request

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QComboBox, QProgressBar,
    QRadioButton, QButtonGroup, QScrollArea, QGroupBox,
    QCheckBox, QGridLayout, QMessageBox, QSpinBox,
    QBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap

from backend import YouTubeDownloader, InstagramDownloader, TikTokDownloader, FacebookDownloader
from utils import HistoryManager


def _shorten(text: str, n: int = 80) -> str:
    if not text:
        return ""
    return text if len(text) <= n else (text[:n] + "...")


# -----------------------------
# Worker Threads
# -----------------------------
class CallThread(QThread):
    """Generic thread for calling a method on target (downloader/widget)."""
    result = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, target, method_name: str, *args, **kwargs):
        super().__init__()
        self.target = target
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            method = getattr(self.target, self.method_name)
            res = method(*self.args, **self.kwargs)
            self.result.emit(res if isinstance(res, dict) else {"result": res})
        except Exception as e:
            self.failed.emit(str(e))


class ThumbThread(QThread):
    """Download thumbnail bytes via urllib (no QtNetwork)."""
    data_ready = pyqtSignal(bytes)
    failed = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        try:
            if not self.url:
                self.failed.emit("Thumbnail URL kosong")
                return

            req = urllib.request.Request(
                self.url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/120.0 Safari/537.36"
                }
            )
            ctx = ssl.create_default_context()

            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                data = resp.read()

            if self._abort:
                return

            self.data_ready.emit(data)
        except Exception as e:
            if not self._abort:
                self.failed.emit(str(e))


class MultiDownloadThread(QThread):
    """Thread download multiple urls with progress."""
    progress = pyqtSignal(int, int, str)   # done, total, text
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, downloader, urls, output_path, quality=None, download_type=None):
        super().__init__()
        self.downloader = downloader
        self.urls = urls or []
        self.output_path = output_path
        self.quality = quality
        self.download_type = download_type
        self._abort = False

    def abort(self):
        self._abort = True

    def _call_download_with_fallback(self, url):
        attempts = [
            (url, self.output_path, self.quality, self.download_type, None, None, None),
            (url, self.output_path, self.quality, self.download_type),
            (url, self.output_path, self.quality),
            (url, self.output_path),
        ]
        last_err = None
        for args in attempts:
            try:
                return self.downloader.download(*args)
            except TypeError as e:
                last_err = e
        raise last_err if last_err else TypeError("Signature downloader.download tidak cocok.")

    def run(self):
        try:
            total = len(self.urls)
            results = []

            for i, url in enumerate(self.urls, start=1):
                if self._abort:
                    break

                self.progress.emit(i - 1, total, f"Downloading {i}/{total}...")
                try:
                    res = self._call_download_with_fallback(url)
                    results.append(res if isinstance(res, dict) else {"result": res, "success": True})
                except Exception as e:
                    results.append({"success": False, "error": str(e), "url": url})

                self.progress.emit(i, total, f"Downloaded {i}/{total}")

            ok_count = len([r for r in results if r.get("success")])
            self.done.emit({"results": results, "count": ok_count})
        except Exception as e:
            self.failed.emit(str(e))


# -----------------------------
# Main Widget
# -----------------------------
class PlatformWidget(QWidget):
    download_complete = pyqtSignal(dict)

    NARROW_WIDTH = 560
    THUMB_MIN_W = 180
    THUMB_MAX_W = 520

    def __init__(self, platform, config):
        super().__init__()
        self.platform = platform
        self.config = config
        self.history = HistoryManager()
        self.current_info = None

        self._thumb_thread = None
        self._thumb_pixmap_original = None
        self._threads = []  # keep refs

        if platform == "YouTube":
            self.downloader = YouTubeDownloader()
        elif platform == "Instagram":
            self.downloader = InstagramDownloader()
        elif platform == "TikTok":
            self.downloader = TikTokDownloader()
        elif platform == "Facebook":
            self.downloader = FacebookDownloader()
        else:
            raise ValueError(f"Platform tidak dikenal: {platform}")

        self.init_ui()
        self._apply_responsive_rules()

    # -----------------------------
    # Thread helper (FIXED)
    # -----------------------------
    def _keep_thread(self, t: QThread):
        """
        Keep reference; cleanup on QThread.finished (built-in).
        PENTING: kalau thread yg selesai adalah thumb thread yg sedang aktif,
        set self._thumb_thread = None sebelum deleteLater.
        """
        self._threads.append(t)

        def _cleanup():
            # null-kan thumb ref kalau itu thread yg aktif
            if getattr(self, "_thumb_thread", None) is t:
                self._thumb_thread = None

            try:
                self._threads.remove(t)
            except ValueError:
                pass

            # deleteLater bisa membuat wrapper "dangling" -> kita pastikan ref penting sudah None
            t.deleteLater()

        t.finished.connect(_cleanup)

    # -----------------------------
    # UI
    # -----------------------------
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Input
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout(input_group)

        if self.platform in ["Instagram", "TikTok"]:
            radio_layout = QHBoxLayout()
            self.input_type_group = QButtonGroup()

            self.url_radio = QRadioButton("URL Postingan")
            self.url_radio.setChecked(True)
            self.url_radio.toggled.connect(self.toggle_input_type)
            self.input_type_group.addButton(self.url_radio)
            radio_layout.addWidget(self.url_radio)

            self.username_radio = QRadioButton("Username")
            self.input_type_group.addButton(self.username_radio)
            radio_layout.addWidget(self.username_radio)

            if self.platform == "Instagram":
                self.story_radio = QRadioButton("Story")
                self.input_type_group.addButton(self.story_radio)
                radio_layout.addWidget(self.story_radio)

            radio_layout.addStretch()
            input_layout.addLayout(radio_layout)

        self._input_row_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self._input_row_layout.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(f"Masukkan URL {self.platform}...")
        self.url_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._input_row_layout.addWidget(self.url_input, 1)

        self.fetch_btn = QPushButton("🔍 Fetch Info")
        self.fetch_btn.setObjectName("primaryButton")
        self.fetch_btn.setMaximumWidth(150)
        self.fetch_btn.clicked.connect(self.fetch_info)
        self._input_row_layout.addWidget(self.fetch_btn, 0)

        input_layout.addLayout(self._input_row_layout)
        layout.addWidget(input_group)

        # Preview
        self.preview_group = QGroupBox("Preview")
        self.preview_group.setVisible(False)
        preview_layout = QVBoxLayout(self.preview_group)

        self._preview_top_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self._preview_top_layout.setSpacing(12)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setScaledContents(False)
        self.thumbnail_label.setStyleSheet("border: 1px solid #3d3d3d; border-radius: 4px;")
        self.thumbnail_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._preview_top_layout.addWidget(self.thumbnail_label, 0)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        info_layout.addWidget(self.title_label)

        self.channel_label = QLabel()
        self.channel_label.setStyleSheet("font-size: 9pt; color: gray;")
        self.channel_label.setVisible(False)
        info_layout.addWidget(self.channel_label)

        self.duration_label = QLabel()
        self.duration_label.setStyleSheet("font-size: 9pt; color: gray;")
        self.duration_label.setVisible(False)
        info_layout.addWidget(self.duration_label)

        self.views_label = QLabel()
        self.views_label.setStyleSheet("font-size: 9pt; color: gray;")
        self.views_label.setVisible(False)
        info_layout.addWidget(self.views_label)

        info_layout.addStretch()
        self._preview_top_layout.addLayout(info_layout, 1)

        preview_layout.addLayout(self._preview_top_layout)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setVisible(False)
        self.content_scroll.setMinimumHeight(180)
        self.content_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.content_scroll, 1)

        layout.addWidget(self.preview_group)

        # Options
        self.options_group = QGroupBox("Download Options")
        self.options_group.setVisible(False)
        options_layout = QVBoxLayout(self.options_group)

        if self.platform in ["YouTube", "Facebook"]:
            type_row = QHBoxLayout()
            type_row.addWidget(QLabel("Type:"))

            self.type_group = QButtonGroup()
            self.video_radio = QRadioButton("Video")
            self.video_radio.setChecked(True)
            self.video_radio.toggled.connect(self.toggle_download_type)
            self.type_group.addButton(self.video_radio)
            type_row.addWidget(self.video_radio)

            self.audio_radio = QRadioButton("Audio")
            self.type_group.addButton(self.audio_radio)
            type_row.addWidget(self.audio_radio)

            type_row.addStretch()
            options_layout.addLayout(type_row)

        quality_row = QHBoxLayout()
        quality_row.addWidget(QLabel("Quality:"))

        self.quality_combo = QComboBox()
        self.quality_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        quality_row.addWidget(self.quality_combo, 1)
        options_layout.addLayout(quality_row)

        if self.platform == "YouTube":
            trim_group = QGroupBox("✂️ Trim Video (Optional)")
            trim_group.setCheckable(True)
            trim_group.setChecked(False)
            trim_layout = QGridLayout(trim_group)

            trim_layout.addWidget(QLabel("Start (detik):"), 0, 0)
            self.start_time_spin = QSpinBox()
            self.start_time_spin.setMinimum(0)
            self.start_time_spin.setMaximum(999999)
            self.start_time_spin.setValue(0)
            self.start_time_spin.setSuffix(" s")
            trim_layout.addWidget(self.start_time_spin, 0, 1)

            trim_layout.addWidget(QLabel("End (detik):"), 0, 2)
            self.end_time_spin = QSpinBox()
            self.end_time_spin.setMinimum(0)
            self.end_time_spin.setMaximum(999999)
            self.end_time_spin.setValue(0)
            self.end_time_spin.setSuffix(" s")
            trim_layout.addWidget(self.end_time_spin, 0, 3)

            self.trim_info_label = QLabel("💡 0 = start/end video")
            self.trim_info_label.setStyleSheet("font-size: 9pt; color: gray;")
            trim_layout.addWidget(self.trim_info_label, 1, 0, 1, 4)

            self.trim_group = trim_group
            options_layout.addWidget(trim_group)

        layout.addWidget(self.options_group)

        self.download_btn = QPushButton("⬇️ Download")
        self.download_btn.setObjectName("primaryButton")
        self.download_btn.setVisible(False)
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.download_btn)

        # Progress
        self.progress_group = QGroupBox("Progress")
        self.progress_group.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_group)

        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(self.progress_group)
        layout.addStretch()

        self.quality_combo.clear()
        self.quality_combo.addItems(["Best Quality"])

    # -----------------------------
    # Responsive
    # -----------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_responsive_rules()

    def _clamp(self, v, lo, hi):
        return max(lo, min(hi, v))

    def _apply_responsive_rules(self):
        w = self.width()
        narrow = w < self.NARROW_WIDTH

        self._input_row_layout.setDirection(QBoxLayout.TopToBottom if narrow else QBoxLayout.LeftToRight)
        if narrow:
            self.fetch_btn.setMaximumWidth(16777215)
            self.fetch_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            self.fetch_btn.setMaximumWidth(150)
            self.fetch_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._preview_top_layout.setDirection(QBoxLayout.TopToBottom if narrow else QBoxLayout.LeftToRight)

        if narrow:
            thumb_w = self._clamp(int(w * 0.55), self.THUMB_MIN_W, self.THUMB_MAX_W)
        else:
            thumb_w = self._clamp(int(w * 0.22), self.THUMB_MIN_W, self.THUMB_MAX_W)
        thumb_h = max(90, int(thumb_w * 9 / 16))
        self.thumbnail_label.setFixedSize(thumb_w, thumb_h)

        if self._thumb_pixmap_original is not None:
            scaled = self._thumb_pixmap_original.scaled(
                thumb_w, thumb_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.thumbnail_label.setPixmap(scaled)

    # -----------------------------
    # State (FIXED)
    # -----------------------------
    def reset_state(self):
        self.current_info = None

        for attr in ("video_checkboxes", "post_checkboxes", "story_checkboxes"):
            if hasattr(self, attr):
                delattr(self, attr)

        self.preview_group.setVisible(False)
        self.options_group.setVisible(False)
        self.download_btn.setVisible(False)

        self.channel_label.setVisible(False)
        self.duration_label.setVisible(False)
        self.views_label.setVisible(False)

        self.title_label.setText("")
        self.thumbnail_label.clear()
        self._thumb_pixmap_original = None

        self.content_scroll.setVisible(False)
        self.content_scroll.takeWidget()

        self.quality_combo.clear()
        self.quality_combo.addItems(["Best Quality"])

        if self.platform == "YouTube" and hasattr(self, "trim_group"):
            self.trim_group.setChecked(False)
            self.trim_group.setVisible(True)
            self.start_time_spin.setValue(0)
            self.end_time_spin.setValue(0)

        # cancel old thumbnail safely (guard RuntimeError)
        t = getattr(self, "_thumb_thread", None)
        if t is not None:
            try:
                if t.isRunning():
                    try:
                        t.abort()
                    except Exception:
                        pass
            except RuntimeError:
                # object already deleted
                pass
        self._thumb_thread = None

        self._apply_responsive_rules()

    # -----------------------------
    # UI interactions
    # -----------------------------
    def toggle_input_type(self):
        if hasattr(self, "username_radio") and self.username_radio.isChecked():
            self.url_input.setPlaceholderText(f"Masukkan username {self.platform}...")
        elif hasattr(self, "story_radio") and self.story_radio.isChecked():
            self.url_input.setPlaceholderText("Masukkan username untuk story...")
        else:
            self.url_input.setPlaceholderText(f"Masukkan URL {self.platform}...")

    def toggle_download_type(self):
        info = self.current_info or {}

        if hasattr(self, "audio_radio") and self.audio_radio.isChecked():
            self.quality_combo.clear()
            self.quality_combo.addItems(["320kbps", "192kbps", "128kbps", "64kbps"])
            if hasattr(self, "trim_group"):
                self.trim_group.setVisible(False)
                self.trim_group.setChecked(False)
        else:
            self.quality_combo.clear()
            formats = None
            if isinstance(info, dict) and "formats" in info:
                formats = info["formats"].get("video")
            self.quality_combo.addItems(formats if formats else ["1080p", "720p", "480p", "360p"])
            if hasattr(self, "trim_group"):
                self.trim_group.setVisible(True)

    # -----------------------------
    # Fetch info
    # -----------------------------
    def fetch_info(self):
        input_text = self.url_input.text().strip()
        if not input_text:
            QMessageBox.warning(self, "Error", "Masukkan URL atau username!")
            return

        self.reset_state()

        self.progress_group.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Fetching info...")
        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)

        if self.platform in ["Instagram", "TikTok"] and hasattr(self, "username_radio"):
            if self.username_radio.isChecked():
                method = "extract_user_posts"
            elif hasattr(self, "story_radio") and self.platform == "Instagram" and self.story_radio.isChecked():
                method = "extract_story"
            else:
                method = "extract_post_info" if self.platform == "Instagram" else "extract_video_info"
        else:
            if self.platform == "YouTube":
                method = "extract_info"
            elif self.platform == "Facebook":
                method = "extract_video_info"
            else:
                method = "extract_post_info"

        t = CallThread(self.downloader, method, input_text)
        self._keep_thread(t)
        self.fetch_thread = t

        t.result.connect(self.on_info_fetched)
        t.failed.connect(self.on_error)
        t.start()

    @pyqtSlot(dict)
    def on_info_fetched(self, info):
        if self.sender() is not getattr(self, "fetch_thread", None):
            return

        self.fetch_btn.setEnabled(True)

        self.current_info = info or {}
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.status_label.setText("Info fetched successfully!")

        self.preview_group.setVisible(True)

        self.title_label.setText(_shorten(self.current_info.get("title", "Unknown"), 80))

        if self.current_info.get("channel"):
            self.channel_label.setText(f"📺 {self.current_info['channel']}")
            self.channel_label.setVisible(True)

        if self.current_info.get("duration"):
            duration = int(self.current_info["duration"])
            minutes = duration // 60
            seconds = duration % 60
            self.duration_label.setText(f"⏱️ {minutes}:{seconds:02d}")
            self.duration_label.setVisible(True)
            if hasattr(self, "end_time_spin"):
                self.end_time_spin.setMaximum(duration)
                self.end_time_spin.setValue(duration)

        if self.current_info.get("view_count"):
            views = int(self.current_info["view_count"])
            if views >= 1_000_000:
                views_str = f"{views/1_000_000:.1f}M"
            elif views >= 1_000:
                views_str = f"{views/1_000:.1f}K"
            else:
                views_str = str(views)
            self.views_label.setText(f"👁️ {views_str} views")
            self.views_label.setVisible(True)

        if self.current_info.get("thumbnail"):
            self.load_thumbnail(self.current_info["thumbnail"])

        if self.current_info.get("type") == "playlist":
            self.show_playlist(self.current_info)
        elif "posts" in self.current_info:
            self.show_posts(self.current_info)
        elif "stories" in self.current_info:
            self.show_stories(self.current_info)
        else:
            self.show_download_options(self.current_info)

        if hasattr(self, "video_radio"):
            self.toggle_download_type()

        self.download_btn.setEnabled(True)
        self._apply_responsive_rules()

    # -----------------------------
    # Thumbnail (FIXED)
    # -----------------------------
    def load_thumbnail(self, url: str):
        # cancel old safely (guard RuntimeError)
        old = getattr(self, "_thumb_thread", None)
        if old is not None:
            try:
                if old.isRunning():
                    try:
                        old.abort()
                    except Exception:
                        pass
            except RuntimeError:
                pass
        self._thumb_thread = None

        t = ThumbThread(url)
        self._keep_thread(t)
        self._thumb_thread = t

        t.data_ready.connect(self.on_thumbnail_data)
        t.failed.connect(self._on_thumbnail_error)
        t.start()

    @pyqtSlot(bytes)
    def on_thumbnail_data(self, data: bytes):
        if self.sender() is not getattr(self, "_thumb_thread", None):
            return

        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            self._thumb_pixmap_original = pixmap
            self._apply_responsive_rules()

    @pyqtSlot(str)
    def _on_thumbnail_error(self, msg: str):
        if self.sender() is not getattr(self, "_thumb_thread", None):
            return
        print(f"[Thumbnail] {msg}")

    # -----------------------------
    # Content displays
    # -----------------------------
    def show_playlist(self, info):
        videos = info.get("videos", [])

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.video_checkboxes = []
        for video in videos:
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.video_data = video

            item_layout = QHBoxLayout()
            item_layout.addWidget(checkbox)

            duration = int(video.get("duration", 0) or 0)
            mins = duration // 60
            secs = duration % 60
            label_text = f"{_shorten(video.get('title', 'Unknown'), 60)} ({mins}:{secs:02d})"

            label = QLabel(label_text)
            label.setWordWrap(True)
            item_layout.addWidget(label, 1)

            content_layout.addLayout(item_layout)
            self.video_checkboxes.append(checkbox)

        content_layout.addStretch()
        self.content_scroll.setWidget(content_widget)
        self.content_scroll.setVisible(True)

        self.show_download_options(info)
        self._apply_responsive_rules()

    def show_posts(self, info):
        posts = info.get("posts", [])

        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        content_layout.setHorizontalSpacing(12)
        content_layout.setVerticalSpacing(8)

        self.post_checkboxes = []
        for i, post in enumerate(posts):
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.post_data = post

            title = _shorten(post.get("title", "Post"), 40)
            label = QLabel(title)
            label.setWordWrap(True)

            row = i // 2
            col = (i % 2) * 2

            content_layout.addWidget(checkbox, row, col)
            content_layout.addWidget(label, row, col + 1)

            self.post_checkboxes.append(checkbox)

        self.content_scroll.setWidget(content_widget)
        self.content_scroll.setVisible(True)

        self.download_btn.setVisible(True)
        self.options_group.setVisible(False)
        self._apply_responsive_rules()

    def show_stories(self, info):
        stories = info.get("stories", [])
        if not stories:
            QMessageBox.information(self, "Info", "Tidak ada story yang tersedia")
            return

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.story_checkboxes = []
        for i, story in enumerate(stories):
            checkbox = QCheckBox(f"Story {i+1} ({story.get('type', 'unknown')})")
            checkbox.setChecked(True)
            checkbox.story_data = story
            self.story_checkboxes.append(checkbox)
            content_layout.addWidget(checkbox)

        content_layout.addStretch()

        self.content_scroll.setWidget(content_widget)
        self.content_scroll.setVisible(True)

        self.download_btn.setVisible(True)
        self.options_group.setVisible(False)
        self._apply_responsive_rules()

    def show_download_options(self, info):
        self.options_group.setVisible(True)

        self.quality_combo.clear()
        if isinstance(info, dict) and "formats" in info:
            if hasattr(self, "audio_radio") and self.audio_radio.isChecked():
                formats = info["formats"].get("audio", ["192kbps"])
            else:
                formats = info["formats"].get("video", ["720p"])
            self.quality_combo.addItems(formats if formats else ["Best Quality"])
        else:
            if hasattr(self, "audio_radio") and self.audio_radio.isChecked():
                self.quality_combo.addItems(["320kbps", "192kbps", "128kbps"])
            else:
                self.quality_combo.addItems(["1080p", "720p", "480p", "360p"])

        self.download_btn.setVisible(True)
        self._apply_responsive_rules()

    # -----------------------------
    # Download helpers
    # -----------------------------
    def _call_playlist_with_fallback(self, urls, output_path, quality, download_type):
        attempts = [
            (urls, output_path, quality, download_type),
            (urls, output_path, quality),
            (urls, output_path),
        ]
        last_err = None
        for args in attempts:
            try:
                return self.downloader.download_playlist(*args)
            except TypeError as e:
                last_err = e
        raise last_err if last_err else TypeError("Signature downloader.download_playlist tidak cocok.")

    def _call_single_with_fallback(self, url, output_path, quality, download_type, start_time=None, end_time=None):
        attempts = [
            (url, output_path, quality, download_type, None, start_time, end_time),
            (url, output_path, quality, download_type),
            (url, output_path, quality),
            (url, output_path),
        ]
        last_err = None
        for args in attempts:
            try:
                return self.downloader.download(*args)
            except TypeError as e:
                last_err = e
        raise last_err if last_err else TypeError("Signature downloader.download tidak cocok.")

    def start_download(self):
        output_path = self.config.get_download_folder()

        download_type = "video"
        if hasattr(self, "audio_radio") and self.audio_radio.isChecked():
            download_type = "audio"

        quality = self.quality_combo.currentText() if self.quality_combo.count() else "Best Quality"

        start_time = None
        end_time = None
        if (
            self.platform == "YouTube"
            and download_type == "video"
            and hasattr(self, "trim_group")
            and self.trim_group.isChecked()
        ):
            st = self.start_time_spin.value()
            et = self.end_time_spin.value()
            start_time = st if st > 0 else None
            end_time = et if et > 0 else None

        self.progress_group.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Downloading...")
        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)

        if hasattr(self, "video_checkboxes"):
            urls = []
            for cb in self.video_checkboxes:
                if cb.isChecked() and getattr(cb, "video_data", None):
                    u = cb.video_data.get("url")
                    if u:
                        urls.append(u)

            t = CallThread(self, "_download_playlist_wrapper", urls, output_path, quality, download_type)
            self._keep_thread(t)
            self.download_thread = t
            t.result.connect(self.on_download_complete)
            t.failed.connect(self.on_error)
            t.start()
            return

        if hasattr(self, "post_checkboxes"):
            urls = [cb.post_data.get("url") for cb in self.post_checkboxes if cb.isChecked() and getattr(cb, "post_data", None)]
            urls = [u for u in urls if u]
            self._start_multi_download(urls, output_path, quality, download_type)
            return

        if hasattr(self, "story_checkboxes"):
            urls = [cb.story_data.get("url") for cb in self.story_checkboxes if cb.isChecked() and getattr(cb, "story_data", None)]
            urls = [u for u in urls if u]
            self._start_multi_download(urls, output_path, quality, download_type)
            return

        url = self.url_input.text().strip()
        t = CallThread(self, "_download_single_wrapper", url, output_path, quality, download_type, start_time, end_time)
        self._keep_thread(t)
        self.download_thread = t
        t.result.connect(self.on_download_complete)
        t.failed.connect(self.on_error)
        t.start()

    def _download_single_wrapper(self, url, output_path, quality, download_type, start_time, end_time):
        return self._call_single_with_fallback(url, output_path, quality, download_type, start_time, end_time)

    def _download_playlist_wrapper(self, urls, output_path, quality, download_type):
        return self._call_playlist_with_fallback(urls, output_path, quality, download_type)

    def _start_multi_download(self, urls, output_path, quality, download_type):
        if not urls:
            self.on_error("Tidak ada item yang dipilih untuk di-download.")
            return

        self.progress_bar.setRange(0, len(urls))
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing multiple download...")

        t = MultiDownloadThread(self.downloader, urls, output_path, quality=quality, download_type=download_type)
        self._keep_thread(t)
        self.multi_thread = t

        t.progress.connect(self.on_multi_progress)
        t.done.connect(self.on_download_complete)
        t.failed.connect(self.on_error)
        t.start()

    @pyqtSlot(int, int, str)
    def on_multi_progress(self, done, total, text):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)
        self.status_label.setText(text)

    # -----------------------------
    # Completion & error
    # -----------------------------
    @pyqtSlot(dict)
    def on_download_complete(self, result):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.status_label.setText("Download complete!")
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)

        if isinstance(result, dict) and "results" in result:
            for r in result["results"]:
                if r.get("success"):
                    self.history.add_entry(
                        platform=self.platform,
                        title=r.get("title", "Unknown"),
                        url=r.get("url", ""),
                        file_path=r.get("file_path", ""),
                        thumbnail=r.get("thumbnail"),
                        item_count=1
                    )
        else:
            self.history.add_entry(
                platform=self.platform,
                title=(result.get("title", "Unknown") if isinstance(result, dict) else "Unknown"),
                url=self.url_input.text(),
                file_path=(result.get("file_path", "") if isinstance(result, dict) else ""),
                thumbnail=(result.get("thumbnail") if isinstance(result, dict) else None),
                item_count=(result.get("count", 1) if isinstance(result, dict) else 1)
            )

        self.download_complete.emit(result if isinstance(result, dict) else {"result": result})
        QMessageBox.information(self, "Success", "Download selesai!")

    @pyqtSlot(str)
    def on_error(self, error_msg):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Error: {error_msg}")
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Error: {error_msg}")

    # -----------------------------
    # Cleanup (guard RuntimeError)
    # -----------------------------
    def closeEvent(self, event):
        try:
            t = getattr(self, "_thumb_thread", None)
            if t is not None:
                try:
                    if t.isRunning():
                        try:
                            t.abort()
                        except Exception:
                            pass
                except RuntimeError:
                    pass
            self._thumb_thread = None

            for t in list(self._threads):
                if isinstance(t, MultiDownloadThread):
                    try:
                        if t.isRunning():
                            t.abort()
                    except RuntimeError:
                        pass
        except Exception:
            pass
        super().closeEvent(event)
