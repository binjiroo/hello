import pyperclip

# 型鋼の名称
steel_name = input("H型鋼のサイズを入力")

# 1. "H-" の部分を取り除き、"x" で分割して値部分のリストを得る
values_str = steel_name.split("x")
# values_str は ["200", "100", "5.5", "8"]

# 2. 文字列から数値に変換（整数または浮動小数点として）
# ここでは、少数を含む可能性があるため float に変換していますが、
# 整数だけの場合は int() にも変換可能です
values = [float(val) for val in values_str]

# 3. 記号に対応する変数として a, b, c, d を割り当て
a, b, c, d = values

# 4. a の値に応じて r の値を設定する（aが0～250ならr=8、251以上ならr=13）
r = 8 if a <= 250 else 13

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

hole_column_x = int(input("孔の列数を指定"))
hole_row_y = int(input("孔の行数を指定"))
hole_pitch_x = int(input("列の孔ピッチを指定"))
hole_pitch_y = int(input("行の孔ピッチを指定"))
hole_endpitch_x = int(input("列の端点からの孔ピッチを指定"))
hole_endpitch_y = int(input("行の端点からの孔ピッチを指定"))
hole_size = int(input("孔径を指定"))

# 各変数の計算
h1 = a / 2            # 200
h2 = a / 2 - d             # 8
lc = input()
lt = input()
ly = input()

# 動的に生成される孔の情報を格納するリスト
hole_list = []

# 行数に応じたループ（中央を基準に配置する例）
for i in range(hole_row_y):
    # 中央基準のy座標の計算
    y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
    for j in range(hole_column_x):
        # 各列のx座標の計算（端点からのオフセットを考慮）
        x = hole_endpitch_x + j * hole_pitch_x
        zx1 = x + hole_size / 2
        zx2 = x - hole_size / 2
        zy1 = y + hole_size / 2
        zy2 = y - hole_size / 2
        # 孔の情報をリストとして追加（形式は例：[1, 1, x, y]）
        hole_list.extend([
            [1, 1, zx1, y, zx2, y, lc, lt, ly],
            [1, 1, x, zy1, x, zy2, lc, lt, ly],
            [1, 1, x, y, zx1, y, lc, lt, ly, "E", 360, 0]
        ])

# ブロック2用の孔の情報を格納するリスト
hole_list2 = []

for i in range(hole_row_y):
    # 中央基準のy座標の計算
    y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
    # 列のループを逆順にする（右から左）
    for j in range(hole_column_x):
        x = hole_endpitch_x + j * hole_pitch_x
        zx1 = x + hole_size / 2
        zx2 = x - hole_size / 2
        zy1 = y + hole_size / 2
        zy2 = y - hole_size / 2
        # 例として、複数の孔情報リストを生成
        hole_list2.extend([
            [2, 2, -zx1, y, -zx2, y, lc, lt, ly],
            [2, 2, -x, zy1, -x, zy2, lc, lt, ly],
            [2, 2, -x, y, -zx1, y, lc, lt, ly, "E", 360, 0]
        ])

# 型式リストの作成
shape_list = [
    ["#H型鋼断面"],
    [30],
    [999],
    [2, "H-" + steel_name],
    ["S", 100, 50],
    ["W", 0],
    #ブロック1切端
    [1, 1, 0, h1 + y_offset, 0, -h1 + y_offset, lc, lt, ly],
]
# 動的に生成された孔リストをshape_listに追加
for hole in hole_list:
    shape_list.append(hole)
    #ブロック間
shape_list.extend([
    [1, 2, 0, 0, 0, 0, lc, 5, ly],
    [1, 2, 0, h1 + y_offset, 0, h1 + y_offset, lc, lt, ly],
    [1, 2, 0, -h1 + y_offset, 0, -h1 + y_offset, lc, lt, ly],
    [1, 2, 0, h2 + y_offset, 0, h2 + y_offset, lc, lt, ly],
    [1, 2, 0, -h2 + y_offset, 0, -h2 + y_offset, lc, lt, ly],
])
# ブロック2切端のヘッダー追加
shape_list.extend([
    [2, 2, 0, h1 + y_offset, 0, -h1 + y_offset, lc, lt, ly]
])

# 生成したブロック2の孔情報を追加
for hole in hole_list2:
    shape_list.append(hole)

shape_list.append(
    [999, 100, 50]
)

# 各行をスペース区切りの文字列に変換
lines = [" ".join(str(item) for item in row) for row in shape_list]

# 各行を改行で結合した文字列にする
result_str = "\n".join(lines)

# 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
