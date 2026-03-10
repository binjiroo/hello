import pyperclip

# 型鋼の名称
steel_name = input("H型鋼のサイズを入力")
steel_values = steel_name.split("x")    # H型鋼のサイズを"x"で分割
steel_values = [float(val) for val in steel_values]

column_name = input("角形鋼管(コラム)のサイズを入力")
column_values = column_name.split("x")  # 角形鋼管(コラム)のサイズを"x"で分割
column_values = [float(val) for val in column_values]

diaphragm_name = input("ダイヤフラムのサイズを入力")
diaphragm_values = diaphragm_name.split("x")  # ダイヤフラムのサイズを"x"で分割
diaphragm_values = [float(val) for val in diaphragm_values]

bracket_length = int(input("柱芯からのブラケットの長さを入力"))

# 3. 記号に対応する変数として a, b, c, d を割り当て
stl_h, stl_w, stl_t1, stl_t2 = steel_values
col_h, col_w, col_t = column_values
dip_h, dip_w, dip_t = diaphragm_values
brk_l = bracket_length

# 4. a の値に応じて r の値を設定する（aが0～250ならr=8、251以上ならr=13）
r = 8 if stl_h <= 250 else 13

# 5. 最終的なリスト（順番は [a, b, c, d, r] とする）
steel = [stl_h, stl_w, stl_t1, stl_t2]
column = [col_h, col_w, col_t]
diaphragm = [dip_h, dip_w, dip_t]

offset_1 = (0, (-stl_h / 2))
offset_2 = (0, 0)
offset_3 = (0, (stl_h / 2))

# ユーザーに選択肢を入力してもらう例
choice = int(input("1から3までの数字を入力してください: "))

if choice == 1:
    selected_offset = offset_1
elif choice == 2:
    selected_offset = offset_2
elif choice == 3:
    selected_offset = offset_3
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
hole_endpitch_x = int(input("端点の孔ピッチを指定"))
hole_size = int(input("孔径を指定"))

# 各変数の計算
w1 = col_w / 2
w2 = dip_w / 2
w3 = brk_l
w4 = brk_l + 10
h1 = stl_w / 2            # 200
h2 = stl_t1 / 2             # 8
f = stl_w * 2
lc = input()
lt = input()
ly = input()

# どの孔パターンを使用するか選択
print("孔パターンを選択してください:")
print("1: 標準配置")
print("2: 千鳥配置")
pattern_choice = input("番号を入力してください: ")

# 標準孔パターン用リスト
hole_list = []   # ブロック1用
hole_list2 = []  # ブロック2用

# 千鳥孔パターン用リスト
row_holes_list_1 = []  # ブロック1用（千鳥）
row_holes_list_2 = []  # ブロック2用（千鳥）

if pattern_choice == "1":
    # 標準配置の処理
    for i in range(hole_row_y):
        y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
        for j in range(hole_column_x):
            x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
            x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
            zx1 = x1 + hole_size / 2
            zx2 = x1 - hole_size / 2
            zx3 = x2 + hole_size / 2
            zx4 = x2 - hole_size / 2
            zy1 = y + hole_size / 2
            zy2 = y - hole_size / 2
            hole_list.extend([
                [1, 1, zx1, y + y_offset, zx2, y + y_offset, lc, lt, ly],
                [1, 1, x1, zy1 + y_offset, x1, zy2 + y_offset, lc, lt, ly],
                [1, 1, x1, y + y_offset, zx1, y + y_offset, lc, lt, ly, "E", 360, 0],

                [1, 1, zx3, y + y_offset, zx4, y + y_offset, lc, lt, ly],
                [1, 1, x2, zy1 + y_offset, x2, zy2 + y_offset, lc, lt, ly],
                [1, 1, x2, y + y_offset, zx3, y + y_offset, lc, lt, ly, "E", 360, 0]
            ])

    for i in range(hole_row_y):
        y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
        for j in range(hole_column_x):
            x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
            x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
            zx1 = x1 + hole_size / 2
            zx2 = x1 - hole_size / 2
            zx3 = x2 + hole_size / 2
            zx4 = x2 - hole_size / 2
            zy1 = y + hole_size / 2
            zy2 = y - hole_size / 2
            hole_list2.extend([
                [2, 2, -zx1, y + y_offset, -zx2, y + y_offset, lc, lt, ly],
                [2, 2, -x1, zy1 + y_offset, -x1, zy2 + y_offset, lc, lt, ly],
                [2, 2, -x1, y + y_offset, -zx1, y + y_offset, lc, lt, ly, "E", 360, 0],

                [2, 2, -zx3, y + y_offset, -zx4, y + y_offset, lc, lt, ly],
                [2, 2, -x2, zy1 + y_offset, -x2, zy2 + y_offset, lc, lt, ly],
                [2, 2, -x2, y + y_offset, -zx3, y + y_offset, lc, lt, ly, "E", 360, 0]
            ])

