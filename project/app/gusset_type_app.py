import pyperclip
# app/cannel_size_app.py
from flask import Blueprint, render_template, request
# ── ここまでを追加 ──
cannel_size_bp = Blueprint('gusset_type', __name__,
                           template_folder='templates/gusset_type')
# ── ここまで Blueprint 定義 ──

@cannel_size_bp.route('/', methods=['GET','POST'])
def index():
    # もともとのチャンネルサイズ計算ロジックをここへ丸ごと！
    if request.method == 'POST':
        # …計算コード…
        return render_template('index.html', result=…)
    return render_template('index.html')

# 各H型鋼に固有のr設定用の辞書
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
    # 他のサイズを追加する場合はここにキーと値を設定する
}

# H型鋼のサイズを指定、H-は省略
steel_name = input("親H型鋼のサイズを指定:")

if steel_name in steel_r_mapping:
    r = steel_r_mapping[steel_name]
else:
    print("指定されたサイズが存在しません。")
    r = None  # エラー処理

print(r)

# 型鋼の名称の入力
main_steel_name = steel_name
sub_steel_name = input("子H型鋼を指定:")
gusset_name = input("ガセット名を指定:")

# 1. "x" で分割して文字列リストを取得し、数値に変換
main_values = [float(val) for val in main_steel_name.split("x")]
sub_values = [float(val) for val in sub_steel_name.split("x")]

# 2. パラメータの展開（例：a, b, c, d と e, f, g, h）
a, b, c, d = main_values
e, f, g, h = sub_values

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

hole_column_x = int(input("孔の列数を指定"))
hole_row_y = int(input("孔の行数を指定"))
hole_pitch_x = int(input("列の孔ピッチを指定"))
hole_pitch_y = int(input("行の孔ピッチを指定"))
hole_endpitch_x = int(input("親フランジ端点からの孔ピッチを指定"))
hole_size = int(input("孔径を指定"))

# 6. その他の計算に用いるパラメータの入力・計算
s1 = input("s1の値を入力: ")
s2 = input("s2の値を入力: ")
w1 = (b / 2 - 10) + x_offset         # 例: 100 / 2 = 50.0
w2 = (c / 2) + x_offset              # 例: 100/2 = 50.0
w3 = (c / 2 + r) + x_offset          # 例: 50 + r
w4 = (b / 2 + 50) + x_offset
w5 = (b / 2 + 1) + x_offset
w6 = (b / 2) + x_offset 
h1 = (a / 2 - d) + y_offset          # 例: 100 / 2 = 50.0
h2 = -(a / 2 - (d + 2)) + y_offset    # 例: 50 - 2 = 48.0（概算）
h3 = (a / 2 - (d + r)) + y_offset    # 例: 50 - r
h4 = -(a / 2 - (d + r + 2)) + y_offset
h5 = (a / 2) + y_set + y_offset
h6 = (a / 2) - e + y_set + y_offset
h7 = ((a - e) / 2) + (e / 2) + y_set
h8 = (a - e) - (d + 2)
h9 = (a / 2 - (d + 2))
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

# リスト生成用の共通関数
def create_shape_list(template, hole_list, new_lines):
    shape_list = [row[:] for row in template]  # テンプレートをコピー
    shape_list.extend(hole_list)
    shape_list.extend(new_lines)
    shape_list.append([999, 100, 50])
    return shape_list

# ヘッダー行を含めるかどうかのオプション入力（'y'なら含める）
include_header = input("クリップボードへ ['#ガセットプレート'], [30], [999] を含めますか？ (y/n): ").strip().lower() == 'y'

# ユーザーがヘッダー行を含める場合としない場合で、base_template を分岐させる
if include_header:
    base_template = [
        ["#ガセットプレート"],
        [30],
        [999],
        [2, gusset_name],
        ["S", 100, 50],
        [800, 1],
    ]
else:
    base_template = [
        [2, gusset_name],
        ["S", 100, 50],
        [800, 1],
    ]

# 最終形状リストの決定
if (h1 - (y_last + 40)) <= 0 and ((h9 + y_first) - 40) <= 0:
    final_shape_type = "shape_list4"
    print("shape_list4を選択。")
elif (h1 - (y_last + 40)) >= 0 and ((h9 + y_first) - 40) < 0:
    final_shape_type = "shape_list3"
    print("shape_list3を選択。")
