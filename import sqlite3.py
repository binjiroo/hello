import sqlite3
import bcrypt

class UserManager:

    def __init__(self, db_name='users.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.setup()

    def setup(self):
        # テーブルが存在しない場合に、テーブルを作成
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL,
            user_id TEXT PRIMARY KEY,
            password BLOB NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        ''')
        self.connection.commit()

    def register_user(self, username, user_id, password, email):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            self.cursor.execute('''
            INSERT INTO users (username, user_id, password, email) 
            VALUES (?, ?, ?, ?)
            ''', (username, user_id, hashed, email))
            self.connection.commit()
        except sqlite3.IntegrityError:
            print("そのユーザーIDやメールアドレスはすでに存在しています。")

    def authenticate(self, user_id, password):
        self.cursor.execute('SELECT password FROM users WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()
        if result:
            hashed = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), hashed):
                return True
        return False

    def get_user_info(self, user_id):
        self.cursor.execute('SELECT username, email FROM users WHERE user_id=?', (user_id,))
        return self.cursor.fetchone()

    def close(self):
        self.connection.close()


# 使用例
if __name__ == '__main__':
    manager = UserManager()

    manager.register_user("Taro", "taro123", "securepassword", "taro@example.com")

    if manager.authenticate("taro123", "securepassword"):
        print("Authentication successful!")
        print(manager.get_user_info("taro123"))
    else:
        print("Authentication failed!")

    manager.close()
