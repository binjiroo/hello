import pyperclip

# 型鋼の名称の入力
main_steel_name = input("親H型鋼を指定:")
sub_steel_name = input("子H型鋼を指定:")
gusset_name = input("ガセット名を指定:")

# 1. "x" で分割して文字列リストを取得し、数値に変換
main_values = [float(val) for val in main_steel_name.split("x")]
sub_values = [float(val) for val in sub_steel_name.split("x")]

# 2. パラメータの展開（例：a, b, c, d と e, f, g, h）
a, b, c, d = main_values
e, f, g, h = sub_values

# 3. r の初期値（※後で入力により上書きされる）
r = 10

y_set = int(input("高さ指定"))

# 4. オフセット値の選択（各offsetをリストにまとめ、ユーザー入力で選択）
offsets = [
    (b / 2, -a / 2),
    (0, -a / 2),
    (-b / 2, -a / 2),
    (b / 2, 0),
    (0, 0),
    (-b / 2, 0),
    (b / 2, a / 2),
    (0, a / 2),
    (-b / 2, a / 2)
]

choice = int(input("1から9までの数字を入力してください: "))
if 1 <= choice <= len(offsets):
    x_offset, y_offset = offsets[choice - 1]
    print("選択されたoffset:", (x_offset, y_offset))
else:
    print("無効な値が入力されました。")
    x_offset, y_offset = (0, 0)

# 5. 板厚、r、孔（穴）に関する各種パラメータの入力
t = int(input("板厚を指定"))
r = int(input("H断面のrを指定"))

hole_column_x = int(input("孔の列数を指定"))
hole_row_y = int(input("孔の行数を指定"))
hole_pitch_x = int(input("列の孔ピッチを指定"))
hole_pitch_y = int(input("行の孔ピッチを指定"))
hole_endpitch_x = int(input("親フランジ端点からの孔ピッチを指定"))
hole_endpitch_y = int(input("行の端点からの孔ピッチを指定"))
hole_size = int(input("孔径を指定"))

# 6. その他の計算に用いるパラメータの入力・計算
s1 = input("s1の値を入力: ")
s2 = input("s2の値を入力: ")
w1 = (b / 2 - 10) + x_offset         # 例: 100 / 2 = 50.0
w2 = (c / 2) + x_offset              # 例: 100/2 = 50.0
w3 = (c / 2 + r) + x_offset          # 例: 50 + r
w4 = (b / 2 + 50) + x_offset
w5 = (b / 2 + 1) + x_offset
h1 = (a / 2 - d) + y_offset          # 例: 100 / 2 = 50.0
h2 = -(a / 2 - (d + 2)) + y_offset    # 例: 50 - 2 = 48.0（概算）
h3 = (a / 2 - (d + r)) + y_offset    # 例: 50 - r
h4 = -(a / 2 - (d + r + 2)) + y_offset
lc = input("lcの値を入力: ")
lt = input("ltの値を入力: ")
ly = input("lyの値を入力: ")

