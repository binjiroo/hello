import pyperclip
import math

# 半径 r と角度（度数）をユーザーに入力してもらう

angle_deg = 95

# 角度をラジアンに変換する
angle_rad = math.radians(angle_deg)

# 三角比を利用して各座標を計算する
x_coord =math.cos(angle_rad)
y_coord =math.sin(angle_rad)
y_tan = math.tan(math.radians(5))

# 結果を表示
print("x 座標 =", x_coord)
print("y 座標 =", y_coord)

# 例: 各鋼材のサイズをキー、対応する r の値を値として持つ辞書
steel_r_mapping = {
    "75x40x5x7": (4, 8),
    "100x50x5x7.5": (4, 8),
    "125x65x6x8": (4, 8),
    "150x75x6.5x10": (5, 10),
    "150x75x9x12.5": (7.5, 15),
    "200x80x7.5x11": (6, 12),
    "200x90x8x13.5": (7, 14),
    "250x90x9x13": (7, 14),
    "250x90x11x14.5": (8.5, 17),
    "300x90x9x13": (7, 14),
    "300x90x10x15.5": (9.5, 19),
    "300x90x12x16": (9.5, 19),
    "380x100x10.5x16": (9, 18),
    "380x100x13x16.5": (9, 18),
    "380x100x13x20": (12, 24),
    # 他のサイズを追加する場合はここにキーと値を設定する
}

# 型鋼の名称
steel_name = input("溝形鋼のサイズを入力")

if steel_name in steel_r_mapping:
    r1, r2 = steel_r_mapping[steel_name]
else:
    print("指定されたサイズが存在しません。")
    r1, r2 = None, None  # エラー処理

print(r1, r2)

# 1. "[-" の部分を取り除き、"x" で分割して値部分のリストを得る
values_str = steel_name.split("x")
# values_str は ["200", "80", "7.5", "11"]

# 2. 文字列から数値に変換（整数または浮動小数点として）
# ここでは、少数を含む可能性があるため float に変換していますが、
# 整数だけの場合は int() にも変換可能です
values = [float(val) for val in values_str]

# 3. 記号に対応する変数として a, b, c, d を割り当て
a, b, c, d = values

# 5. 最終的なリスト（順番は [a, b, c, d, r] とする）
aaa = [a, b, c, d, r1, r2]

ff = ((b - c) / 2 ) - (r2 + (r2 * x_coord))
gg = ((b - c) / 2 ) - (r1 + (r1 * x_coord))
hh = ((a / 2) - d) - ff * y_tan
ii = ((a / 2) - d) + gg * y_tan
print(ff)
print(gg)
print(hh)
print(ii)

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
w2 = b / 2 - c     # (5.5 / 2) + 8 = 10.75
w3 = (((b - c) / 2) - (r2 + (r2 * x_coord))) - (c / 2)   # 5.5 / 2 = 2.75
print("w3", w3)
w4 = (((b - c) / 2 ) - (r1 + (r1 * x_coord))) + (c / 2)
w5 = b / 2 - (c + r2)
print("w3", w5)
w6 = b / 2 - r1
print("w6", w6)
h1 = a / 2            # 200
h2 = (((a / 2) - d) - ff * y_tan) - (r2 * y_coord) 
print("h2", h2)            # 8
h3 = ((a / 2) - d) - ff * y_tan       # 200 - 8 = 192
h4 = (((a / 2) - d) + gg * y_tan) + (r1 * y_coord)
print("h4", h4)
h5 = ((a / 2) - d) + gg * y_tan
lc = input("線色を指定")
lt = input("線種を指定")
ly = input("レイヤーを指定")

# 型式リストの作成
shape_list = [
    ["#溝型鋼断面"],
    [30],
    [999],
    [1, "[-" + steel_name],
    #基準線
    [s1, s2, 0 + x_offset, h1 + y_offset, 0 + x_offset, -h1 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, 0 + y_offset, w1 + x_offset, 0 + y_offset, lc, lt, ly],
    #外フランジ上下
    [s1, s2, -w1 + x_offset, h1 + y_offset, w1 + x_offset, h1 + y_offset, lc, lt, ly],
    [s1, s2, -w1 + x_offset, -h1 + y_offset, w1 + x_offset, -h1 + y_offset, lc, lt, ly],
    #内フランジ上下
    [s1, s2, -w3 + x_offset, h3 + y_offset, w4 + x_offset, h5 + y_offset, lc, lt, ly],
    [s1, s2, -w3 + x_offset, -h3 + y_offset, w4 + x_offset, -h5 + y_offset, lc, lt, ly],
    #ウェーブ
    [s1, s2, -w1 + x_offset, h1 + y_offset, -w1 + x_offset, -h1 + y_offset, lc, lt, ly],
    [s1, s2, -w2 + x_offset, h2 + y_offset, -w2 + x_offset, -h2 + y_offset, lc, lt, ly],
    #フランジエッジ
    [s1, s2, w1 + x_offset, h1 + y_offset, w1 + x_offset, h4 + y_offset, lc, lt, ly],
    [s1, s2, w1 + x_offset, -h1 + y_offset, w1 + x_offset, -h4 + y_offset, lc, lt, ly],
    #r指定
    [s1, s2, -w5 + x_offset, h2 + y_offset, 95, 180, lc, lt, ly, "E", r2],
    [s1, s2, -w5 + x_offset, -h2 + y_offset, 180, 265, lc, lt, ly, "E", r2],
    [s1, s2, w6 + x_offset, h4 + y_offset, 275, 0, lc, lt, ly, "E", r1],
    [s1, s2, w6 + x_offset, -h4 + y_offset, 0, 85, lc, lt, ly, "E", r1],
    [999]
]

# 各行をスペース区切りの文字列に変換
lines = [" ".join(str(item) for item in row) for row in shape_list]

# 各行を改行で結合した文字列にする
result_str = "\n".join(lines)

# 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
