import streamlit as st
import pandas as pd
import os
from werkzeug.utils import secure_filename
from io import StringIO
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
            for i in range(len(df)):
                customer = df.iloc[i]
                for x in range(29):
                    item_code = customer.get(f"商品コード{x+1}")
                    item_name = customer.get(f"商品名{x+1}")
                    item_num = customer.get(f"商品数量{x+1}")

                    if pd.notna(item_code) and pd.notna(item_name) and pd.notna(item_num):
                        if item_code not in item_code_name:
                            item_code_name[item_code] = item_name
                            item_code_num[item_code] = int(item_num)
                        else:
                            item_code_num[item_code] += int(item_num)

            picking_datas = [["商品コード", "商品名", "合計数量"]]
            for k, v in item_code_name.items():
                data = [k, v, item_code_num[k]]
                picking_datas.append(data)

            textStream = StringIO()
            picking_datas_df = pd.DataFrame(picking_datas)
            picking_datas_df.to_csv(textStream, header=False, index=False, encoding='utf-8')

            st.download_button(label="CSVファイルをダウンロード", data=textStream.getvalue(), file_name='picking.csv', mime='text/csv')
        else:
            st.error('許可されていないファイル形式です。CSVファイルをアップロードしてください。')
    else:
        st.info('ファイルをアップロードしてください。')
