import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.videoplayer import VideoPlayer
import youtube_dl

kivy.require('2.0.0')

class VideoApp(App):
    def build(self):
        # YouTube動画のURL
        video_url = 'https://www.youtube.com/watch?v=tEGmunfngD4'
        
        try:
            # YouTube動画のダウンロード
            ydl_opts = {
                'format': 'best',
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_url = info_dict.get('url', None)

            # ビデオプレーヤーの作成
            video = VideoPlayer(source=video_url, size_hint=(None, None), size=(400, 750), state='play')
        
            # レイアウトの作成
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(video)

            return layout
        except Exception as e:
            print(f'Error: {e}')
            return BoxLayout()

if __name__ == '__main__':
    VideoApp().run()
