import ast
import io
import sys
import tokenize
from token import tok_name


def read_source_from_file(path: str) -> str:
    """指定されたファイルからソースコードを読み込む"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_source_from_stdin() -> str:
    """標準入力からソースコードを読み込む（パイプで渡す用）"""
    return sys.stdin.read()


def read_default_source() -> str:
    """引数がないとき用のデフォルトサンプルコード"""
    return """\
import math

x = 10

def f(a):
    y = a + x
    return y

f(5)
"""


def show_tokens(source: str) -> None:
    """tokenize.generate_tokens を使ってトークンを可視化"""
    print("=== Tokens (tokenize) ===")
    reader = io.StringIO(source).readline

    for tok in tokenize.generate_tokens(reader):
        ttype = tok.type
        tname = tok_name.get(ttype, str(ttype))
        tstring = tok.string
        start_line, start_col = tok.start
        end_line, end_col = tok.end

        # 改行やインデント系は分かりやすいようにreprで表示
        display_str = repr(tstring)

        print(
            f"{tname:<12} "
            f"str={display_str:<10} "
            f"start=({start_line:>2},{start_col:<2}) "
            f"end=({end_line:>2},{end_col:<2})"
        )

    print()  # 空行


def show_ast(source: str, filename: str = "<input>") -> None:
    """ast.parse + ast.dump でASTを可視化"""
    print("=== AST (ast.parse / ast.dump) ===")
    tree = ast.parse(source, filename=filename, mode="exec")

    # include_attributes=True で lineno / col_offset なども表示
    dumped = ast.dump(tree, indent=2, include_attributes=True)
    print(dumped)
    print()


def main():
    # 1. ソースの取得方法：
    #   - 引数あり: ファイルパスとして扱う
    #   - 引数なし & 標準入力がパイプ: stdinから読む
    #   - それ以外: デフォルトのサンプルコードを使う
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
        source = read_source_from_file(filename)
    else:
        # 標準入力からコードが渡されているかチェック
        if not sys.stdin.isatty():
            filename = "<stdin>"
            source = read_source_from_stdin()
        else:
            filename = "<sample>"
            source = read_default_source()

    print(f"# Inspecting: {filename}\n")
    show_tokens(source)
    show_ast(source, filename=filename)


if __name__ == "__main__":
    main()
