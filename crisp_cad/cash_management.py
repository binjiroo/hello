from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.core.clipboard import Clipboard
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton, ActionGroup
from kivy.clock import Clock  # Clockをインポート
import json
import os

class TransactionApp(App):
    def build(self):
        self.current_transaction = {}
        self.transactions = []

        root_layout = BoxLayout(orientation='vertical')

        # ActionBar at the top
        self.actionbar = ActionBar(pos_hint={'top': 1}, size_hint_y=None, height=56)
        self.action_view = ActionView()
        self.actionbar.add_widget(self.action_view)
        self.action_previous = ActionPrevious(title='取引管理', with_previous=False)
        self.action_view.add_widget(self.action_previous)

        # Adjust size_hint_x for proper layout
        self.action_previous.size_hint_x = None
        self.action_previous.width = 200  # Adjust as needed

        # File menu using ActionGroup
        self.file_menu = self.create_file_menu()
        self.action_view.add_widget(self.file_menu)

        root_layout.add_widget(self.actionbar)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=2)

        # ScrollView to hold the grid
        self.grid = GridLayout(cols=7, size_hint_y=None, spacing=2, row_force_default=True, row_default_height=40)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)

        # Input and control area at the bottom
        control_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        self.info_label = Label(text="取引先を入力してエンターを押してください", size_hint_y=None, height=40, font_size=18)
        self.input = TextInput(size_hint_y=None, height=40, multiline=False, font_size=18)
        self.input.bind(on_text_validate=self.on_enter)
        control_layout.add_widget(self.info_label)
        control_layout.add_widget(self.input)

        button_layout = BoxLayout(size_hint_y=None, height=60)
        income_button = Button(text="収入", on_press=lambda instance: self.set_transaction_type('収入'))
        payment_button = Button(text="支払", on_press=lambda instance: self.set_transaction_type('支払'))
        copy_button = Button(text="コピー", on_press=self.copy_data)
        clear_button = Button(text="クリア", on_press=self.clear_data)
        button_layout.add_widget(income_button)
        button_layout.add_widget(payment_button)
        button_layout.add_widget(copy_button)
        button_layout.add_widget(clear_button)
        control_layout.add_widget(button_layout)

        main_layout.add_widget(control_layout)

        self.update_grid()

        root_layout.add_widget(main_layout)
        return root_layout

    def create_file_menu(self):
        file_group = ActionGroup(text='ファイル', mode='spinner')

        save_btn = ActionButton(text='保存')
        save_btn.bind(on_release=lambda x: self.show_save_dialog())
        file_group.add_widget(save_btn)

        load_btn = ActionButton(text='開く')
        load_btn.bind(on_release=lambda x: self.show_load_dialog())
        file_group.add_widget(load_btn)

        return file_group

    def on_enter(self, instance):
        text = self.input.text.strip()
        self.input.text = ""
        Clock.schedule_once(lambda dt: setattr(self.input, 'focus', True), 0)  # フォーカスを再設定

        if 'transaction_type' not in self.current_transaction:
            self.info_label.text = "エラー: 先に収入か支払を選択してください"
        elif 'partner' not in self.current_transaction:
            self.current_transaction['partner'] = text
            self.info_label.text = "金額を入力してエンターを押してください"
        elif 'amount' not in self.current_transaction:
            self.current_transaction['amount'] = self.format_currency(text)
            self.info_label.text = "日付を入力してエンターを押してください"
        elif 'date' not in self.current_transaction:
            self.current_transaction['date'] = text
            self.complete_transaction()
            self.reset_input()

    def complete_transaction(self):
        self.transactions.append(self.current_transaction.copy())
        self.current_transaction = {}
        self.update_grid()

    def reset_input(self):
        self.info_label.text = "取引先を入力してエンターを押してください"
        Clock.schedule_once(lambda dt: setattr(self.input, 'focus', True), 0)  # フォーカスを再設定

    def set_transaction_type(self, transaction_type):
        self.current_transaction['transaction_type'] = transaction_type
        self.reset_input()

    def format_currency(self, amount):
        amount_int = int(amount)
        return f"¥{amount_int:,}"

    def parse_currency(self, amount_str):
        return int(amount_str.replace('¥', '').replace(',', ''))

    def update_grid(self):
        self.grid.clear_widgets()
        headers = ["タイプ", "取引先", "金額", "日付", "削除", "表示", "加算"]
        for header in headers:
            self.grid.add_widget(Label(text=header, font_size=18))

        total_income = 0
        total_payment = 0

        for transaction in self.transactions:
            # Check visibility
            if transaction.get('visible', True):
                amount = self.parse_currency(transaction.get('amount', '0'))
                if transaction['transaction_type'] == '収入':
                    if transaction.get('included', True):
                        total_income += amount
                elif transaction['transaction_type'] == '支払':
                    if transaction.get('included', True):
                        total_payment += amount

            for key in ['transaction_type', 'partner', 'amount', 'date']:
                self.grid.add_widget(Label(text=str(transaction.get(key, '')), font_size=18))

            delete_button = Button(text="削除", size_hint_y=None, height=40)
            delete_button.bind(on_press=lambda instance, t=transaction: self.delete_transaction(t))
            self.grid.add_widget(delete_button)

            visible_toggle = ToggleButton(text='表示', size_hint_y=None, height=40,
                                          state='down' if transaction.get('visible', True) else 'normal')
            visible_toggle.bind(on_press=lambda instance, t=transaction: self.toggle_visible(t))
            self.grid.add_widget(visible_toggle)

            include_toggle = ToggleButton(text='加算', size_hint_y=None, height=40,
                                          state='down' if transaction.get('included', True) else 'normal')
            include_toggle.bind(on_press=lambda instance, t=transaction: self.toggle_included(t))
            self.grid.add_widget(include_toggle)

        # Add total rows
        if total_income > 0 or total_payment > 0:
            # Add empty row as a separator
            for _ in range(7):
                self.grid.add_widget(Label(text=""))

            # Add total income row
            if total_income > 0:
                self.grid.add_widget(Label(text="収入", font_size=18))
                self.grid.add_widget(Label(text="合計収入", font_size=18))
                self.grid.add_widget(Label(text=self.format_currency(str(total_income)), font_size=18))
                self.grid.add_widget(Label(text="", font_size=18))  # Empty date
                # Empty cells for buttons
                for _ in range(3):
                    self.grid.add_widget(Label(text=""))

            # Add total payment row
            if total_payment > 0:
                self.grid.add_widget(Label(text="支払", font_size=18))
                self.grid.add_widget(Label(text="合計支払", font_size=18))
                self.grid.add_widget(Label(text=self.format_currency(str(total_payment)), font_size=18))
                self.grid.add_widget(Label(text="", font_size=18))  # Empty date
                # Empty cells for buttons
                for _ in range(3):
                    self.grid.add_widget(Label(text=""))

    def delete_transaction(self, transaction, *args):
        if transaction in self.transactions:
            self.transactions.remove(transaction)
            self.update_grid()

    def toggle_visible(self, transaction, *args):
        transaction['visible'] = not transaction.get('visible', True)
        self.update_grid()

    def toggle_included(self, transaction, *args):
        transaction['included'] = not transaction.get('included', True)
        self.update_grid()

    def copy_data(self, instance):
        transactions_to_copy = [
            t for t in self.transactions
            if t.get('visible', True)
        ]

        data_lines = [
            f"{t['transaction_type']}, {t['partner']}, {t['amount']}, {t['date']}"
            for t in transactions_to_copy
        ]

        total_income = sum(
            self.parse_currency(t['amount'])
            for t in transactions_to_copy
            if t.get('included', True) and t['transaction_type'] == '収入'
        )
        total_payment = sum(
            self.parse_currency(t['amount'])
            for t in transactions_to_copy
            if t.get('included', True) and t['transaction_type'] == '支払'
        )

        if total_income > 0:
            data_lines.append(f"収入, 合計収入, {self.format_currency(str(total_income))},")
        if total_payment > 0:
            data_lines.append(f"支払, 合計支払, {self.format_currency(str(total_payment))},")

        data = '\n'.join(data_lines)
        Clipboard.copy(data)

    def clear_data(self, instance):
        self.transactions.clear()
        self.update_grid()

    # File management methods
    def show_save_dialog(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        self.filechooser = FileChooserListView(filters=['*.json'], path=os.getcwd())
        content.add_widget(self.filechooser)
        buttons = BoxLayout(size_hint_y=None, height=40)
        save_btn = Button(text='保存', size_hint_y=None, height=40)
        save_btn.bind(on_release=lambda x: self.do_save(self.filechooser.path, self.filechooser.selection))
        cancel_btn = Button(text='キャンセル', size_hint_y=None, height=40)
        cancel_btn.bind(on_release=lambda x: self.popup.dismiss())
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        self.popup = Popup(title='保存', content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def do_save(self, path, selection):
        if selection:
            file_path = selection[0]
        else:
            file_path = os.path.join(path, 'transactions.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, ensure_ascii=False, indent=4)
        self.popup.dismiss()
        self.info_label.text = f"データを保存しました: {file_path}"

    def show_load_dialog(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        self.filechooser = FileChooserListView(filters=['*.json'], path=os.getcwd())
        content.add_widget(self.filechooser)
        buttons = BoxLayout(size_hint_y=None, height=40)
        load_btn = Button(text='開く', size_hint_y=None, height=40)
        load_btn.bind(on_release=lambda x: self.do_load(self.filechooser.selection))
        cancel_btn = Button(text='キャンセル', size_hint_y=None, height=40)
        cancel_btn.bind(on_release=lambda x: self.popup.dismiss())
        buttons.add_widget(load_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        self.popup = Popup(title='開く', content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def do_load(self, selection):
        if selection:
            file_path = selection[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                self.transactions = json.load(f)
            self.update_grid()
            self.info_label.text = f"データを読み込みました: {file_path}"
        self.popup.dismiss()

if __name__ == "__main__":
    TransactionApp().run()
