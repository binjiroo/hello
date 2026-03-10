from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
import MeCab
import romkan
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

def get_google_ime_suggestions(text):
    url = "https://www.google.com/transliterate?langpair=ja-Hira|ja&text=" + text
    response = requests.get(url)
    if response.status_code == 200:
        candidates = response.json()[0][1]
        logging.debug(f"API Response for {text}: {candidates}")
        return candidates
    else:
        logging.error(f"Failed to get candidates for '{text}', status code: {response.status_code}")
        return []

def hiragana_to_katakana(hiragana_text):
    return ''.join(chr(ord(char) + 0x60) if 'ぁ' <= char <= 'ん' else char for char in hiragana_text)

def katakana_to_hiragana(katakana_text):
    return ''.join(chr(ord(char) - 0x60) if 'ァ' <= char <= 'ヴ' else char for char in katakana_text)

def normalize_input(text):
    return romkan.to_hiragana(romkan.to_roma(text))

def generate_conversion_candidates(surface, feature, reading):
    normalized_reading = normalize_input(reading)
    candidates = [surface, hiragana_to_katakana(normalized_reading), normalized_reading, romkan.to_roma(normalized_reading)]
    kanji_candidates = get_google_ime_suggestions(normalized_reading)
    all_candidates = list(set(candidates + kanji_candidates))
    ordered_candidates = sorted(all_candidates)
    return ordered_candidates

class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.nodes = []  # 形態素解析の結果を保存するリスト

    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        # ユーザーが複数行のテキストを入力できるテキスト入力ボックス
        self.text_input = TextInput(hint_text='複数行テキストを入力してください', size_hint_y=None, height=100, multiline=True)
        # 形態素解析を実行するボタン
        self.analyze_button = Button(text='形態素解析を実行', size_hint_y=None, height=50)
        self.analyze_button.bind(on_press=self.analyze_text)
        # レイアウトにウィジェットを追加
        self.layout.add_widget(self.text_input)
        self.layout.add_widget(self.analyze_button)
        return self.layout

    def analyze_text(self, instance):
        text = self.text_input.text
        self.nodes.clear()  # 以前の分析結果をクリア
        mecab = MeCab.Tagger("-Ochasen")
        lines = text.splitlines()
        for line in lines:
            parsed = mecab.parse(line)
            for chunk in parsed.splitlines()[:-1]:  # EOSを除外
                cols = chunk.split('\t')
                if len(cols) >= 6:
                    surface, feature, reading = cols[0], cols[3], cols[1]
                    # 各単語について変換候補を生成し、スピナーを作成
                    conversion_candidates = self.generate_conversion_candidates(surface, feature, reading)
                    spinner = Spinner(text=surface, values=conversion_candidates, size_hint_y=None, height=44)
                    spinner.bind(text=self.on_spinner_select)
                    # レイアウトにスピナーを追加
                    self.layout.add_widget(spinner)

    def generate_conversion_candidates(self, surface, feature, reading):
        normalized_reading = romkan.to_hiragana(romkan.to_roma(reading))
        candidates = [surface, romkan.to_katakana(normalized_reading), normalized_reading, romkan.to_roma(normalized_reading)]
        return candidates

    def on_spinner_select(self, spinner, text):
        print(f"Selected {text} for {spinner.text}")  # 変更された値をコンソールに出力

if __name__ == '__main__':
    MainApp().run()