from cefpython3 import cefpython as cef

# CEFを初期化する
cef.Initialize()

# CEFのバージョン情報を取得する
version_info = cef.GetVersion()

# バージョン情報を表示する
print("CEF Version:", version_info.get("cef_version", "Not available"))
print("Chromium Version:", version_info.get("chrome_version", "Not available"))

# CEFを終了する
cef.Shutdown()
print("CEF Python version:", cef.GetVersion())