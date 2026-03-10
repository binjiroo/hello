import pyperclip

# 型鋼の名称
steel_name = input("角形鋼管のサイズを入力: ")

# 1. "□-" の部分を取り除き、"x" で分割して値部分のリストを得る
values_str = steel_name.split("x")
# 例: values_str は ["100", "100", "2.3"]

# 2. 文字列から数値に変換（小数も扱えるように float に変換）
values = [float(val) for val in values_str]

# 3. 記号に対応する変数として a, b, c を割り当て
a, b, c = values

# 4. r の値を c の2倍に設定する
r = c * 2
r2 = c

# 5. 最終的なリスト（順番は [a, b, c, r] とする）
aaa = [a, b, c, r]

offset_1 = ((a / 2), (-b / 2))
offset_2 = (0, (-b / 2))
offset_3 = ((-a / 2), (-b / 2))
offset_4 = ((a / 2), 0)
offset_5 = (0, 0)
offset_6 = ((-a / 2), 0)
offset_7 = ((a / 2), (b / 2))
offset_8 = (0, (b / 2))
offset_9 = ((-a / 2), (b / 2))

# ユーザーに選択肢を入力してもらう例
choice = int(input("1から9までの数字を入力してください: "))

if choice == 1:
    selected_offset = offset_1
elif choice == 2:
    selected_offset = offset_2
elif choice == 3:
    selected_offset = offset_3
elif choice == 4:
    selected_offset = offset_4
elif choice == 5:
    selected_offset = offset_5
elif choice == 6:
    selected_offset = offset_6
elif choice == 7:
    selected_offset = offset_7
elif choice == 8:
    selected_offset = offset_8
elif choice == 9:
    selected_offset = offset_9
else:
    print("無効な値が入力されました。")
    selected_offset = None

# 例えば、選択したoffsetを出力する
if selected_offset is not None:
    print("選択されたoffset:", selected_offset)

x_offset = selected_offset[0]
y_offset = selected_offset[1]

# 各変数の計算
s1 = input("s1の値を入力: ")
s2 = input("s2の値を入力: ")
w1 = a / 2          # 例: 100 / 2 = 50.0
w2 = a / 2 - c      # 例: 100/2 - 2.3 = 50 - 2.3 = 47.7
w3 = a / 2 - r  # 例: 50 - (2.3 + 4.6) = 50 - 6.9 = 43.1
h1 = b / 2          # 例: 100 / 2 = 50.0
h2 = b / 2 - c      # 例: 50 - 2.3 = 47.7
h3 = b / 2 - r  # 例: 50 - (2.3 + 4.6) = 50 - 6.9 = 43.1
lc = input("lcの値を入力: ")
lt = input("ltの値を入力: ")
ly = input("lyの値を入力: ")

# 型式リストの作成
shape_list = [
    ["#角形鋼管断面"],
    [30],
    [999],
    [1, "□-" + steel_name],
    # 基本的な直線部分：各x座標にx_offset、各y座標にy_offsetを加える
    [s1, s2, -w1 + x_offset, 0 + y_offset, w1 + x_offset, 0 + y_offset, lc, lt, ly],
    [s1, s2, 0 + x_offset, h1 + y_offset, 0 + x_offset, -h1 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, h1 + y_offset, w1 + x_offset, h1 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, -h1 + y_offset, w1 + x_offset, -h1 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, h1 + y_offset, -w1 + x_offset, -h1 + y_offset, lc, lt, ly],
    [s1, s2, w1 + x_offset, h1 + y_offset, w1 + x_offset, -h1 + y_offset, lc, lt, ly],
    # 角丸や円弧のパラメータが含まれる行については、座標部分にのみオフセットを加える
    [s1, s2, -w3 + x_offset, h2 + y_offset, w3 + x_offset, h2 + y_offset, lc, lt, ly],
    [s1, s2, -w3 + x_offset, -h2 + y_offset, w3 + x_offset, -h2 + y_offset, lc, lt, ly],
    [s1, s2, -w2 + x_offset, h3 + y_offset, -w2 + x_offset, -h3 + y_offset, lc, lt, ly],
    [s1, s2, w2 + x_offset, h3 + y_offset, w2 + x_offset, -h3 + y_offset, lc, lt, ly],
    # 角度が入る行では、座標（wn, hn）の部分にだけオフセットを加える
    [s1, s2, -w3 + x_offset, h3 + y_offset, 90, 180, lc, lt, ly, "E", r],
    [s1, s2, w3 + x_offset, h3 + y_offset, 0, 90, lc, lt, ly, "E", r],
    [s1, s2, w3 + x_offset, -h3 + y_offset, 270, 0, lc, lt, ly, "E", r],
    [s1, s2, -w3 + x_offset, -h3 + y_offset, 180, 270, lc, lt, ly, "E", r],
    # 以下、同様に他の行にも適用
    [s1, s2, -w3 + x_offset, h3 + y_offset, 90, 180, lc, lt, ly, "E", r2],
    [s1, s2, w3 + x_offset, h3 + y_offset, 0, 90, lc, lt, ly, "E", r2],
    [s1, s2, w3 + x_offset, -h3 + y_offset, 270, 0, lc, lt, ly, "E", r2],
    [s1, s2, -w3 + x_offset, -h3 + y_offset, 180, 270, lc, lt, ly, "E", r2],
    [999]
]

# 各行をスペース区切りの文字列に変換
lines = [" ".join(str(item) for item in row) for row in shape_list]

# 各行を改行で結合した文字列にする
result_str = "\n".join(lines)

# 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
