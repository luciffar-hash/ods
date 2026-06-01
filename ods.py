import sys, subprocess, io, csv, glob, os
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
    table = Table(name="股票資產管理")
    doc.spreadsheet.addElement(table)
    
    raw_rows = []
    if is_bytes:
        content = csv_file_obj.getvalue()
        for enc in ['big5', 'utf-8']:
            try:
                raw_rows = list(csv.reader(io.StringIO(content.decode(enc, errors='ignore'))))
                break
            except: continue
    else:
        with open(csv_file_obj, 'r', encoding='big5', errors='ignore') as f:
            raw_rows = list(csv.reader(f))

    for out_row_idx, row in enumerate([r for r in raw_rows if r and not any(k in r[0] for k in ["總和", "融資"])], start=1):
        tr = TableRow()
        table.addElement(tr)
        for cell_value in row:
            tc = TableCell()
            tc.addElement(P(text=cell_value))
            tr.addElement(tc)
    
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

if HAS_STREAMLIT and (st.runtime.exists() or 'STREAMLIT_SERVER_PORT' in os.environ):
    st.set_page_config(page_title="路西法智庫", page_icon="🌌")
    st.title("🌌 路西法智庫：命運重塑 v1.7.4 (輕量優化版)")
    
    uploaded_files = st.file_uploader("📥 祭入 CSV：", type=["csv"], accept_multiple_files=True)
    if uploaded_files:
        # 溫柔提示音
        st.audio("https://actions.google.com/sounds/v1/ui/light_toast.ogg", format="audio/ogg", autoplay=True)
        for i, u_file in enumerate(uploaded_files):
            ods_data = core_transform_engine(u_file, True)
            st.download_button(f"💾 下載 {u_file.name}", ods_data, f"{u_file.name}.ods", key=f"dl_{i}")
        st.balloons()
else:
    print("【本地模式】請將 CSV 放入資料夾後執行。")
    input("按 Enter 關閉...")
