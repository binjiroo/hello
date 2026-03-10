import pyperclip

# 各H型鋼に対応するr設定用の辞書
steel_r_mapping = {
    "100x50x5x7": 8,
    "125x60x6x7": 8,
    "150x75x5x7": 8,
    "175x90x5x8": 8,
    "200x100x5.5x8": 8,
    "248x124x5x8": 8,
    "250x125x6x9": 8,
    "298x149x5.5x8": 13,
    "300x150x6.5x9": 13,
    "346x174x6x9": 13,
    "350x175x7x11": 13,
    "396x199x7x11": 13,
    "400x200x8x13": 13,
    "446x199x8x12": 13,
    "450x200x9x14": 13,
    "496x199x9x14": 13,
    "500x200x10x16": 13,
}

# 型鋼の名称
steel_name = input("H型鋼のサイズを入力")

if steel_name in steel_r_mapping:
    r = steel_r_mapping[steel_name]
else:
    print("指定されたサイズが存在しません。")
    r = None  # エラー処理

print(r)

# 1. "H-" の部分を取り除き、"x" で分割して値部分のリストを得る
values_str = steel_name.split("x")
# values_str は ["200", "100", "5.5", "8"]

# 2. 文字列から数値に変換（整数または浮動小数点として）
# ここでは、少数を含む可能性があるため float に変換していますが、
# 整数だけの場合は int() にも変換可能です
values = [float(val) for val in values_str]

# 3. 記号に対応する変数として a, b, c, d を割り当て
a, b, c, d = values

# 5. 最終的なリスト（順番は [a, b, c, d, r] とする）
aaa = [a, b, c, d, r]

offset_1 = ((b / 2), (-a / 2))
offset_2 = (0, (-a / 2))
offset_3 = ((-b / 2), (-a / 2))
offset_4 = ((b / 2), 0)
offset_5 = (0, 0)
offset_6 = ((-b / 2), 0)
offset_7 = ((b / 2), (a / 2))
offset_8 = (0, (a / 2))
offset_9 = ((-b / 2), (a / 2))

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
s1 = input("s1の値を指定")
s2 = input("s2の値を指定")
w1 = b / 2          # 100 / 2 = 50.0
w2 = c / 2 + r     # (5.5 / 2) + 8 = 10.75
w3 = c / 2          # 5.5 / 2 = 2.75
h1 = a / 2            # 200
h2 = a / 2 - d             # 8
h3 = a / 2 - (d + r)       # 200 - 8 = 192
lc = input("線色を指定")
lt = input("線種を指定")
ly = input("レイヤーを指定")

# 型式リストの作成
shape_list = [
    ["#H型鋼断面"],
    [30],
    [999],
    [1, "H-" + steel_name],
    #基準線
    [s1, s2, 0 + x_offset, h1 + y_offset, 0 + x_offset, -h1 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, 0 + y_offset, w1 + x_offset, 0 + y_offset, lc, lt, ly],
    #外フランジ上下
    [s1, s2, -w1 + x_offset, h1 + y_offset, w1 + x_offset, h1 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, -h1 + y_offset, w1 + x_offset, -h1 + y_offset, lc, lt, ly],
    #内フランジ上下
    [s1, s2, -w1 + x_offset, h2 + y_offset, -w2 + x_offset, h2 + y_offset, lc, lt, ly],
    [s1, s2, w1 + x_offset, h2 + y_offset, w2 + x_offset, h2 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, -h2 + y_offset, -w2 + x_offset, -h2 + y_offset, lc, lt, ly],
    [s1, s2, w1 + x_offset, -h2 + y_offset, w2 + x_offset, -h2 + y_offset, lc, lt, ly],
    #ウェーブ
    [s1, s2, -w3 + x_offset, h3 + y_offset, -w3 + x_offset, -h3 + y_offset, lc, lt, ly],
    [s1, s2, w3 + x_offset, h3 + y_offset, w3 + x_offset, -h3 + y_offset, lc, lt, ly],
    #フランジエッジ
    [s1, s2, -w1 + x_offset, h1 + y_offset, -w1 + x_offset, h2 + y_offset, lc, lt, ly],
    [s1, s2, w1 + x_offset, h1 + y_offset, w1 + x_offset, h2 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, -h1 + y_offset, -w1 + x_offset, -h2 + y_offset, lc, lt, ly],
    [s1, s2, w1 + x_offset, -h1 + y_offset, w1 + x_offset, -h2 + y_offset, lc, lt, ly],
    #r指定
    [s1, s2, -w2 + x_offset, h3 + y_offset, 0, 90, lc, lt, ly, "E", r],
    [s1, s2, w2 + x_offset, h3 + y_offset, 90, 180, lc, lt, ly, "E", r],
    [s1, s2, -w2 + x_offset, -h3 + y_offset, 270, 0, lc, lt, ly, "E", r],
    [s1, s2, w2 + x_offset, -h3 + y_offset, 180, 270, lc, lt, ly, "E", r],
    [999]
]

# 各行をスペース区切りの文字列に変換
lines = [" ".join(str(item) for item in row) for row in shape_list]

# 各行を改行で結合した文字列にする
result_str = "\n".join(lines)

# 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
