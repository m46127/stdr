# Inventory.py

import streamlit as st
import pandas as pd
import base64
import io

def get_binary_file_downloader_html(bin_file, file_label='File'):
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">Download {file_label}</a>'
    return href

def main():
    uploaded_file_csv = st.file_uploader("Choose a CSV file", type="csv")
    uploaded_file_excel = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file_csv is not None and uploaded_file_excel is not None:
        # CSVファイルを読み込む
        picking_df = pd.read_csv(uploaded_file_csv)
        
        # '商品コード'と'合計数量'の列が存在するか確認
        if '商品コード' in picking_df.columns and '合計数量' in picking_df.columns:
            # '商品コード'でグループ化して'合計数量'の合計を計算
            picking_df = picking_df.groupby('商品コード')['合計数量'].sum().reset_index()
            picking_df['商品コード'] = picking_df['商品コード'].astype(str).str.strip().str.upper()
        else:
            # '商品コード'または'合計数量'列が存在しない場合の処理
            st.error('CSVファイルに「商品コード」または「合計数量」列が存在しません。')
            return
        
        # 在庫表のExcelファイルを読み込む
        inventory_df = pd.read_excel(uploaded_file_excel, usecols='D')
        inventory_df.columns = ['商品コード']
        inventory_df['商品コード'] = inventory_df['商品コード'].astype(str).str.strip().str.upper()
        
        # 在庫表とピッキングリストをマージ
        merged_df = pd.merge(inventory_df, picking_df, on='商品コード', how='left')
        merged_df['合計数量'].fillna(0, inplace=True)
        
        # ファイルをダウンロードするためのリンクを作成
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            merged_df.to_excel(writer, sheet_name='Sheet1', index=False)
        
        binary_excel = output.getvalue()
        st.markdown(get_binary_file_downloader_html(binary_excel, 'Merged_YourFileNameHere.xlsx'), unsafe_allow_html=True)
