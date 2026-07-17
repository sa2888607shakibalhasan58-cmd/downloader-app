import sys
import os
import threading
import socket
import ssl
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.core.window import Window
import yt_dlp

# Global SSL Bypass to ensure zero network-handshake crashes on Android
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

if sys.platform == 'android':
    from android.permissions import request_permissions, Permission

class UniversalDownloaderApp(App):
    def build(self):
        self.exit_click_count = 0
        
        # Hardware Back Button Interceptor
        Window.bind(on_keyboard=self.on_back_button)

        # Request Permissions on Android App Boot
        if sys.platform == 'android':
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.READ_EXTERNAL_STORAGE
            ])

        # Premium Dark-Theme Layout
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=18)
        
        self.label = Label(
            text="Universal Video Downloader Pro", 
            font_size='22sp', 
            bold=True,
            color=get_color_from_hex('#FFFFFF')
        )
        self.layout.add_widget(self.label)
        
        # High-Performance Input Box
        self.url_input = TextInput(
            hint_text="Paste any video link (FB, YT, TikTok, Insta, etc.)...", 
            multiline=False,
            size_hint_y=None,
            height=55,
            background_color=get_color_from_hex('#1E1E24'),
            foreground_color=get_color_from_hex('#FFFFFF'),
            hint_text_color=get_color_from_hex('#7A7A7A'),
            padding=(15, 15, 15, 15)
        )
        self.layout.add_widget(self.url_input)
        
        # Download Button
        self.download_btn = Button(
            text="Download Video", 
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=55,
            background_normal='',
            background_color=get_color_from_hex('#1D70B8')
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        self.layout.add_widget(self.download_btn)
        
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        self.layout.add_widget(self.progress_bar)
        
        self.status_label = Label(
            text="Status: System Ready", 
            font_size='14sp',
            color=get_color_from_hex('#B0B0B0')
        )
        self.layout.add_widget(self.status_label)
        
        return self.layout

    def on_back_button(self, window, key, *args):
        """Play Store Standard Double-tap to exit handler."""
        if key == 27:
            self.exit_click_count += 1
            if self.exit_click_count < 2:
                self.status_label.text = "Press BACK again to exit app"
                Clock.schedule_once(self.reset_exit_counter, 2)
                return True
            else:
                return False  
        return False

    def reset_exit_counter(self, dt):
        self.exit_click_count = 0

    def update_ui(self, progress_val, status_text):
        self.progress_bar.value = progress_val
        self.status_label.text = status_text

    def progress_hook(self, d):
        """Asynchronous download monitoring engine."""
        try:
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percent = int((downloaded / total) * 100)
                    Clock.schedule_once(lambda dt: self.update_ui(percent, f"Status: Downloading ({percent}%)"))
            elif d['status'] == 'finished':
                Clock.schedule_once(lambda dt: self.update_ui(100, "Success: Saved to Phone Gallery!"))
        except Exception:
            pass 

    def is_network_available(self):
        try:
            socket.setdefaulttimeout(4)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except Exception:
            return False

    def clean_url(self, url):
        """Extracts absolute clean URLs by discarding garbage tracking strings."""
        match = re.search(r'(https?://[^\s?]+)', url)
        if match:
            return match.group(1)
        return url

    def start_download_thread(self, instance):
        raw_url = self.url_input.text.strip()
        url = self.clean_url(raw_url)

        if not url or not url.startswith("http"):
            self.status_label.text = "Error: Please paste a valid web URL!"
            return
        
        self.status_label.text = "Status: Spawning download stream..."
        self.progress_bar.value = 0
        
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        if not self.is_network_available():
            Clock.schedule_once(lambda dt: self.update_ui(0, "Error: Internet connection lost!"))
            return

        Clock.schedule_once(lambda dt: self.update_ui(0, "Status: Decrypting website source..."))

        # Setup Global Shared Public Media Storage Path for Android
        if sys.platform == 'android':
            from android.storage import primary_external_storage_path
            download_dir = os.path.join(primary_external_storage_path(), 'Movies', 'Universal_Downloads')
            try:
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
            except Exception:
                Clock.schedule_once(lambda dt: self.update_ui(0, "Error: Storage execution failed!"))
                return
        else:
            download_dir = '.'

        file_template = os.path.join(download_dir, '%(title)s_%(id)s.mp4')

        # Universal Config to handle 1000+ Websites seamlessly
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Multi-source format picker
            'outtmpl': file_template,
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'rm_cachedir': True,
            'socket_timeout': 25,
            'ignoreerrors': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            # Broadcast Media Scanner to push downloaded files to Android Gallery instantly
            if sys.platform == 'android' and os.path.exists(filename):
                from jnius import autoclass
                MediaScannerConnection = autoclass('android.media.MediaScannerConnection')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                currentActivity = PythonActivity.mActivity
                
                MediaScannerConnection.scanFile(currentActivity, [filename], None, None)
                
        except yt_dlp.utils.DownloadError:
            Clock.schedule_once(lambda dt: self.update_ui(0, "Error: Unsupported site, private video, or broken link!"))
        except IOError:
            Clock.schedule_once(lambda dt: self.update_ui(0, "Error: Insufficient phone storage!"))
        except Exception:
            Clock.schedule_once(lambda dt: self.update_ui(0, "Error: Connection timed out. Retry!"))

if __name__ == '__main__':
    UniversalDownloaderApp().run()
