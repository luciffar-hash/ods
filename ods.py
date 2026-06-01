# ==============================================================================
# 項目名稱：路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS
# 檔案名稱：ods.py
# 目前版本：v1.6.9 (Luciffar 智庫宇宙溫柔低分貝版)
# ==============================================================================

import sys
import subprocess
import io
import csv
import glob
import os

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
    from odf.style import Style, TextProperties, TableCellProperties, TableColumnProperties
    from odf.table import TableColumn
except ImportError:
    if not HAS_STREAMLIT:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "odfpy"])
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableRow, TableCell
        from odf.text import P
        from odf.style import Style, TextProperties, TableCellProperties, TableColumnProperties
        from odf.table import TableColumn

def core_transform_engine(csv_file_obj, is_bytes=False):
    doc = OpenDocumentSpreadsheet()
    header_style = Style(name="HeaderStyle", family="table-cell")
    header_style.addElement(TextProperties(fontweight="bold", fontsize="10pt"))
    header_style.addElement(TableCellProperties(backgroundcolor="#DCE6F1", border="0.5pt solid #A6B9D1"))
    doc.styles.addElement(header_style)
    
    data_style = Style(name="DataStyle", family="table-cell")
    data_style.addElement(TableCellProperties(border="0.5pt solid #E0E0E0"))
    doc.styles.addElement(data_style)
    
    table = Table(name="股票資產管理")
    table.setAttribute("print", "true")
    doc.spreadsheet.addElement(table)
    
    raw_rows = []
    if is_bytes:
        content = csv_file_obj.getvalue()
        for encoding in ['big5', 'utf-8', 'gbk']:
            try:
                decoded_content = content.decode(encoding, errors='ignore')
                raw_rows = list(csv.reader(io.StringIO(decoded_content)))
                if raw_rows: break
            except Exception: continue
    else:
        with open(csv_file_obj, 'r', encoding='big5', errors='ignore') as f:
            raw_rows = list(csv.reader(f))

    processed_rows = []
    data_row_indices = []
    has_header_written = False
    current_out_idx = 0

    for r in raw_rows:
        if not r or not any(r): continue
        r = [cell.strip() for cell in r]
        if "股票名稱" in r[0]:
            if not has_header_written:
                processed_rows.append(r)
                current_out_idx += 1
                has_header_written = True
            continue
        if len(r) > 8 and "融資" in r[8]: continue
        if any(keyword in r[0] for keyword in ["總和", "加總", "損益", "合計"]): continue
        processed_rows.append(r)
        current_out_idx += 1
        data_row_indices.append(current_out_idx)

    for out_row_idx, row in enumerate(processed_rows, start=1):
        tr = TableRow()
        table.addElement(tr)
        while len(row) < 12: row.append("")
        for col_idx, cell_value in enumerate(row, start=1):
            col_letter = chr(64 + col_idx) if col_idx <= 26 else "A" + chr(64 + col_idx - 26)
            tc = TableCell()
            tc.setAttribute("stylename", header_style if out_row_idx == 1 else data_style)
            if out_row_idx > 1 and out_row_idx in data_row_indices:
                if col_letter in ['G', 'H', 'C', 'D', 'E', 'F', 'J', 'K']:
                    try:
                        clean_num = cell_value.replace(',', '').split('.')[0]
                        if clean_num:
                            tc.setAttribute("value", clean_num)
                            tc.setAttribute("valuetype", "float")
                        else: tc.addElement(P(text=cell_value))
                    except: tc.addElement(P(text=cell_value))
                else: tc.addElement(P(text=cell_value))
            else: tc.addElement(P(text=cell_value))
            tr.addElement(tc)

    output_stream = io.BytesIO()
    doc.save(output_stream)
    return output_stream.getvalue()

if HAS_STREAMLIT and (st.runtime.exists() or 'STREAMLIT_SERVER_PORT' in os.environ):
    st.set_page_config(page_title="路西法智庫", page_icon="🌌", layout="wide")
    st.title("🌌 路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS")
    
    uploaded_files = st.file_uploader("📥 祭入 CSV（支援多檔批次）：", type=["csv"], accept_multiple_files=True)
    
    if uploaded_files:
        # 💥 這裡就是音效區塊，已經替換為原始增益極低的輕柔音效
        st.components.v1.html(
            '<audio autoplay><source src="https://actions.google.com/sounds/v1/ui/light_toast.ogg" type="audio/ogg"></audio>',
            height=0
        )
        
        for u_file in uploaded_files:
            try:
                ods_bytes = core_transform_engine(u_file, is_bytes=True)
                st.download_button(
                    label=f"💾 點擊下載 ➔ {u_file.name}_自動化.ods",
                    data=ods_bytes,
                    file_name=f"{u_file.name}_自動化.ods",
                    mime="application/vnd.oasis.opendocument.spreadsheet"
                )
            except Exception as e: st.error(f"錯誤: {e}")
        st.balloons()

    st.write("---")
    st.markdown('<small style="color: #888888;">免責聲明：資料僅供參考，風險自負。</small>', unsafe_allow_html=True)
else:
    print("【本地模式】請將 CSV 放入資料夾後執行。")
    input("按 Enter 關閉...")