elif (h1 - (y_last + 40)) < 0 and ((h9 + y_first) - 40) >= 0:
    final_shape_type = "shape_list2"
    print("shape_list2を選択。")
else:
    final_shape_type = "shape_list"
    print("shape_listを選択。")

# 使用するmodeを入力
mode = int(input("モードを選択（mood1=1、mood2=2、mood3=3）: "))

# modeとshapeごとの設定テンプレートを定義（各shapeで異なる要素のみ変更）
mode_templates = {
    1: {
        "shape_list": [
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
        ],
        "shape_list2": [
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
        ],
        "shape_list3": [
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
        ],
        "shape_list4": [
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
    },
    2: {  # mode2では異なる設定を指定可能（現状は例として同じ設定を使用）
        # mode2独自の設定に書き換え可能
        "shape_list": [
            [s1, s2, w3, h1, w6, h1, lc, lt, ly],
            [s1, s2, w3, h2, w6, h2, lc, lt, ly],
            [s1, s2, w2, h3, w2, h4, lc, lt, ly],
            [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
            [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
            [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
            [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
            [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
            [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
            [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
            [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list2": [
            [s1, s2, w3, h1, w5, h1, lc, lt, ly],
            [s1, s2, w3, h2, w6, h2, lc, lt, ly],
            [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
            [s1, s2, w2, h3, w2, h4, lc, lt, ly],
            [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
            [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
            [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
            [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
            [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
            [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
            [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
            [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list3": [
            [s1, s2, w3, h1, w6, h1, lc, lt, ly],
            [s1, s2, w3, h2, w5, h2, lc, lt, ly],
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
        ],
        "shape_list4": [
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
    },
    3: {  # mode2では異なる設定を指定可能（現状は例として同じ設定を使用）
        # mode2独自の設定に書き換え可能
        "shape_list": [
            [s1, s2, w3, h1, w6, h1, lc, lt, ly],
            [s1, s2, w3, h2, w6, h2, lc, lt, ly],
            [s1, s2, w2, h3, w2, h4, lc, lt, ly],
            [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
            [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
            [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
            [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
            [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
            [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
            [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
            [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list2": [
            [s1, s2, w3, h1, w5, h1, lc, lt, ly],
            [s1, s2, w3, h2, w6, h2, lc, lt, ly],
            [s1, s2, w2, h3, w2, h4, lc, lt, ly],
            [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
            [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
            [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
            [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
            [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
            [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
            [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
            [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
            [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list3": [
            [s1, s2, w3, h1, w6, h1, lc, lt, ly],
            [s1, s2, w3, h2, w5, h2, lc, lt, ly],
            [s1, s2, w2, h3, w2, h4, lc, lt, ly],
            [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
            [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
            [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
            [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
            [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
            [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
            [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
            [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
            [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
        ],
        "shape_list4": [
            [s1, s2, w3, h1, w5, h1, lc, lt, ly],
            [s1, s2, w3, h2, w5, h2, lc, lt, ly],
            [s1, s2, w2, h3, w2, h4, lc, lt, ly],
            [s1, s2, w5, h1, w5, y_last + 40, lc, lt, ly],
            [s1, s2, w5, h2, w5, y_first - 40, lc, lt, ly],
            [s1, s2, w3, h3, 90, 180, lc, lt, ly, "E", r],
            [s1, s2, w3, h4, 180, 270, lc, lt, ly, "E", r],
            [s1, s2, -w3, h1, -w1, h1, lc, lt, ly],
            [s1, s2, -w3, h2, -w1, h2, lc, lt, ly],
            [s1, s2, -w1, h1, -w1, h2, lc, lt, ly],
            [s1, s2, -w2, h3, -w2, h4, lc, lt, ly],
            [s1, s2, -w3, h3, 0, 90, lc, lt, ly, "E", r],
            [s1, s2, -w3, h4, 270, 0, lc, lt, ly, "E", r],
        ],
    }
}

new_lines = []

if mode == 1:
    # 元々の条件 (mode 1用)
    if (h1 - (y_last + 40)) > 0:
        print("mood1:上面切欠き")
        print((h1 - (y_last + 40)) > 0)
        print(h1 - (y_last + 40))
        top_horizontal_line = [
            s1, s2, w6, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
        ]
    else:
        print("mood1:上面突出し。")
        print((h1 - (y_last + 40)) > 0)
        print(h1 - (y_last + 40))
        top_horizontal_line = [
            s1, s2, w5, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
        ]
    new_lines.append(top_horizontal_line)

    if ((h9 + y_first) - 40) > 0:
        print("mood1:下面切欠き。")
        print((h9 + y_first) - 40 > 0)
        print((h9 + y_first) - 40)
        bottom_horizontal_line = [
            s1, s2, w6, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
        ]
    else:
        print("mood1:下面突出し。")
        print((h9 + y_first) - 40 > 0)
        print((h9 + y_first) - 40)
        bottom_horizontal_line = [
            s1, s2, w5, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
        ]
    new_lines.append(bottom_horizontal_line)

    right_vertical_line = [
        s1, s2, x_last + 40, y_first - 40, x_last + 40, y_last + 25, lc, lt, ly
    ]
    new_lines.append(right_vertical_line)

    cut_line = [
        s1, s2, x_last + 25, y_last + 40, x_last + 40, y_last + 25, lc, lt, ly
    ]
    new_lines.append(cut_line)

    # 角丸線の追加条件をフラグに基づいて行う
    if final_shape_type in ["shape_list", "shape_list3"]:
        print("top_corner_lineが選択されました。")
        top_corner_line = [s1, s2, w6, y_last + 50, 180, 270, lc, lt, ly, "E", 10, 0]
        new_lines.append(top_corner_line)
        
    if final_shape_type in ["shape_list", "shape_list2"]:
        print("bottom_corner_lineが選択されました。")
        bottom_corner_line = [s1, s2, w6, y_first - 50, 90, 180, lc, lt, ly, "E", 10, 0]
        new_lines.append(bottom_corner_line)

elif mode == 2:
    # top_horizontal_line (mode2用)
    if (- d - y_set + y_offset) > 0:
        print("mood2:上面斜め。")
        print((- d - y_set + y_offset) - (r + 10))
        top_horizontal_line = [
            s1, s2, w6, h1, x_last + 40, h5, lc, lt, ly
        ]
        new_lines.append(top_horizontal_line)
    else:
        print("mood2:上面突出し。")
        print(- d - y_set + y_offset)
        top_horizontal_line = [
            s1, s2, w5, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
        ]
        cut_line = [
            s1, s2, x_last + 25, y_last + 40, x_last + 40, y_last + 25, lc, lt, ly
        ]
        new_lines.append(top_horizontal_line)
        new_lines.append(cut_line)

    # bottom_horizontal_lineとright_vertical_line (mode2用)
    if (h8 + y_set + y_offset) > 0:
        print("mood2:下面斜め。")
        print((h8 + y_set + y_offset) - (r + 10))
        bottom_horizontal_line = [
            s1, s2, w6, h2, x_last + 40, h6, lc, lt, ly
        ]
        new_lines.append(bottom_horizontal_line)
    else:
        print("mood2:下面突出し。")
        print(h8 + y_set + y_offset)
        bottom_horizontal_line = [
            s1, s2, w5, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
        ]
        new_lines.append(bottom_horizontal_line)

    #mode = int(input("モードを選択（元々の条件=1、新しい条件=2）: "))

    # 条件フラグを設定
    cond1 = (- d - y_set + y_offset) < 0
    cond2 = (h8 + y_set + y_offset) < 0

    # 4通りのケースで分岐
    if cond1 and cond2:
        # 両方とも True の場合
        # この場合の right_vertical_line の設定を（例として）行う
        right_vertical_line = [s1, s2, x_last + 40, y_last + 25, x_last + 40, y_first - 40, lc, lt, ly]
        new_lines.append(right_vertical_line)
        print("両方とも True")
    elif (not cond1) and (not cond2):
        # 両方とも False の場合
        right_vertical_line = [s1, s2, x_last + 40, h7, x_last + 40, y_first - 40, lc, lt, ly]
        new_lines.append(right_vertical_line)
        print("両方とも False")
    elif cond1 and (not cond2):
        # 条件1のみ True の場合
        right_vertical_line = [s1, s2, x_last + 40, y_last + 25, x_last + 40, h6, lc, lt, ly]
        new_lines.append(right_vertical_line)
        print("条件1のみ True")
    elif (not cond1) and cond2:
        # 条件2のみ True の場合
        right_vertical_line = [s1, s2, x_last + 40, h5, x_last + 40, y_first - 40, lc, lt, ly]
        new_lines.append(right_vertical_line)
        print("条件2のみ True")
    else:
        # 万が一のためのデフォルト値
        right_vertical_line = []
        new_lines.append(right_vertical_line)

elif mode == 3:
    # 元々の条件 (mode 3用)
    if (- d - y_set + y_offset) > 0:
        print("mood3:上面斜め。")
        print(h1 - (y_last + 40))
        print(- d - y_set + y_offset)
        top_horizontal_line = [
            s1, s2, w6, h1, x_last + 40, h5, lc, lt, ly
        ]
        new_lines.append(top_horizontal_line)
    else:
        print("mood3:上面切欠き。")
        print(h1 - (y_last + 40))
        print(- d - y_set + y_offset)
        top_horizontal_line = [
            s1, s2, w5, y_last + 40, x_last + 25, y_last + 40, lc, lt, ly
        ]
        new_lines.append(top_horizontal_line)

    # 元々の条件 (mode 3用)
    if (h8 + y_set + y_offset) > 0:
        print("mood3:下面斜め。")
        print(h1 - (y_last + 40))
        print(- d - y_set + y_offset)
        bottom_horizontal_line = [
            s1, s2, w6, h2, x_last + 40, h6, lc, lt, ly
        ]
        new_lines.append(bottom_horizontal_line)
    else:
        print("mood3:下面切欠き。")
        print(h1 - (y_last + 40))
        print(- d - y_set + y_offset)
        bottom_horizontal_line = [
            s1, s2, w5, y_first - 40, x_last + 40, y_first - 40, lc, lt, ly
        ]
        new_lines.append(bottom_horizontal_line)

    # 条件フラグを設定
    cond1 = (- d - y_set + y_offset) < 0
    cond2 = (h8 + y_set + y_offset) < 0
    print("cond1=", cond1)
    print("cond2=", cond2)
    print(- d - y_set + y_offset) #上フランジから梁上
    print(h8 + y_set + y_offset) #下フランジから梁下
    print(h1 - (y_last + 40)) #上フランジから切端
    print((h9 + y_first) - 40) #下フランジから切端
    print(h1 - y_last) #上フランジから孔芯
    print(h9 + y_first) #下フランジから孔芯
    print( y_last) #基準点から上端孔
    print( y_first) #基準点から下端孔

    # 4通りのケースで分岐
    if cond1 and cond2:
        right_vertical_line = [s1, s2, x_last + 40, y_last + 25, x_last + 40, y_first - 40, lc, lt, ly]
        # 角丸線の追加条件をフラグに基づいて行う
        cut_line = [
            s1, s2, x_last + 25, y_last + 40, x_last + 40, y_last + 25, lc, lt, ly
        ]
        new_lines.append(right_vertical_line)
        new_lines.append(cut_line)
        print("両方とも True")
    elif (not cond1) and (not cond2):
        # 両方とも False の場合
        right_vertical_line = [s1, s2, x_last + 40, h7, x_last + 40, h6, lc, lt, ly]
        # 角丸線の追加条件をフラグに基づいて行う
        new_lines.append(right_vertical_line)
        print("両方とも False")
    elif cond1 and (not cond2):
        right_vertical_line = [s1, s2, x_last + 40, y_last + 25, x_last + 40, h6, lc, lt, ly]
        cut_line = [
            s1, s2, x_last + 25, y_last + 40, x_last + 40, y_last + 25, lc, lt, ly
        ]
        new_lines.append(right_vertical_line)
        new_lines.append(cut_line)
        print("条件1のみTrue")
    elif cond2 and (not cond1):
        # 両方とも False の場合
        right_vertical_line = [s1, s2, x_last + 40, h7, x_last + 40, y_first - 40, lc, lt, ly]
        # 角丸線の追加条件をフラグに基づいて行う
        new_lines.append(right_vertical_line)
        print("条件2のみTrue")
    else:
        # 万が一のためのデフォルト値
        right_vertical_line = []
        new_lines.append(right_vertical_line)
    
selected_template = base_template + mode_templates[mode][final_shape_type]

debug_info = ["debug_info", top_horizontal_line[3] - y_set, h1, bottom_horizontal_line[3] - y_set, h2]
print(debug_info)

# リスト作成関数を呼び出す
final_shape_list = create_shape_list(selected_template, hole_list, new_lines)

# 各行をスペース区切りの文字列に変換
result_str = "\n".join(" ".join(str(item) for item in row) for row in final_shape_list)

# 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
