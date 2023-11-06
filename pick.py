import streamlit as st
import pandas as pd
import os
from werkzeug.utils import secure_filename
# StringIOは使わないので削除し、BytesIOのみをインポート
from io import BytesIO
import math

UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def picking_page():
    st.title('ファイルアップロード')

    uploaded_file = st.file_uploader("ファイルを選択してください", type=['csv'])

    if uploaded_file is not None:
        if allowed_file(uploaded_file.name):
            filename = secure_filename(uploaded_file.name)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            df = pd.read_csv(filepath, encoding='cp932')

            item_code_name = {}
            item_code_num = {}
            item_type_num = {}
            for i in range(len(df)):
                customer = df.iloc[i]
                for x in range(29):
                    item_code = customer.get(f"商品コード{x+1}")
                    item_name = customer.get(f"商品名{x+1}")
                    item_num = customer.get(f"商品数量{x+1}")
                    item_type = customer.get(f"商品タイプ{x+1}")

                    if pd.notna(item_code) and pd.notna(item_name) and pd.notna(item_num) and pd.notna(item_type):
                        if item_code not in item_code_name:
                            item_code_name[item_code] = item_name
                            item_code_num[item_code] = int(item_num)
                            item_type_num[item_code] = item_type
                        else:
                            item_code_num[item_code] += int(item_num)

            picking_datas = [["商品タイプ", "商品コード", "商品名", "合計数量"]]
            for k, v in item_code_name.items():
                data = [item_type_num[k], k, v, item_code_num[k]]
                picking_datas.append(data)

            picking_datas_df = pd.DataFrame(picking_datas[1:], columns=picking_datas[0])
            picking_datas_df = picking_datas_df.sort_values(by=["商品タイプ", "合計数量"], ascending=[False, False])

            # Excelファイルとしてストリームに書き込む
            excel_stream = BytesIO()
            picking_datas_df.to_excel(excel_stream, index=False)  # Excelファイルとしてデータフレームを書き出し
            excel_stream.seek(0)  # ストリームの位置を先頭に戻す

            # ダウンロードボタンを追加するが、今度はExcelファイルとして
            st.download_button(
                label="Excelファイルをダウンロード",
                data=excel_stream,
                file_name='picking_list.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.error('許可されていないファイル形式です。CSVファイルをアップロードしてください。')
    else:
        st.info('ファイルをアップロードしてください。')
