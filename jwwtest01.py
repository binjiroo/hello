import win32ui
import win32con
from PIL import Image, ImageWin
import win32print

def print_image(image_path):
    print("print_image関数が呼び出されました")

def print_image(image_path):
    # 画像ファイルのパス（拡張子も含める）
    image_path = r"C:\Users\kokada\OneDrive\画像\133683152286093333.jpg"
    
    # 使用するプリンタ名（印刷ダイアログに表示される名前と同一）
    printer_name = "FUJI XEROX DocuCentre-VI C2264"
    
    # 画像読み込み（RGBモードに変換）
    img = Image.open(image_path).convert("RGB")
    img_width, img_height = img.size

    # プリンタDCの作成
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    
    # マッピングモードを設定（描画座標の調整に必要）
    hDC.SetMapMode(win32con.MM_ANISOTROPIC)
    
    # プリンタの描画可能領域の取得
    printable_area = (hDC.GetDeviceCaps(win32con.HORZRES), hDC.GetDeviceCaps(win32con.VERTRES))
    
    # 画像のスケーリング（プリンタ上に収まるように）
    scale = min(printable_area[0] / img_width, printable_area[1] / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    
    # 論理座標とデバイス座標の対応付け（ウィンドウとビューポートの設定）
    hDC.SetWindowExt((img_width, img_height))
    hDC.SetViewportExt((new_width, new_height))
    
    # 印刷ジョブの開始
    print("プリンタDC作成完了")
    hDC.StartDoc("Kivy印刷ジョブ")
    print("印刷ジョブ開始")
    hDC.StartPage()
    print("ページ開始")
    
    # 矩形を描画してテストする
    hDC.Rectangle((100, 100, 400, 400))
    
    # ページとジョブの終了
    print("画像描画完了")
    hDC.EndPage()
    print("ページ終了")
    hDC.EndDoc()
    print("印刷ジョブ終了")
    hDC.DeleteDC()

# ローカルプリンタ一覧を取得する
printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
for printer in printers:
    print(printer[2])

# Kivyアプリ内のボタンイベントなどからこの関数を呼び出してください
if __name__ == '__main__':
    # Kivyアプリとは別にprint_imageを呼び出すテスト
    print_image(r"C:\Users\kokada\OneDrive\画像\133683152286093333.jpg")

