# sort.py
import streamlit as st
import csv
import pandas as pd
import chardet
from io import StringIO
import base64

def consumer_to_group_label(consumer):
    product_codes = sorted(list(consumer["products"].keys()))
    return ",".join(product_codes)

@st.cache_data
def process_file(uploaded_file):
    result = chardet.detect(uploaded_file.read())
    encoding = result['encoding']
    uploaded_file.seek(0)
    csvfile = StringIO(uploaded_file.getvalue().decode(encoding))
    reader = csv.reader(csvfile)
    header = []
    consumers = []
    for line, row in enumerate(reader):
        if line == 0:
            header = row
            continue
        consumer = {"row": row}
        products = {}
        for i in range(30):
            if len(row) > 52 + 1 * 7 + 1:
                product_code = row[52 + i * 7 + 0]
                if product_code:
                    amount_str = row[52 + i * 7 + 21]
                    if amount_str.isdigit():
                        amount = int(amount_str)
                        products[product_code] = amount + products.get(product_code, 0)
        consumer["products"] = products
        consumers.append(consumer)
    consumer_groups = {}
    for consumer in consumers:
        label = consumer_to_group_label(consumer)
        l = consumer_groups.get(label, [])
        l.append(consumer)
        consumer_groups[label] = l
    sorted_consumer_groups = sorted(consumer_groups.values(), key=lambda x: len(x), reverse=True)
    output = []
    for consumers in sorted_consumer_groups:
        for consumer in consumers:
            output.append(consumer["row"])
    return header, output

def write_to_csv(header, output):
    csv_output = StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(header)
    for row in output:
        writer.writerow(row)
    return csv_output.getvalue()

def main():
    st.title("CSV File Processor")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        header, output = process_file(uploaded_file)
        csv_string = write_to_csv(header, output)
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="output.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)
