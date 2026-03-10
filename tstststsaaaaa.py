import tkinter as tk

# 入力されたテキストをリストボックスに追加する関数
def add_to_list():
    # エントリーからテキストを取得
    input_text = entry.get()
    # リストボックスにテキストを追加
    if input_text:  # 入力されたテキストが空でない場合のみ追加
        listbox.insert(tk.END, input_text)
    # エントリーの内容をクリア
    entry.delete(0, tk.END)

# ウインドウの作成
root = tk.Tk()
root.title("テキスト入力とリスト追加")

# エントリー（入力フォーム）の作成
entry = tk.Entry(root)
entry.pack()

# 追加ボタンの作成
add_button = tk.Button(root, text="追加", command=add_to_list)
add_button.pack()

# リストボックスの作成
listbox = tk.Listbox(root)
listbox.pack(fill=tk.BOTH, expand=True)

# GUIを表示
root.mainloop()
