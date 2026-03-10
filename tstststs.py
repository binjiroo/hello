import tkinter as tk

def add_button():
    # ユーザー入力を取得
    text = new_button_text.get()
    row = int(new_button_row.get())
    col = int(new_button_col.get())
    
    # 新しいボタンをリストに追加
    button_texts.append((text, row, col))
    
    # 新しいボタンをGUIに追加
    button = tk.Button(buttons_frame, text=text, width=3, height=1, 
                       font=('Arial', 24), 
                       command=lambda num=text: on_button_click(num))
    button.grid(row=row, column=col)
    
    # 入力フィールドをクリア
    new_button_text.set('')
    new_button_row.set('')
    new_button_col.set('')

def on_button_click(number):
    current_value = display_var.get()
    if len(current_value) < 5:  # 現在の値が5桁未満の場合のみ追加
        display_var.set(current_value + number)  # ボタンの数字を現在の値に追加

def reset_display():
    display_var.set('')  # 表示変数を空に設定

# ウィンドウの作成
window = tk.Tk()
window.title("数字表示アプリ")

# 表示欄の作成（背景を黒に、文字色を白に設定）
display_var = tk.StringVar()
display_label = tk.Label(window, textvariable=display_var, font=('Arial', 28), bg='black', fg='white')
display_label.pack(fill=tk.X)

# ボタンの作成と配置
buttons_frame = tk.Frame(window)
buttons_frame.pack()

# ボタンの配置はテンキーの並びに似せる
button_texts = [
    ('9', 1, 2),
    ('8', 1, 1),
    ('7', 1, 0),
    ('6', 2, 2),
    ('5', 2, 1),
    ('4', 2, 0),
    ('3', 3, 2),
    ('2', 3, 1),
    ('1', 3, 0),
    ('0', 4, 1),
    ('DEL', 4, 2),  # デリートボタンを追加
]

# ボタンとその動作を定義
for text, row, col in button_texts:
    if text == 'DEL':  # デリートボタンの場合、入力欄をリセットする関数を割り当て
        button = tk.Button(buttons_frame, text=text, width=3, height=1,
                           font=('Arial', 24),
                           command=reset_display)
    else:
        button = tk.Button(buttons_frame, text=text, width=3, height=1, 
                           font=('Arial', 24), 
                           command=lambda num=text: on_button_click(num))
    button.grid(row=row, column=col)

# 新しいボタンの情報を入力するためのフィールド
new_button_text = tk.StringVar()
new_button_row = tk.StringVar()
new_button_col = tk.StringVar()

entry_text = tk.Entry(window, textvariable=new_button_text)
entry_row = tk.Entry(window, textvariable=new_button_row)
entry_col = tk.Entry(window, textvariable=new_button_col)
add_button_btn = tk.Button(window, text="ボタン追加", command=add_button)

# ユーザー入力フィールドとボタン追加ボタンを配置
entry_text.pack()
entry_row.pack()
entry_col.pack()
add_button_btn.pack()

# ウィンドウのメインループを実行
window.mainloop()
