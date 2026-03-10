import tkinter as tk
from tkinter import scrolledtext

# 翻訳機能の模擬
def translate_text():
    # 入力されたテキストを取得
    original_text = text_area.get("1.0", tk.END)
    # 翻訳されたテキストを表示エリアに設定（ここでは単純にテキストを置換）
    translated_text = "Translated text would appear here."
    result_area.config(state=tk.NORMAL)
    result_area.delete("1.0", tk.END)
    result_area.insert(tk.INSERT, translated_text)
    result_area.config(state=tk.DISABLED)

# GUIの作成
root = tk.Tk()
root.title("テキスト翻訳アプリ")

# テキスト入力エリア
text_area = scrolledtext.ScrolledText(root, width=40, height=10)
text_area.pack()

# 翻訳ボタン
translate_button = tk.Button(root, text="翻訳", command=translate_text)
translate_button.pack()

# 翻訳結果表示エリア
result_area = scrolledtext.ScrolledText(root, width=40, height=10)
result_area.pack()
result_area.config(state=tk.DISABLED)

root.mainloop()
