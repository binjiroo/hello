import tkinter as tk
import json
from tkinter import simpledialog, filedialog, ttk, messagebox
import sympy as sp  # SymPyをインポート
from sympy.parsing.latex import parse_latex

class TextEditorApp:
    def __init__(self, root):
        self.root = root
        self.documents = {}
        self.current_title = None
        self.current_page_index = -1

        # GUIの初期設定
        self.setup_gui()

        # 右クリックメニューの設定
        self.setup_context_menus()

    def setup_gui(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(side=tk.TOP, fill=tk.X)

        self.title_font_size_var = tk.StringVar(value="24")
        self.text_font_size_var = tk.StringVar(value="12")
        self.title_font_size_var.trace('w', self.update_font_sizes)
        self.text_font_size_var.trace('w', self.update_font_sizes)

        ttk.Combobox(self.menu_frame, textvariable=self.title_font_size_var, values=["24", "32", "36"], width=5).pack(side=tk.LEFT)
        ttk.Combobox(self.menu_frame, textvariable=self.text_font_size_var, values=[str(x) for x in range(12, 25, 2)], width=5).pack(side=tk.LEFT)

        self.text_area = tk.Text(self.root)
        self.text_area.pack(expand=True, fill=tk.BOTH)

        tk.Button(self.menu_frame, text="新規タイトル", command=self.new_title).pack(side=tk.LEFT)
        tk.Button(self.menu_frame, text="ページを追加", command=self.add_page).pack(side=tk.LEFT)
        tk.Button(self.menu_frame, text="開く", command=self.open_file).pack(side=tk.LEFT)
        tk.Button(self.menu_frame, text="保存", command=self.save_file).pack(side=tk.LEFT)
        tk.Button(self.menu_frame, text="名前を付けて保存", command=self.save_file_as).pack(side=tk.LEFT)
        # LaTeX変換ボタンを追加
        tk.Button(self.menu_frame, text="LaTeX変換", command=self.convert_to_latex).pack(side=tk.LEFT)

        self.titles_listbox = tk.Listbox(self.root, width=20)
        self.titles_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.titles_listbox.bind('<<ListboxSelect>>', self.change_title)

        self.pages_listbox = tk.Listbox(self.root, width=20)
        self.pages_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.pages_listbox.bind('<<ListboxSelect>>', self.change_page)

    def setup_context_menus(self):
        self.title_list_menu = tk.Menu(self.root, tearoff=0)
        self.title_list_menu.add_command(label="名前を変更", command=self.rename_title)

        self.page_list_menu = tk.Menu(self.root, tearoff=0)
        self.page_list_menu.add_command(label="名前を変更", command=self.rename_page)

        self.titles_listbox.bind("<Button-3>", self.show_title_list_menu)
        self.pages_listbox.bind("<Button-3>", self.show_page_list_menu)

    def show_title_list_menu(self, event):
        try:
            self.titles_listbox.selection_clear(0, tk.END)
            self.titles_listbox.selection_set(self.titles_listbox.nearest(event.y))
            self.titles_listbox.activate(self.titles_listbox.nearest(event.y))
            self.title_list_menu.post(event.x_root, event.y_root)
        except tk.TclError:
            pass

    def show_page_list_menu(self, event):
        try:
            self.pages_listbox.selection_clear(0, tk.END)
            self.pages_listbox.selection_set(self.pages_listbox.nearest(event.y))
            self.pages_listbox.activate(self.pages_listbox.nearest(event.y))
            self.page_list_menu.post(event.x_root, event.y_root)
        except tk.TclError:
            pass

    def rename_title(self):
        index = self.titles_listbox.curselection()
        if not index:
            return  # 選択されていない場合は何もしない
        old_name = self.titles_listbox.get(index)
        new_name = simpledialog.askstring("名前を変更", "新しいタイトル名:", initialvalue=old_name)
        if new_name and new_name != old_name:
            if new_name in self.documents:
                messagebox.showerror("エラー", "このタイトル名は既に存在します。")
                return
            # 文書データ構造内でタイトル名を更新
            self.documents[new_name] = self.documents.pop(old_name)  # ここでキーを更新
            self.titles_listbox.delete(index)
            self.titles_listbox.insert(index, new_name)
            self.titles_listbox.select_set(index)  # 更新した項目を選択状態にする
            self.current_title = new_name  # 現在のタイトルも更新

    def rename_page(self):
        page_index = self.pages_listbox.curselection()
        if not page_index:
            return  # タイトルまたはページが選択されていない場合は何もしない
        old_name = self.pages_listbox.get(page_index)
        new_name = simpledialog.askstring("名前を変更", "新しいページ名:", initialvalue=old_name)
        if new_name and new_name != old_name:
            # ページ名の重複チェック
            if any(page['name'] == new_name for page in self.documents[self.current_title]):
                messagebox.showerror("エラー", "このページ名は既に存在します。")
                return
            # ページ名を更新
            self.documents[self.current_title][page_index[0]]['name'] = new_name
            self.pages_listbox.delete(page_index[0])  # ここを修正
            self.pages_listbox.insert(page_index[0], new_name)  # ここを修正
            self.pages_listbox.select_set(page_index[0])  # 更新した項目を選択状態にする

    def new_title(self):
        title = simpledialog.askstring("タイトル入力", "新しいタイトル:")
        if title and title not in self.documents:
            self.documents[title] = []
            self.titles_listbox.insert(tk.END, title)
            self.pages_listbox.delete(0, tk.END)

    def add_page(self):
        if self.current_title:
            page_name = simpledialog.askstring("ページ名入力", "新しいページの名前:")
            if page_name:
                # 名前の重複をチェック
                if any(page_name == page['name'] for page in self.documents[self.current_title]):
                    tk.messagebox.showerror("エラー", "このページ名は既に存在します。別の名前を選んでください。")
                    return
                new_page = {"name": page_name, "content": ""}
                self.documents[self.current_title].append(new_page)
                self.pages_listbox.insert(tk.END, page_name)
                self.pages_listbox.select_set(tk.END)
                self.change_page()

    def change_title(self, event=None):
        index = self.titles_listbox.curselection()
        if index:
            # 現在のページ内容を保存する前に、ページが存在するか確認
            if self.current_page_index >= 0 and self.current_title in self.documents and len(self.documents[self.current_title]) > self.current_page_index:
                self.save_current_page_content()
            title = self.titles_listbox.get(index)
            self.current_title = title
            self.current_page_index = -1  # ページインデックスをリセット
            self.pages_listbox.delete(0, tk.END)
            for page in self.documents[title]:
                self.pages_listbox.insert(tk.END, page['name'])
            if self.documents[title]:
                self.pages_listbox.select_set(0)
                self.change_page()

    def change_page(self, event=None):
        index = self.pages_listbox.curselection()
        if index:
            self.save_current_page_content()
            self.current_page_index = index[0]
            page_content = self.documents[self.current_title][self.current_page_index]["content"]
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, page_content)

    # convert_to_latexメソッド内でのカスタムダイアログの使用
    def convert_to_latex(self):
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            print(f"変換前のテキスト: {selected_text}")
            sympy_expr = parse_latex(selected_text)
            latex_str = sp.latex(sympy_expr)
            CustomDialog(self.root, "LaTeX変換結果", latex_str)
        except tk.TclError:
            messagebox.showerror("エラー", "テキストが選択されていません。", parent=self.root)
        except Exception as e:
            messagebox.showerror("エラー", f"変換に失敗しました。エラー: {e}", parent=self.root)

    def save_current_page_content(self):
        if self.current_title is not None and self.current_page_index >= 0:
            self.documents[self.current_title][self.current_page_index]["content"] = self.text_area.get(1.0, tk.END)

    def update_font_sizes(self, *args):
        title_font_size = int(self.title_font_size_var.get())
        text_font_size = int(self.text_font_size_var.get())
        self.titles_listbox.config(font=("Arial", title_font_size))
        self.pages_listbox.config(font=("Arial", title_font_size))
        self.text_area.config(font=("Arial", text_font_size))

    def open_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, 'r') as file:
                self.documents = json.load(file)
            self.refresh_ui()
            self.current_file_path = filepath  # 現在開いているファイルのパスを保存

    def save_file(self):
        if hasattr(self, 'current_file_path') and self.current_file_path:
            with open(self.current_file_path, 'w') as file:
                json.dump(self.documents, file)
        else:
            self.save_file_as()

    def save_file_as(self):
        filepath = filedialog.asksaveasfilename(defaultextension="json")
        if filepath:
            with open(filepath, 'w') as file:
                json.dump(self.documents, file)
            self.current_file_path = filepath

    def refresh_ui(self):
        # UIをリフレッシュするためのメソッド
        # タイトルリストとページリストをクリアして、新しく読み込んだデータで更新します。
        self.titles_listbox.delete(0, tk.END)
        self.pages_listbox.delete(0, tk.END)
        for title in self.documents.keys():
            self.titles_listbox.insert(tk.END, title)
        self.current_title = None
        self.current_page_index = -1
        self.text_area.delete(1.0, tk.END)

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")  # ウィンドウサイズの設定

        # メッセージを表示するテキストウィジェットの設定
        self.text_widget = tk.Text(self, height=10, width=50)
        self.text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_widget.insert(tk.END, message)
        self.text_widget.config(state=tk.DISABLED)  # 編集不可に設定

        # 閉じるボタンの設定
        self.button_close = tk.Button(self, text="閉じる", command=self.destroy)
        self.button_close.pack(pady=5)

root = tk.Tk()
app = TextEditorApp(root)
root.mainloop()
