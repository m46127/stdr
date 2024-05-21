import streamlit as st
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfgen import canvas
import pandas as pd
import os
import shutil
from PyPDF2 import PdfMerger, PdfReader
import glob
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import chardet 

w, h = portrait(A4)

def create_pdf_files(uploaded_file):
    pdfmetrics.registerFont(TTFont('mmt', './fonts/GenShinGothic-Monospace-Medium.ttf'))
    output_files = []
    # output フォルダをクリーンアップ
    if os.path.exists('output'):
        shutil.rmtree('output')
    os.makedirs('output', exist_ok=True)
    
    # ファイルが空でないか確認
    uploaded_file.seek(0)
    if len(uploaded_file.read()) == 0:
        print("エラー: アップロードされたファイルが空です")
        return
    
    # ファイルをデータフレームに変換
    uploaded_file.seek(0)
    rawdata = uploaded_file.read()
    result = chardet.detect(rawdata)
    enc = result['encoding']
    uploaded_file.seek(0)
    try:
        df = pd.read_csv(uploaded_file, encoding=enc)
    except pd.errors.EmptyDataError:
        print("エラー: CSV ファイルが空です")
        return
    
    for index, record in df.iterrows():
        # ファイルの指定
        output_file = f'./output/output_{index+1}.pdf'  # 完成したPDFの保存先
        output_files.append(output_file)
        # キャンバスの設定
        cv = canvas.Canvas(output_file, pagesize=(w, h))
        cv.setFillColorRGB(0, 0, 0)
        # 以下、PDF生成の処理...

        # フォントの設定
        cv.setFont('mmt', 12)

        # データの描画
        customer_id = record['顧客ID']
        if pd.isna(customer_id):
            customer_id_str = ''
        else:
            customer_id_str = str(int(customer_id))
        cv.setFont('mmt', 10) 
        cv.drawString(30, h - 120, f"顧客ID:{customer_id_str}")
        cv.drawString(30, h - 60, 'お買い上げ明細書兼領収書')
        cv.setFont('mmt', 12) 
        cv.drawString(30, h - 80, 'この度はお買い上げいただき、ありがとうございます。')
        cv.setFont('mmt', 10)
        cv.drawString(150, h - 120, f"受注ID:{record['注文番号']}")
        cv.drawString(30, h - 140, f"{record['お届け先名称１']} 様")
        cv.drawString(30, h - 155, f"〒{record['お届け先郵便番号']}")
        cv.drawString(30, h - 170, str(record['お届け先住所１']))
        cv.drawString(30, h - 185, str(record['お届け先住所２']))
        cv.setFont('mmt', 8)
        cv.drawString(30, h - 220, f"次回お届け予定日:{record['次回お届け予定日']}")
        cv.drawString(30, h - 235, '【お申込み内容の確認・変更、各種申請ついて】')
        cv.drawString(30, h - 250, ' 次回お届け予定日の10日前までにマイページ')
        cv.setFont('mmt', 10)
        cv.drawString(350, h - 60, str(record['ご依頼主名称１']))
        cv.drawString(350, h - 75, '登録番号:T101001102642')
        cv.drawString(350, h - 90, f"〒{record['ご依頼主郵便番号']}")
        cv.drawString(350, h - 105, str(record['ご依頼主住所１']))
        cv.drawString(350, h - 120, str(record['ご依頼主住所２']))
        cv.drawString(350, h - 135, 'TEL 0120-444-636(平日9:30~17:30)')
        cv.drawString(310, h - 170, 'プレゼント内容')
        cv.rect(305, h - 250, 260, 100)
        cv.drawString(35, h - 690, '【備考】')
        cv.rect(30, h - 800, 500, 140)
        cv.drawString(350, h - 690, '＜同梱物＞')

        # QR1を表示
        image_path = './image/QR1.jpg'  # 画像のパスを指定してください
        x = 210
        y = h - 270
        width = 80
        height = 80
        cv.drawImage(image_path, x, y, width, height)
        #QR2を表示
        image_path = './image/QR2.png'  # 画像のパスを指定してください
        x = 210
        y = h - 370
        width = 60
        height = 60
        cv.drawImage(image_path, x, y, width, height)

        # 商品情報の取得
        items = get_items(record)
        regular_sale = []
        present = []
        flyer = []
        for item in items:
            if item['type'] == '定期販売':
                regular_sale.append(item)
            elif item['type'] == 'プレゼント':
                present.append(item)
            else:
                flyer.append(item)

        # 定期販売商品の描画
        y = h - 400  # Y座標の初期値

        # ヘッダーの描画
        cv.setFont('mmt', 10)
        cv.drawString(60, y, '商品コード - 商品名 (数量, 単価)')

        # ヘッダーに枠を追加
        cv.rect(50, y - 5, 400, 20, fill=False)

        y -= 20  # ヘッダーの下に移動

        # 定期販売商品の枠と背景色の描画
        for idx, item in enumerate(regular_sale):
            background_color = colors.whitesmoke if idx % 2 == 0 else colors.lightgrey
            cv.setFillColor(background_color)
            cv.rect(50, y - 5, 400, 20, fill=True, stroke=False)
            cv.setFillColor(colors.black)
            cv.setFont('mmt', 10)
            cv.drawString(60, y, f"{item['code']} - {item['name']} ({int(item['count'])}個, {int(item['unit_price'])}円)")  # 商品コード、商品名、数量、単価の描画
            cv.rect(50, y - 5, 400, 20, fill=False)  # 枠の描画
            y -= 20  # Y座標を下げて次の行に移動


        # 定期販売商品の枠と背景色の描画
        for idx, item in enumerate(regular_sale):
            background_color = colors.whitesmoke if idx % 2 == 0 else colors.lightgrey
            cv.setFillColor(background_color)
            cv.rect(50, y - 5, 400, 20, fill=True, stroke=False)
            cv.setFillColor(colors.black)
            cv.setFont('mmt', 10)
            cv.drawString(60, y, f"{item['code']} - {item['name']} ({int(item['count'])}個, {int(item['unit_price'])}円)")  # 商品コード、商品名、数量、単価の描画
            cv.rect(50, y - 5, 400, 20, fill=False)  # 枠の描画
            y -= 20  # Y座標を下げて次の行に移動

        # プレゼント商品の描画
        y = h - 180  # Y座標の初期値
        for item in present:
            cv.setFont('mmt', 8)
            cv.drawString(310, y, f"{item['name']} ({int(item['count'])}個)")  # 商品コード、商品名、数量の描画
            y -= 10  # Y座標を下げて次の行に移動

        # 同梱物の描画
        y = h - 700  # Y座標の初期値
        for item in flyer:
            cv.setFont('mmt', 8)
            cv.drawString(350, y, f"{item['code']} - ({int(item['count'])}個)")  # 商品コード、商品名、数量の描画
            y -= 10  # Y座標を下げて次の行に移動

        # PDFの保存
        cv.showPage()
        cv.save()
    return output_files

