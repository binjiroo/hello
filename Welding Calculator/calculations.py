import pyperclip

# 型鋼の名称
steel_name = input("H型鋼のサイズを入力")

# 1. "H-" の部分を取り除き、"x" で分割して値部分のリストを得る
values_str = steel_name.replace("H-", "").split("x")
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

# 各変数の計算
s1 = input()
s2 = input()
w1 = aaa[1] / 2          # 100 / 2 = 50.0
w2 = aaa[2] / 2 + aaa[4]     # (5.5 / 2) + 8 = 10.75
w3 = aaa[2] / 2          # 5.5 / 2 = 2.75
h1 = aaa[0]              # 200
h2 = aaa[3]              # 8
h3 = aaa[0] - aaa[3]       # 200 - 8 = 192
h4 = aaa[3] + aaa[4]       # 8 + 8 = 16
h5 = aaa[0] - aaa[3] - aaa[4] # 200 - 8 - 8 = 184
r  = aaa[4]              # 8
lc = input()
lt = input()
ly = input()

# 型式リストの作成
shape_list = [
    ["#H型鋼断面"],
    [30],
    [999],
    [1, steel_name],
    [s1, s2, 0, 0, 0, -h1, lc, lt, ly],
    [s1, s2, -w1, 0, w1, 0, lc, lt, ly],
    [s1, s2, -w1, -h1, w1, -h1, lc, lt, ly],
    [s1, s2, -w1, -h2, -w2, -h2, lc, lt, ly],
    [s1, s2, w1, -h2, w2, -h2, lc, lt, ly],
    [s1, s2, -w1, -h3, -w2, -h3, lc, lt, ly],
    [s1, s2, w1, -h3, w2, -h3, lc, lt, ly],
    [s1, s2, -w3, -h4, -w3, -h5, lc, lt, ly],
    [s1, s2, w3, -h4, w3, -h5, lc, lt, ly],
    [s1, s2, -w1, 0, -w1, -h2, lc, lt, ly],
    [s1, s2, w1, 0, w1, -h2, lc, lt, ly],
    [s1, s2, -w1, -h1, -w1, -h3, lc, lt, ly],
    [s1, s2, w1, -h1, w1, -h3, lc, lt, ly],
    [s1, s2, -w2, -h4, 0, 90, lc, lt, ly, "E", r],
    [s1, s2, w2, -h4, 90, 180, lc, lt, ly, "E", r],
    [s1, s2, -w2, -h5, 270, 0, lc, lt, ly, "E", r],
    [s1, s2, w2, -h5, 180, 270, lc, lt, ly, "E", r]
]

# 各行をスペース区切りの文字列に変換
lines = [" ".join(str(item) for item in row) for row in shape_list]

# 各行を改行で結合した文字列にする
result_str = "\n".join(lines)

# 結果をクリップボードにコピー
pyperclip.copy(result_str)
print("各行ごとの結果がクリップボードにコピーされました。")