elif pattern_choice == "2":
    # 千鳥配置の場合
    outer_rows = hole_row_y
    actual_rows = outer_rows * 2
    y_top = -hole_pitch_y / 2
    y_bottom = hole_pitch_y / 2
    interval = (y_bottom - y_top) / 3
    y_positions = [y_top, y_top + interval, y_top + 2 * interval, y_bottom]

    for i in range(actual_rows):
        y = y_positions[i]
        if i == 0 or i == actual_rows - 1:
            num_cols = hole_column_x
            extra_x_offset = 0
        else:
            num_cols = hole_column_x - 1
            extra_x_offset = hole_pitch_x / 2

        row_holes_1 = []
        row_holes_2 = []
        for j in range(num_cols):
            x1 = w4 + (hole_endpitch_x + j * hole_pitch_x) + extra_x_offset
            x2 = w3 - (hole_endpitch_x + j * hole_pitch_x) - extra_x_offset
            zx1 = x1 + hole_size / 2
            zx2 = x1 - hole_size / 2
            zy1 = y + hole_size / 2
            zy2 = y - hole_size / 2

            hole_info1 = [
                [1, 1, zx1, y + y_offset, zx2, y + y_offset, lc, lt, ly],
                [1, 1, x1, zy1 + y_offset, x1, zy2 + y_offset, lc, lt, ly],
                [1, 1, x1, y + y_offset, zx1, y + y_offset, lc, lt, ly, "E", 360, 0]
            ]

            hole_info2 = [
                [2, 2, -zx1, y + y_offset, -zx2, y + y_offset, lc, lt, ly],
                [2, 2, -x1, zy1 + y_offset, -x1, zy2 + y_offset, lc, lt, ly],
                [2, 2, -x1, y + y_offset, -zx1, y + y_offset, lc, lt, ly, "E", 360, 0]
            ]

            row_holes_1.extend(hole_info1)
            row_holes_2.extend(hole_info2)

        row_holes_list_1.append(row_holes_1)
        row_holes_list_2.append(row_holes_2)

else:
    print("無効なパターン選択です。標準配置として処理します。")
    for i in range(hole_row_y):
        y = (i - (hole_row_y - 1) / 2) * hole_pitch_y
        for j in range(hole_column_x):
            x1 = w4 + (hole_endpitch_x + j * hole_pitch_x)
            x2 = w3 - (hole_endpitch_x + j * hole_pitch_x)
            zx1 = x1 + hole_size / 2
            zx2 = x1 - hole_size / 2
            zx3 = x2 + hole_size / 2
            zx4 = x2 - hole_size / 2
            zy1 = y + hole_size / 2
            zy2 = y - hole_size / 2
            hole_list.extend([
                [1, 1, zx1, y + y_offset, zx2, y + y_offset, lc, lt, ly],
                [1, 1, x1, zy1 + y_offset, x1, zy2 + y_offset, lc, lt, ly],
                [1, 1, x1, y + y_offset, zx1, y + y_offset, lc, lt, ly, "E", 360, 0],
            ])
            hole_list2.extend([
                [2, 2, -zx1, y + y_offset, -zx2, y + y_offset, lc, lt, ly],
                [2, 2, -x1, zy1 + y_offset, -x1, zy2 + y_offset, lc, lt, ly],
                [2, 2, -x1, y + y_offset, -zx1, y + y_offset, lc, lt, ly, "E", 360, 0]
            ])