def get_items(record):
    items_dict = {}
    for i in range(30):
        code = record[f'商品コード{i + 1}']
        name = record[f'商品名{i + 1}']
        count = record[f'商品数量{i + 1}']
        unit_price = record[f'商品単価{i + 1}']
        price = record[f'商品金額{i + 1}']
        type_ = record[f'商品タイプ{i + 1}']
        detail = record[f'商品明細表示{i + 1}']

        if type(code) != float:  # 商品コードが NaN でない場合
            if code not in items_dict:
                item = {
                    'code': code,
                    'name': name,
                    'count': count,
                    'unit_price': unit_price,
                    'price': price,
                    'type': type_,
                    'detail': detail,
                }
                items_dict[code] = item
            else:
                items_dict[code]['count'] += count
                items_dict[code]['price'] += price

    items = list(items_dict.values())
    return items

def merge_pdf_in_dir(dir_path, dst_path):
    l = glob.glob(os.path.join(dir_path, '*.pdf'))
    l.sort()

    merger = PdfMerger()
    for p in l:
        if not PdfReader(p).is_encrypted:
            merger.append(p)

    merger.write(dst_path)
    merger.close()

def main():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        output_files = create_pdf_files(uploaded_file)
        merged_file = './output/merged.pdf'
        merge_pdf_in_dir('output', merged_file)

        with open(merged_file, "rb") as f:
            st.download_button(
                label="Download Merged PDF",
                data=f,
                file_name="merged.pdf",
                mime="application/pdf",
            )

# main関数を実行
if __name__ == "__main__":
    main()
