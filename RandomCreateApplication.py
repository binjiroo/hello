import tkinter as tk
import random

# 数値を生成する関数
def generate_numbers(digit):
    return [str(random.randint(0, 10**digit - 1)).zfill(digit) for _ in range(50)]

# 数値を表示する関数
def display_numbers(numbers):
    for widget in generate_space.winfo_children():
        widget.destroy()

    for i, number in enumerate(numbers):
        row, col = divmod(i, 10)
        label = tk.Label(generate_space, text=number, bg="white")
        label.grid(row=row, column=col, padx=5, pady=5)

# "Create"ボタンの動作
def create_numbers():
    digit = int(digit_var.get())
    numbers = generate_numbers(digit)
    display_numbers(numbers)

# 以下、アプリの基本設定を続ける
app = tk.Tk()
# ...（前述の基本設定コード）

# 桁数設定のためのドロップダウンメニュー
digit_var = tk.StringVar(value="1")
digit_menu = ttk.Combobox(button_frame, textvariable=digit_var, values=[str(i) for i in range(1, 11)])
digit_menu.pack(side=tk.LEFT)

# "Create"ボタン
create_button = tk.Button(button_frame, text="Create", bg="cyan", command=create_numbers)
create_button.pack(side=tk.LEFT)

# アプリの実行
app.mainloop()
