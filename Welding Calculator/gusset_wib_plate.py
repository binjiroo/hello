import pyperclip

# 型鋼の名称
steel_name = input("親H型鋼のサイズを指定:")  # 例400x200x8x13
sub_steel_name = input("子H型鋼のサイズを指定:")  # 例250x125x6x9
hole_column = int(input("孔の列数"))
hole_pitch = int(input("孔ピッチ"))

# 1."x" で分割して値部分のリストを得る
values_str = steel_name.split("x") + sub_steel_name.split("x")
# 例: values_str は ["400", "200", "8", "13", "250", "125", "6", "9"]

# リスト内包表記で要素を除外
filtered = [v for i, v in enumerate(values_str) if i not in (1, 2, 5, 7)]
# → ["a",d","e","h"]a deh 0346

values_str = filtered

a, b, c, d = values_str

a = values_str[0]  # b
b = values_str[1]  # c
c = values_str[2]  # e
d = values_str[3]  # h

print(a, b, c, d)

# 2. 文字列から数値に変換（小数も扱えるように float に変換）
values = [float(val) for val in values_str]

# 3. 記号に対応する変数として a, b, c を割り当て
a, b, c, d = values

# 5. 最終的なリスト（順番は [a, b] とする）
aaa = [a, b, c, d]

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

t = int(input("板厚を指定"))

# 各変数の計算
s1 = input("s1の値を入力: ")
s2 = input("s2の値を入力: ")
w1 = d / 2  # 例: 100 / 2 = 50.0
w2 = d / 2 + t  # 例: 100/2 - 2.3 = 50 - 2.3 = 47.7
w3 = -d / 2 - 20  # 例: 50 - (2.3 + 4.6) = 50 - 6.9 = 43.1
w4 = d / 2 + t + 20
h1 = a / 2 - b  # 例: 100 / 2 = 50.0
h2 = a / 2 - b - 2  # 例: 50 - 2.3 = 47.7
h3 = a / 2 - c / 2  # 例: 50 - (2.3 + 4.6) = 50 - 6.9 = 43.1
h4 = a / 2 - c / 2
lc = input("lcの値を入力: ")
lt = input("ltの値を入力: ")
ly = input("lyの値を入力: ")

# 型式リストの作成
shape_list = [
    ["#ガセットプレート"],
    [30],
    [999],
    [2, gusset_name],
    ["S", 100, 50],
    [800, 1],
]
# 基本直線（h1, h2 まわり）はそのまま
shape_list.extend(
    [
        [
            s1,
            s2,
            w1 + x_offset,
            h1 + y_offset,
            w2 + x_offset,
            h1 + y_offset,
            lc,
            lt,
            ly,
        ],
        [
            s1,
            s2,
            w1 + x_offset,
            -h2 + y_offset,
            w2 + x_offset,
            -h2 + y_offset,
            lc,
            lt,
            ly,
        ],
        [
            s1,
            s2,
            w1 + x_offset,
            h1 + y_offset,
            w1 + x_offset,
            -h2 + y_offset,
            lc,
            lt,
            ly,
        ],
        [
            s1,
            s2,
            w2 + x_offset,
            h1 + y_offset,
            w2 + x_offset,
            -h2 + y_offset,
            lc,
            lt,
            ly,
        ],
        # [s1, s2, w1 + x_offset, h1 + y_offset, w1 + x_offset, h3_end + y_offset, lc, lt, ly],
        # [s1, s2, w2 + x_offset, h1 + y_offset, w2 + x_offset, h3_end + y_offset, lc, lt, ly],
    ]
)

# 1. 穴と穴の間隔の数を計算（本数－1）
intervals = hole_column - 1
# 2. トータルのスパン (= 間隔数×ピッチ)
span = intervals * hole_pitch
# 3. 開始オフセット（中心から start だけ下方向にずらす）
start = -span / 2

last_bolt_y = None
for i in range(hole_column):
    # ボルト芯の Y 座標
    y_bolt = h4 + start + i * hole_pitch
    last_bolt_y = y_bolt
    shape_list.append(
        [
            s1,
            s2,
            w3 + x_offset,
            y_bolt + y_offset,
            w4 + x_offset,
            y_bolt + y_offset,
            lc,
            lt,
            ly,
        ]
    )

# 3. 最終ボルト列から＋40のY座標を計算
top_line_y = last_bolt_y + 40

shape_list.append(
    [
        s1,
        s2,
        w1 + x_offset,
        top_line_y + y_offset,
        w2 + x_offset,
        top_line_y + y_offset,
        lc,
        lt,
        ly,
    ]
)

shape_list.extend([[999, 100, 50]])

# 各行をスペース区切りの文字列に変換
lines = [" ".join(str(item) for item in row) for row in shape_list]

# 各行を改行で結合した文字列にする
result_str = "\n".join(lines)

# 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
