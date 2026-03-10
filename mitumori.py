import pandas as pd

# 元のファイルのデータを読み込む
file_path = '/mnt/data/松井邸カーポート見積り明細書.xlsx'
df = pd.read_excel(file_path)

# 新しいExcelファイルの作成
with pd.ExcelWriter('new_file.xlsx', engine='xlsxwriter') as writer:
    # データを新しいファイルに書き込む
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    
    # ワークブックとワークシートの取得
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']

    # ここでフォーマットを設定
    # 例: ヘッダーのフォーマットを設定
    header_format = workbook.add_format({'bold': True, 'text_wrap': True})
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # 他のフォーマット設定もここに追加

# ファイルの保存
writer.save()