# 7. 動的に生成される孔の情報をリストへ追加
hole_list = []
for i in range(hole_row_y):
    # 中央基準の y 座標計算
    y = (((i - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set
    for j in range(hole_column_x):
        # 各列の x 座標計算（親フランジ端点からのオフセットを加味）
        x = ((b / 2) + hole_endpitch_x + j * hole_pitch_x) + x_offset
        zx1 = x + hole_size / 2
        zx2 = x - hole_size / 2
        zy1 = y + hole_size / 2
        zy2 = y - hole_size / 2
        ep = hole_size / 2
        # 元コードと同様、3行分のリストを追加
        hole_list.append([s1, s2, zx1, y, zx2, y, lc, lt, ly])
        hole_list.append([s1, s2, x, zy1, x, zy2, lc, lt, ly])
        hole_list.append([s1, s2, x, y, 0, 360, lc, lt, ly, "E", ep, 0])

# 8. 基準座標の計算（孔の配置に利用）
x_first = ((b / 2) + hole_endpitch_x) + x_offset
x_last = ((b / 2) + hole_endpitch_x + (hole_column_x - 1) * hole_pitch_x) + x_offset

y_first = (((0 - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set
y_last = ((((hole_row_y - 1) - (hole_row_y - 1) / 2) * hole_pitch_y) + (a / 2 - e / 2)) + y_offset + y_set

# 9. 新しい線（水平線・垂直線、カット線、コーナー線）の情報をリストに追加
new_lines = []

if ((y_last - y_set) + 40) < h1:
    # shape_list用（それ以外の場合は「shape_listとフランジ-10」）
    print("shape_listとフランジ-10を指定。")
    print(y_last + 40)
    print(h1)
    top_horizontal_line = [s1, s2, w5, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly]
elif ((y_last - y_set) + 40) >= h1:
    # shape_list2用（上水平線の y 座標が h1 より大きい）
    print("shape_list2とフランジ+1を指定。")
    print(y_last + 40)
    print(h1)
    top_horizontal_line = [s1, s2, w1 + 10, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly]

# その後、new_lines に追加する
new_lines.append(top_horizontal_line)

# bottom_horizontal_line のリストを条件に応じて定義する
if (y_first - y_set - 40) > h2:
    # shape_list3用（下水平線の y 座標が -h1 より小さい場合）
    print("shape_listとフランジ-10を指定。")
    print(y_first - 40)
    print(h2)
    bottom_horizontal_line = [s1, s2, w1 + 10, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly]
elif (y_first - y_set - 40) <= h2:
    # shape_listまたはshape_list2用（下水平線の y 座標が -h1 以上の場合）
    print("shape_list2とフランジ-10を指定。")
    print(y_first - 40)
    print(h2)
    bottom_horizontal_line = [s1, s2, w5, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly]
new_lines.append(bottom_horizontal_line)

right_vertical_line = [s1, s2, x_last + 40, y_first - 40,
                       x_last + 40, y_last + 25, lc, lt, ly]
new_lines.append(right_vertical_line)

cut_line = [s1, s2, x_last + 25, y_last + 40,
            x_last + 40, y_last + 25, lc, lt, ly]
new_lines.append(cut_line)

print("shape_list → ", (y_last + 40) < h1 and (y_first - 40) > h2)
print("shape_list → ", (y_last + 40), "<", h1, ":", (y_first - 40), ">", h2)
print("shape_list2 → ", (y_last + 40) > h1)
print("shape_list2 → ", (y_last + 40), ">", h1)
print("shape_list3 → ", (y_first - 40) < h2)
print("shape_list3 → ", (y_first - 40), "<", h2)
print("shape_list4 → ", (y_last + 40) >= h1 and (y_first - 40) <= h2)
print("shape_list4 → ", (y_last + 40), ">=", h1, ":", (y_first - 40), "<=", h2)
# 最終形状リストを決定する前に、フラグ変数を設定する（例: final_shape_type に "shape_list", "shape_list2", "shape_list3" などを代入）
if (y_last + 40) >= h1 and (y_first - 40) <= h2:
    final_shape_type = "shape_list4"
    print("shape_list4 → ", (y_first - 40) < h2)
    print("shape_list4を選択")
    shape_list4_debug_info = ["shape_list4", (y_first - 40), h2]
    print(shape_list4_debug_info)
elif (y_last + 40) >= h1:
    final_shape_type = "shape_list2"
    print("shape_list2 → ", (y_last + 40) > h1)
    print("shape_list2を選択")
    shape_list2_debug_info = ["shape_list2", ((y_last) + 40), h1]
    print(shape_list2_debug_info)
elif (y_first - 40) <= h2:
    final_shape_type = "shape_list3"
    print("shape_list3 → ", (y_first - 40) < h2)
    print("shape_list3を選択")
    shape_list3_debug_info = ["shape_list3", (y_first - 40), h2]
    print(shape_list3_debug_info)
else:
    final_shape_type = "shape_list"
    print("shape_list → ", (y_last + 40) < h1 and (y_first - 40) > h2)
    print("shape_listを選択")
    shape_list_debug_info = ["shape_list", (y_last + 40), h1, (y_first - 40), h2]
    print(shape_list_debug_info)

# 角丸線の追加条件をフラグに基づいて行う
if final_shape_type in ["shape_list", "shape_list3"]:
    print("top_corner_lineが選択されました。")
    top_corner_line = [s1, s2, w1 + 10, y_last + 50, 180, 270, lc, lt, ly, "E", 10, 0]
    new_lines.append(top_corner_line)
    
if final_shape_type in ["shape_list", "shape_list2"]:
    print("bottom_corner_lineが選択されました。")
    bottom_corner_line = [s1, s2, w1 + 10, y_first - 50, 90, 180, lc, lt, ly, "E", 10, 0]
    new_lines.append(bottom_corner_line)

# 10. 型式リストの作成（元のコードと同じリスト構成）
shape_list = [
    ["#ガセットプレート"],
    [30],
    [999],
    [2, gusset_name],
    ["S", 100, 50],
    [800, 1],
    [s1, s2, w3, h1, w1, h1, lc, lt, ly],
    [s1, s2, w3, h2, w1, h2, lc, lt, ly],
    [s1, s2, w1, h1, w1, y_last + 50, lc, lt, ly],
    [s1, s2, w1, h2, w1, y_first - 50, lc, lt, ly],
    [s1, s2, w2, h3, w2, h4, lc, lt, ly],
    [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
    [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
    [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
    [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
    [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
    [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
    [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
    [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
]
# shape_list の生成後、デバッグ情報をリストの先頭に追加する例
debug_info = ["debug_info", top_horizontal_line[3] - y_set, h1, bottom_horizontal_line[3] - y_set, h2]
#shape_list.insert(0, debug_info)
print(debug_info)
# 動的に生成された孔リストをshape_listに追加
for hole in hole_list:
    shape_list.append(hole)

# new_lines のリストを shape_list に追加
shape_list.extend(new_lines)

# 最後に [999, 100, 50] を追加
shape_list.append([999, 100, 50])

final_shape_list = shape_list  # そのまま shape_list を使用

# shape_list2 を新たに定義（例として、shape_list の内容を一部変更する）
shape_list2 = [
    ["#ガセットプレート (修正版)"],
    [30],   # 例: 30 の代わりに 40
    [999],  # 例: 異なる番号
    [2, gusset_name],
    ["S", 100, 50],
    [800, 1],
    # shape_list の残りの要素を必要に応じて追加
    [s1, s2, w3, h1, w5, h1, lc, lt, ly],
    [s1, s2, w3, h2, w1, h2, lc, lt, ly],
    [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
    [s1, s2, w1, h2, w1, y_first - 50, lc, lt, ly],
    [s1, s2, w2, h3, w2, h4, lc, lt, ly],
    [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
    [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
    [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
    [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
    [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
    [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
    [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
    [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
]
# shape_list2 の生成後、デバッグ情報をリストの先頭に追加する例
debug_info2 = ["debug_info2", top_horizontal_line[3] - y_set, h1]
#shape_list2.insert(0, debug_info2)
# もし動的な孔情報や new_lines を追加する必要があれば、同様に追加します
for hole in hole_list:
    shape_list2.append(hole)
# new_lines の中から top_corner_line を除外したリストを作成
shape_list2.extend(new_lines)
shape_list2.append([999, 100, 50])

final_shape_list = shape_list2  # 以降は shape_list2 を使用

# shape_list3 を新たに定義（例として、shape_list の内容を一部変更する）
shape_list3 = [
    ["#ガセットプレート (修正版)"],
    [30],   # 例: 30 の代わりに 40
    [999],  # 例: 異なる番号
    [2, gusset_name],
    ["S", 100, 50],
    [800, 1],
    # shape_list の残りの要素を必要に応じて追加
    [s1, s2, w3, h1, w1, h1, lc, lt, ly],
    [s1, s2, w3, h2, w5, h2, lc, lt, ly],
    [s1, s2, w1, h1, w1, y_last + 50, lc, lt, ly],
    [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
    [s1, s2, w2, h3, w2, h4, lc, lt, ly],
    [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
    [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
    [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
    [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
    [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
    [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
    [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
    [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
]
# shape_list3 の生成後、デバッグ情報をリストの先頭に追加する例
debug_info3 = ["debug_info3", bottom_horizontal_line[3] - y_set, h2]
#shape_list3.insert(0, debug_info3)

# もし動的な孔情報や new_lines を追加する必要があれば、同様に追加します
for hole in hole_list:
    shape_list3.append(hole)
# new_lines の中から top_corner_line を除外したリストを作成
shape_list3.extend(new_lines)
shape_list3.append([999, 100, 50])

final_shape_list = shape_list3  # 以降は shape_list2 を使用

shape_list4 = [
    ["#ガセットプレート"],
    [30],
    [999],
    [2, gusset_name],
    ["S", 100, 50],
    [800, 1],
    [s1, s2, w3, h1, w5, h1, lc, lt, ly],
    [s1, s2, w3, h2, w5, h2, lc, lt, ly],
    [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
    [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
    [s1, s2, w2, h3, w2, h4, lc, lt, ly],
    [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
    [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
    [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
    [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
    [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
    [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
    [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
    [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
]
# shape_list の生成後、デバッグ情報をリストの先頭に追加する例
debug_info4 = ["debug_info", top_horizontal_line[3] - y_set, h1, bottom_horizontal_line[3] - y_set, h2]
#shape_list.insert(0, debug_info4)
print(debug_info4)
# 動的に生成された孔リストをshape_listに追加
for hole in hole_list:
    shape_list4.append(hole)

# new_lines のリストを shape_list に追加
shape_list4.extend(new_lines)
shape_list4.append([999, 100, 50])

final_shape_list = shape_list4  # そのまま shape_list を使用

if final_shape_type == "shape_list2":
    print("shape_list2 を生成します。")
    print(debug_info2)
    final_shape_list = shape_list2
elif final_shape_type == "shape_list3":
    print("shape_list3 を生成します。")
    print(debug_info3)
    final_shape_list = shape_list3
elif final_shape_type == "shape_list4":
    print("shape_list4 を生成します。")
    print(debug_info4)
    final_shape_list = shape_list4
else:
    print("shape_list を生成します。")
    print(debug_info)
    final_shape_list = shape_list


# 11. 各行をスペース区切りの文字列に変換して最終結果文字列を生成
lines = [" ".join(str(item) for item in row) for row in final_shape_list]
result_str = "\n".join(lines)

final_debug_info = [bottom_horizontal_line[3] - y_set, h2]
final_shape_list.insert(0, debug_info)
print(final_debug_info)  # これでコンソールに出力される

# 12. 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
