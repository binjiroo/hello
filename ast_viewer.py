import tkinter as tk
from tkinter import ttk, messagebox


class ASTViewer(tk.Tk):
    """
    AST テキスト（ast.dump(indent=2) のようなインデント付き表現）を
    インデントレベルに応じてツリー表示する簡易ビューア。

    機能:
      - ノード種別ごとに背景色
      - キーワード検索
      - 検索結果リスト:
          ・左: "N. ラベル" ボタン（クリックで該当ノードへジャンプ）
          ・中: 親階層ごとのカラーボタン（クリックでメインASTツリーの該当親ノードを開閉）
          ・右: 行全体トグルボタン（その行の親チェーンを一括開閉）
      - 検索結果全体を 1 つのトグルボタンで一括展開／一括折りたたみ
      - ツリーで選択した行に対応する AST テキスト行のハイライト
          ・選択行のみ
          ・親パスも含めて
          ・チェックボックスで ON/OFF 切り替え
      - 現在選択中ノードまでのパス表示（AST Root / Module / body / ...）
    """

    def __init__(self):
        super().__init__()

        self.title("AST Viewer")
        self.geometry("1200x750")

        # 検索結果の各行 Frame を保持（再検索時に destroy 用）
        self.result_rows = []               # list[ttk.Frame]
        # 各行ごとの「(node_id, btn) のリスト」を保持（全体一括操作用）
        self.row_toggle_groups = []         # list[list[tuple[str, tk.Button]]]
        # 各行の「行全体トグルボタン」を保持
        self.row_all_buttons = []           # list[tk.Button]

        # ★ 選択行／親パスのハイライト ON/OFF フラグ
        self.highlight_current_var = tk.BooleanVar(value=True)    # 選択行
        self.highlight_ancestors_var = tk.BooleanVar(value=True)  # 親パス

        # ------------------------------
        # 全体レイアウト：左右に分割
        # ------------------------------
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # ==========================
        # 左側：AST テキスト入力
        # ==========================
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        label_input = ttk.Label(
            left_frame,
            text="AST テキストを貼り付け（例: ast.dump(tree, indent=2)）"
        )
        label_input.pack(anchor="w", padx=5, pady=(5, 0))

        input_area = ttk.Frame(left_frame)
        input_area.pack(fill="both", expand=True, padx=5, pady=5)

        self.ast_text = tk.Text(input_area, wrap="none")
        yscroll_in = ttk.Scrollbar(input_area, orient="vertical", command=self.ast_text.yview)
        xscroll_in = ttk.Scrollbar(input_area, orient="horizontal", command=self.ast_text.xview)
        self.ast_text.configure(yscrollcommand=yscroll_in.set, xscrollcommand=xscroll_in.set)

        self.ast_text.grid(row=0, column=0, sticky="nsew")
        yscroll_in.grid(row=0, column=1, sticky="ns")
        xscroll_in.grid(row=1, column=0, sticky="ew")

        input_area.rowconfigure(0, weight=1)
        input_area.columnconfigure(0, weight=1)

        # 変換／置換ボタン用の横並びフレーム
        button_row = ttk.Frame(left_frame)
        button_row.pack(anchor="w", padx=5, pady=(0, 5))

        # AST変換ボタン
        convert_button = ttk.Button(
            button_row,
            text="AST変換",
            command=self.convert_ast_to_tree
        )
        convert_button.pack(side="left", padx=(0, 5))

        # AST置換ボタン（クリップボードでテキスト全置換）
        clipboard_button = ttk.Button(
            button_row,
            text="AST置換",
            command=self.replace_with_clipboard
        )
        clipboard_button.pack(side="left")

        # ==========================
        # 右側：AST ツリー + 検索
        # ==========================
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        # --- 検索 UI ---
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill="x", padx=5, pady=(5, 0))

        ttk.Label(search_frame, text="検索キーワード:").pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left")

        search_button = ttk.Button(
            search_frame,
            text="検索実行",
            command=self.search_ast_nodes
        )
        search_button.pack(side="left", padx=(5, 0))

        # ★ ハイライトモード切り替えチェックボックス
        highlight_frame = ttk.Frame(right_frame)
        highlight_frame.pack(fill="x", padx=5, pady=(2, 0))

        chk_current = ttk.Checkbutton(
            highlight_frame,
            text="選択行をハイライト",
            variable=self.highlight_current_var,
            command=self.refresh_highlight_from_selection,
        )
        chk_current.pack(side="left")

        chk_ancestors = ttk.Checkbutton(
            highlight_frame,
            text="親パスもハイライト",
            variable=self.highlight_ancestors_var,
            command=self.refresh_highlight_from_selection,
        )
        chk_ancestors.pack(side="left", padx=(10, 0))

        # --- メイン AST ツリー ---
        label_tree = ttk.Label(right_frame, text="AST ツリー（ノード種別ごとに色分け）")
        label_tree.pack(anchor="w", padx=5, pady=(5, 0))

        tree_area = ttk.Frame(right_frame)
        tree_area.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(tree_area, show="tree")
        yscroll_tree = ttk.Scrollbar(tree_area, orient="vertical", command=self.tree.yview)
        xscroll_tree = ttk.Scrollbar(tree_area, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll_tree.set, xscrollcommand=xscroll_tree.set)

        # Treeviewの選択変更イベントにハンドラをバインド
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll_tree.grid(row=0, column=1, sticky="ns")
        xscroll_tree.grid(row=1, column=0, sticky="ew")

        tree_area.rowconfigure(0, weight=1)
        tree_area.columnconfigure(0, weight=1)

        # メイン AST ルート
        self.root_node = self.tree.insert("", "end", text="AST Root", open=True)

        # タグごとの色設定
        self.setup_tree_tags()

        # --- 検索結果ヘッダ（件数表示＋全体トグル） ---
        header_frame = ttk.Frame(right_frame)
        header_frame.pack(anchor="w", padx=5, pady=(0, 2))

        self.result_label = ttk.Label(header_frame, text="検索結果: 0件")
        self.result_label.pack(side="left")

        # 検索結果全体を一括開閉するトグルボタン（色付き）
        self.global_toggle_btn = tk.Button(header_frame, state="disabled")
        # 初期状態は「閉じている」想定（水色＋）
        self.style_toggle_button(self.global_toggle_btn, is_open=False)
        self.global_toggle_btn.configure(
            command=self.toggle_all_results
        )
        self.global_toggle_btn.pack(side="left", padx=(6, 0))

        # --- 検索結果の各行を並べるフレーム（スクロール付き） ---
        self.result_outer = ttk.Frame(right_frame)
        self.result_outer.pack(fill="x", padx=5, pady=(0, 5), anchor="w")

        # Canvas + Frame でスクロール領域を作る
        self.result_canvas = tk.Canvas(self.result_outer, height=160)
        self.result_canvas.pack(side="left", fill="x", expand=True)

        result_scrollbar = ttk.Scrollbar(
            self.result_outer,
            orient="vertical",
            command=self.result_canvas.yview
        )
        result_scrollbar.pack(side="right", fill="y")

        self.result_canvas.configure(yscrollcommand=result_scrollbar.set)

        # Canvas の中に実際の行を並べる Frame を置く
        self.result_frame = ttk.Frame(self.result_canvas)
        self.result_canvas.create_window(
            (0, 0),
            window=self.result_frame,
            anchor="nw"
        )

        # 中身のサイズが変わったらスクロール範囲を更新
        def _on_result_frame_configure(event):
            self.result_canvas.configure(
                scrollregion=self.result_canvas.bbox("all")
            )

        self.result_frame.bind("<Configure>", _on_result_frame_configure)

        # TreeviewノードID → ASTテキストの行番号 の対応を保存する dict
        self.node_to_line = {}

        # ★ 現在選択中ノードまでのパス表示用
        self.path_var = tk.StringVar(value="パス: ")
        self.path_label = ttk.Label(right_frame, textvariable=self.path_var)
        self.path_label.pack(anchor="w", padx=5, pady=(0, 5))

    # ----------------------------------------
    # Treeview 選択時の処理
    # ----------------------------------------
    def on_tree_select(self, event):
        """
        Treeviewで選択されたノードに対応するASTテキスト行を、
        （設定に応じて）ハイライトし、パスも表示する。
        """
        selection = self.tree.selection()
        if not selection:
            return

        node_id = selection[0]

        # テキスト側ハイライト更新
        self.update_text_highlight(node_id)
        # パス表示更新
        self.update_path_label(node_id)

    def update_path_label(self, node_id):
        """
        AST Root から選択ノードまでのパスを表示用文字列にしてラベルに反映する。
        """
        parts = []
        cur = node_id
        while cur:
            text = self.tree.item(cur, "text")
            parts.append(text)
            cur = self.tree.parent(cur)

        parts.reverse()  # AST Root → ... → 選択ノード の順に
        path_str = " / ".join(parts)
        self.path_var.set("パス: " + path_str)

    # ----------------------------------------
    # ASTテキスト側のハイライト処理
    # ----------------------------------------
    def _get_kind_tag_from_tree(self, node_id):
        """
        Treeviewノードに付いているタグから、
        module/import/class/method/function/other のいずれかを返す。
        見つからなければ None。
        """
        node_tags = self.tree.item(node_id, "tags")
        for t in node_tags:
            if t in ("module", "import", "class", "method", "function", "other"):
                return t
        return None

    def update_text_highlight(self, node_id):
        """
        指定ノードと、その親チェーン（設定に応じて）を
        ASTテキスト側でハイライトする。
        """

        # 既存の背景色タグを全部消す
        for tag in ("module", "import", "class", "method", "function", "other"):
            self.ast_text.tag_remove(tag, "1.0", "end")

        # 何もハイライトしない設定なら終了
        if not self.highlight_current_var.get() and not self.highlight_ancestors_var.get():
            return

        # --- 1. 選択ノードの行をハイライト ---
        if self.highlight_current_var.get():
            line_no = self.node_to_line.get(node_id)
            if line_no is not None:
                kind_tag = self._get_kind_tag_from_tree(node_id)
                if kind_tag:
                    start = f"{line_no}.0"
                    end = f"{line_no}.end"
                    self.ast_text.tag_add(kind_tag, start, end)
                    self.ast_text.see(start)

        # --- 2. 親パスをハイライト ---
        if self.highlight_ancestors_var.get():
            cur = self.tree.parent(node_id)
            while cur:
                line_no = self.node_to_line.get(cur)
                if line_no is not None:
                    kind_tag = self._get_kind_tag_from_tree(cur)
                    if kind_tag:
                        start = f"{line_no}.0"
                        end = f"{line_no}.end"
                        self.ast_text.tag_add(kind_tag, start, end)
                cur = self.tree.parent(cur)

    def refresh_highlight_from_selection(self):
        """
        チェックボックスの状態変更時に、
        現在の選択ノードに合わせてハイライトを更新する。
        """
        selection = self.tree.selection()
        if not selection:
            # 何も選ばれていないときは、単にハイライトを全部消す
            for tag in ("module", "import", "class", "method", "function", "other"):
                self.ast_text.tag_remove(tag, "1.0", "end")
            return

        node_id = selection[0]
        self.update_text_highlight(node_id)

    # ----------------------------------------
    # タグごとの色設定（背景色＋文字色）
    # ----------------------------------------
    def setup_tree_tags(self):
        """
        メイン Treeview のタグと色の対応を設定する。
        """
        self.tree.tag_configure("module",
                                background="#e6f2ff",  # 薄い青
                                foreground="#000000")
        self.tree.tag_configure("import",
                                background="#f0e6ff",  # 薄い紫
                                foreground="#000000")
        self.tree.tag_configure("class",
                                background="#e6ffe6",  # 薄い緑
                                foreground="#000000")
        self.tree.tag_configure("method",
                                background="#fff2e6",  # 薄いオレンジ
                                foreground="#000000")
        self.tree.tag_configure("function",
                                background="#fff8e6",  # 薄い黄
                                foreground="#000000")
        self.tree.tag_configure("other",
                                background="#ffffff",  # 白
                                foreground="#000000")

        # 検索ヒット強調用
        self.tree.tag_configure("search_hit",
                                foreground="#d62728",
                                font=("TkDefaultFont", 9, "bold"))

        # ASTテキスト側のハイライト用タグ（Treeviewと同じ色）
        self.ast_text.tag_configure("module",   background="#e6f2ff")
        self.ast_text.tag_configure("import",   background="#f0e6ff")
        self.ast_text.tag_configure("class",    background="#e6ffe6")
        self.ast_text.tag_configure("method",   background="#fff2e6")
        self.ast_text.tag_configure("function", background="#fff8e6")
        self.ast_text.tag_configure("other",    background="#f5f5f5")

    # ----------------------------------------
    # トグルボタンの見た目（色＋記号）を制御
    # ----------------------------------------
    def style_toggle_button(self, btn, is_open):
        """
        開閉状態に応じてボタンの色と記号を設定する。

        is_open = False → 水色に白い「+」
        is_open = True  → ピンクに白い「-」
        """
        if is_open:
            btn.config(
                text="-",
                bg="#ff99c8",           # ピンク系
                fg="white",
                activebackground="#ff7aa2",
                activeforeground="white",
                relief="flat",
                bd=1,
                width=2
            )
        else:
            btn.config(
                text="+",
                bg="#89c2ff",           # 水色系
                fg="white",
                activebackground="#4ea8de",
                activeforeground="white",
                relief="flat",
                bd=1,
                width=2
            )

    def is_node_open(self, node_id):
        """Treeview の open 状態を bool で返す。"""
        return bool(self.tree.item(node_id, "open"))

    def open_parents(self, nid):
        """指定ノードの親チェーンをすべて open=True にする。"""
        parent = self.tree.parent(nid)
        while parent:
            self.tree.item(parent, open=True)
            parent = self.tree.parent(parent)

    # ----------------------------------------
    # ノード種別の判定ロジック
    # ----------------------------------------
    def classify_node(self, label, parent_kind):
        """
        行テキストと親ノード種別から、このノードを
        module/import/class/method/function/other のどれに分類するか決める。
        """
        head = label.split("(", 1)[0]

        if head == "Module":
            return "module"
        if head in ("Import", "ImportFrom"):
            return "import"
        if head == "ClassDef":
            return "class"
        if head in ("FunctionDef", "AsyncFunctionDef"):
            if parent_kind == "class":
                return "method"
            else:
                return "function"
        return "other"

    # ----------------------------------------
    # AST テキスト → メインツリー変換
    # ----------------------------------------
    def convert_ast_to_tree(self):
        """
        テキストエリアの AST 表現を行単位で読み込み、
        インデント数とノード種別をもとにメイン Treeview の階層構造を構築する。
        """
        text = self.ast_text.get("1.0", "end").rstrip("\n")

        # メイン AST ツリーをクリア（Root の配下だけ消す）
        for child in self.tree.get_children(self.root_node):
            self.tree.delete(child)

        # ノードID → 行番号 の対応もリセット
        self.node_to_line.clear()

        # 検索結果もクリア
        self.clear_search_results()
        self.clear_search_hit_tags()
        self.result_label.config(text="検索結果: 0件")

        if not text.strip():
            return

        lines = text.splitlines()

        # スタックには (indent_level, node_id, kind) を積む
        stack = [(-1, self.root_node, "root")]

        for line_no, raw_line in enumerate(lines, start=1):
            if not raw_line.strip():
                continue

            indent = len(raw_line) - len(raw_line.lstrip(" "))
            label = raw_line.strip()

            while stack and indent <= stack[-1][0]:
                stack.pop()

            if not stack:
                parent_indent, parent_id, parent_kind = -1, self.root_node, "root"
                stack = [(-1, self.root_node, "root")]
            else:
                parent_indent, parent_id, parent_kind = stack[-1]

            kind = self.classify_node(label, parent_kind)

            node_id = self.tree.insert(
                parent_id,
                "end",
                text=label,
                open=False,
                tags=(kind,)
            )

            # ノードID → 行番号 を保存
            self.node_to_line[node_id] = line_no
            stack.append((indent, node_id, kind))

    def replace_with_clipboard(self):
        """
        クリップボード内のテキストで AST テキストエリア全体を置き換える。
        """
        try:
            text = self.clipboard_get()
        except tk.TclError:
            messagebox.showwarning(
                "クリップボードエラー",
                "クリップボードからテキストを取得できませんでした。"
            )
            return

        if not text:
            # 空文字の場合も一応確認する
            if not messagebox.askyesno(
                "確認",
                "クリップボードが空のようです。テキストエリアを空にしてもよいですか？"
            ):
                return

        # ASTテキストエリアをクリップボードの内容で全置換
        self.ast_text.delete("1.0", "end")
        self.ast_text.insert("1.0", text)

    # ----------------------------------------
    # 検索結果クリア + ヒット強調クリア
    # ----------------------------------------
    def clear_search_results(self):
        """検索結果の行 Frame と管理リストを破棄。"""
        for row in self.result_rows:
            row.destroy()
        self.result_rows.clear()
        self.row_toggle_groups.clear()
        self.row_all_buttons.clear()

        # 全体トグルボタンをリセットして無効化
        self.style_toggle_button(self.global_toggle_btn, is_open=False)
        self.global_toggle_btn.config(state="disabled")

    def clear_search_hit_tags(self):
        """
        メインツリーのすべてのノードから search_hit タグだけを除去。
        """
        def walk(node_id):
            tags = list(self.tree.item(node_id, "tags"))
            if "search_hit" in tags:
                tags.remove("search_hit")
                self.tree.item(node_id, tags=tuple(tags))
            for child in self.tree.get_children(node_id):
                walk(child)

        for child in self.tree.get_children(self.root_node):
            walk(child)

    # ----------------------------------------
    # 検索＆検索結果リスト構築
    # ----------------------------------------
    def search_ast_nodes(self):
        """
        メインツリー内のすべてのノードから、テキストに
        キーワードを含むものを見つけて、検索結果リストを作成する。
        """
        query = self.search_var.get().strip()
        if not query:
            return

        query_lower = query.lower()

        # 既存ヒット強調を解除＆検索結果UIをクリア
        self.clear_search_hit_tags()
        self.clear_search_results()

        hits = []

        # メインツリー全ノードを DFS で巡回
        def walk(node_id):
            text = self.tree.item(node_id, "text")
            if query_lower in text.lower():
                hits.append(node_id)
            for child in self.tree.get_children(node_id):
                walk(child)

        for child in self.tree.get_children(self.root_node):
            walk(child)

        self.result_label.config(text=f"検索結果: {len(hits)}件")

        # メインツリー側でヒットを強調
        for nid in hits:
            tags = list(self.tree.item(nid, "tags"))
            if "search_hit" not in tags:
                tags.append("search_hit")
            self.tree.item(nid, tags=tuple(tags))

        # 検索結果リストに行を追加
        for idx, nid in enumerate(hits, start=1):
            self.create_result_row(idx, nid)

        # 全体トグルボタンの状態更新
        if self.row_toggle_groups:
            self.global_toggle_btn.config(state="normal")
            all_nodes = [nid for group in self.row_toggle_groups for (nid, _) in group]
            all_open = all(self.is_node_open(nid) for nid in all_nodes)
            self.style_toggle_button(self.global_toggle_btn, is_open=all_open)
        else:
            self.global_toggle_btn.config(state="disabled")
            self.style_toggle_button(self.global_toggle_btn, is_open=False)

        # ヒットが1件だけなら自動ジャンプ
        if len(hits) == 1:
            self.focus_on_tree_item(hits[0])

    # ----------------------------------------
    # 検索結果 1行分の UI
    # ----------------------------------------
    def create_result_row(self, index, node_id):
        """
        検索結果の1行を作成する。
        - 左: "N. ラベル" ボタン（クリックでそのノードにジャンプ）
        - 中: 親階層ごとのカラーボタン（クリックでメインツリーの該当親ノードを開閉）
        - 右: 行全体トグルボタン（その行の親チェーンを一括開閉）
        """
        row = ttk.Frame(self.result_frame)
        row.pack(fill="x", anchor="w")
        self.result_rows.append(row)

        label_text = self.tree.item(node_id, "text")

        # 1. 行番号 + テキスト部分（ボタンにしてジャンプ）
        btn_jump = ttk.Button(
            row,
            text=f"{index}. {label_text}",
            command=lambda nid=node_id: self.focus_on_tree_item(nid)
        )
        btn_jump.pack(side="left", padx=(0, 5))

        # 2. 親階層をたどって、各階層ごとのトグルボタンを右側に並べる
        parents = []
        cur = node_id
        while True:
            parent = self.tree.parent(cur)
            if not parent or parent == self.root_node:
                break
            parents.append(parent)
            cur = parent

        row_toggles = []

        for anc_id in parents:
            btn = tk.Button(row)
            self.style_toggle_button(btn, self.is_node_open(anc_id))
            btn.configure(
                command=lambda nid=anc_id, btn_obj=btn: self.toggle_ancestor(nid, btn_obj)
            )
            btn.pack(side="left", padx=(2, 0))
            row_toggles.append((anc_id, btn))

        if row_toggles:
            self.row_toggle_groups.append(row_toggles)

            # 3. 行全体トグルボタン（この行の親チェーンを一括開閉）
            all_open = all(self.is_node_open(nid) for nid, _ in row_toggles)
            row_all_btn = tk.Button(row)
            self.style_toggle_button(row_all_btn, all_open)
            row_all_btn.configure(
                command=lambda toggles=row_toggles, btn_obj=row_all_btn: self.toggle_row_all(
                    toggles, btn_obj
                )
            )
            row_all_btn.pack(side="left", padx=(6, 0))
            self.row_all_buttons.append(row_all_btn)

    # ----------------------------------------
    # 親階層 1つ分のトグル
    # ----------------------------------------
    def toggle_ancestor(self, node_id, btn):
        """
        親階層用ボタンが押されたときに、
        メインASTツリーの該当ノードを開閉し、
        ボタンの色と記号も更新する。
        """
        current = self.is_node_open(node_id)
        new_state = not current

        self.tree.item(node_id, open=new_state)

        if new_state:
            self.open_parents(node_id)

        self.tree.see(node_id)
        self.style_toggle_button(btn, new_state)

        # 行全体トグルボタンの見た目を更新
        for group_idx, row_toggles in enumerate(self.row_toggle_groups):
            nids = [nid for nid, _ in row_toggles]
            if node_id in nids:
                all_open = all(self.is_node_open(nid) for nid, _ in row_toggles)
                if group_idx < len(self.row_all_buttons):
                    self.style_toggle_button(self.row_all_buttons[group_idx], all_open)
                break

        # 全体トグルボタンの見た目も更新
        self.update_global_toggle_button()

    # ----------------------------------------
    # 1行ぶんの親階層を一括トグル
    # ----------------------------------------
    def toggle_row_all(self, toggles, btn_obj):
        """
        1行ぶんの親チェーンを一括開閉する。
        """
        all_open = all(self.is_node_open(nid) for nid, _ in toggles)
        new_state = not all_open

        for nid, child_btn in toggles:
            self.tree.item(nid, open=new_state)
            if new_state:
                self.open_parents(nid)
            self.style_toggle_button(child_btn, new_state)

        self.tree.see(toggles[0][0])
        self.style_toggle_button(btn_obj, new_state)

        # 全体トグルボタンの見た目も更新
        self.update_global_toggle_button()

    # ----------------------------------------
    # 検索結果全体を一括展開／一括折りたたみ
    # ----------------------------------------
    def toggle_all_results(self):
        """
        検索結果に含まれるすべての親ノードを一括で開閉する。
        """
        if not self.row_toggle_groups:
            return

        all_nodes = [nid for group in self.row_toggle_groups for (nid, _) in group]
        all_open = all(self.is_node_open(nid) for nid in all_nodes)
        new_state = not all_open

        for row_toggles in self.row_toggle_groups:
            for nid, btn in row_toggles:
                self.tree.item(nid, open=new_state)
                if new_state:
                    self.open_parents(nid)
                self.style_toggle_button(btn, new_state)

        for row_all_btn in self.row_all_buttons:
            self.style_toggle_button(row_all_btn, new_state)

        self.style_toggle_button(self.global_toggle_btn, new_state)

        self.tree.see(all_nodes[0])

    def update_global_toggle_button(self):
        """
        現在の開閉状態に基づいて、全体トグルボタンの見た目を更新する。
        """
        if not self.row_toggle_groups:
            self.global_toggle_btn.config(state="disabled")
            self.style_toggle_button(self.global_toggle_btn, is_open=False)
            return

        self.global_toggle_btn.config(state="normal")
        all_nodes = [nid for group in self.row_toggle_groups for (nid, _) in group]
        all_open = all(self.is_node_open(nid) for nid in all_nodes)
        self.style_toggle_button(self.global_toggle_btn, is_open=all_open)

    # ----------------------------------------
    # メインツリーの該当ノードへジャンプ
    # ----------------------------------------
    def focus_on_tree_item(self, node_id):
        """
        指定ノードにフォーカスして、親をすべて open し、見える位置までスクロール。
        """
        self.open_parents(node_id)
        self.tree.selection_set(node_id)
        self.tree.focus(node_id)
        self.tree.see(node_id)


def main():
    app = ASTViewer()
    app.mainloop()


if __name__ == "__main__":
    main()