# 型式リストの作成
shape_list = [
    ["#H型鋼断面"],
    [30],
    [999],
    [2, "H-" + steel_name],
    ["S", 100, 50],
    ["W", 0],
    #ブロック1ブラケット切端
    [1, 1, w1, 0 + y_offset, w3, 0 + y_offset, lc, 5, ly],
    [1, 1, w3, h1 + y_offset, w3, -h1 + y_offset, lc, lt, ly],
    [1, 1, w1, h1 + y_offset, w3, h1 + y_offset, lc, lt, ly],
    [1, 1, w1, -h1 + y_offset, w3, -h1 + y_offset, lc, lt, ly],
    [1, 1, w1, h2 + y_offset, w3, h2 + y_offset, lc, 5, ly],
    [1, 1, w1, -h2 + y_offset, w3, -h2 + y_offset, lc, 5, ly],
    #ブロック1大梁切端
    [1, 1, w4, h1 + y_offset, w4, -h1 + y_offset, lc, lt, ly],
]
# 選択した孔パターンに応じて、動的生成された孔リストをshape_listに追加する
# 孔情報を shape_list に追加
if pattern_choice == "1":
    shape_list.extend(hole_list)
    shape_list.extend(hole_list2)

elif pattern_choice == "2":
    for row in row_holes_list_1:
        shape_list.extend(row)
    for row in row_holes_list_2:
        shape_list.extend(row)
#ブロック間
shape_list.extend([
    [1, 2, w4, 0 + y_offset, -w4, 0 + y_offset, lc, 5, ly],
    [1, 2, w4, h1 + y_offset, -w4, h1 + y_offset, lc, lt, ly],
    [1, 2, w4, -h1 + y_offset, -w4, -h1 + y_offset, lc, lt, ly],
    [1, 2, w4, h2 + y_offset, -w4, h2 + y_offset, lc, 5, ly],
    [1, 2, w4, -h2 + y_offset, -w4, -h2 + y_offset, lc, 5, ly],
])
    
shape_list.extend([
    #ブロック2ブラケット切端
    [2, 2, -w1, 0 + y_offset, -w3, 0 + y_offset, lc, 5, ly],
    [2, 2, -w3, h1 + y_offset, -w3, -h1 + y_offset, lc, lt, ly],
    [2, 2, -w1, h1 + y_offset, -w3, h1 + y_offset, lc, lt, ly],
    [2, 2, -w1, -h1 + y_offset, -w3, -h1 + y_offset, lc, lt, ly],
    [2, 2, -w1, h2 + y_offset, -w3, h2 + y_offset, lc, 5, ly],
    [2, 2, -w1, -h2 + y_offset, -w3, -h2 + y_offset, lc, 5, ly],
    #ブロック2大梁切端
    [2, 2, -w4, h1 + y_offset, -w4, -h1 + y_offset, lc, lt, ly],
])

# 選択した孔パターンに応じて、動的生成された孔リストをshape_listに追加する
if pattern_choice == "1":
    # 標準配置の場合
    for hole in hole_list:
        shape_list.append(hole)
    for hole in hole_list2:
        shape_list.append(hole)
elif pattern_choice == "2":
    # 千鳥配置の場合
    for hole in hole_info1:
        shape_list.append(hole)
    for hole in hole_info2:
        shape_list.append(hole)

shape_list.append(
    [999, 100, 50]
)

def flatten(item):
    """再帰的にアイテムを平坦化して、1次元リストに変換する関数
       リストとタプルの両方を平坦化対象とする"""
    if isinstance(item, (list, tuple)):
        flat_list = []
        for sub in item:
            flat_list.extend(flatten(sub))
        return flat_list
    else:
        return [item]

# shape_list はすでに作成済みで各行はリストまたはリストのリストになっているとする
flattened_lines = []
for row in shape_list:
    # row を再帰的に平坦化してから、各要素を文字列に変換し、スペースで連結
    flat_row = flatten(row)
    line = " ".join(str(x) for x in flat_row)
    flattened_lines.append(line)

# 改行で結合
result_str = "\n".join(flattened_lines)
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
