import subprocess
from pathlib import Path

class WingetApplicationListGenerator:
    """
    インストールされたアプリケーションのリストをwingetを利用して生成するユーティリティクラス。
    """

    @staticmethod
    def get_installed_apps():
        """
        wingetコマンドを利用してインストールされたアプリケーションのリストを取得する。

        戻り値:
            List[Dict]: アプリケーション名とバージョンの辞書リスト。
        """
        installed_apps = []
        command = ["winget", "list"]
        try:
            output = subprocess.check_output(command, encoding="utf-8", errors="replace")
            for line in output.strip().split("\n")[2:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        name = " ".join(parts[:-3])
                        version = parts[-3]
                        installed_apps.append({"Name": name, "Version": version})
                    else:
                        print(f"Skipping invalid line: {line}")
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving installed applications: {e}")

        print(f"Retrieved {len(installed_apps)} applications using winget.")
        return installed_apps

    @staticmethod
    def save_installed_apps_to_file(filename):
        """
        インストールされたアプリケーションのリストをファイルに保存する。

        引数:
            filename (str): アプリケーションリストを保存するファイルパス。
        """
        apps = WingetApplicationListGenerator.get_installed_apps()
        if not apps:
            print("No installed applications found.")
        else:
            with open(filename, "w", encoding="utf-8") as file:
                for app in sorted(apps, key=lambda x: x['Name']):
                    file.write(f"{app['Name']} (Version: {app['Version']})\n")
            print(f"Application list saved to {filename}.")

# 使用例:
if __name__ == "__main__":
    # ユーザーのドキュメントフォルダ内にファイルを保存
    documents_path = Path.home() / "Documents/installed_apps_list_winget.txt"
    WingetApplicationListGenerator.save_installed_apps_to_file(str(documents_path))
