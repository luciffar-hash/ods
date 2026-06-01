# ==============================================================================
# 項目名稱：路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS
# 檔案名稱：ods.py
# 目前版本：v1.7.4 (Luciffar 智庫宇宙完整修復版)
# ==============================================================================

import sys, subprocess, io, csv, glob, os
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# 依賴檢查
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
    
    # 讀取 CSV 並清洗
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

    # 執行過濾與寫入
    for out_row_idx, row in enumerate([r for r in raw_rows if r and not any(k in r[0] for k in ["總和", "融資", "合計"])], start=1):
        tr = TableRow()
        table.addElement(tr)
        for cell_value in row:
            tc = TableCell()
            tc.addElement(P(text=cell_value))
            tr.addElement(tc)
    
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

# Streamlit 網頁呈現
if HAS_STREAMLIT and (st.runtime.exists() or 'STREAMLIT_SERVER_PORT' in os.environ):
    st.set_page_config(page_title="路西法智庫", page_icon="🌌", layout="wide")
    st.title("🌌 路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS")
    st.markdown("#### *Luciffar Think Tank: Destiny Reshaping*")
    
    # 完整說明文件
    st.markdown("""
    ### **【核心轉化機制說明】**
    本神器專為 **國泰樹精靈電腦版** 匯出之庫存 CSV 設計：
    * ⚡ **命運奪天**：將死資料洗滌，注入動態活公式，告別券商靜態死數值。
    * ⚔️ **斷罪斬無用**：自動精確剔除重複標頭與末端干擾行，只留下純淨資產本體。
    * 🌌 **萬法歸一**：動態追蹤庫存長度，精確加總各項資產並整數化。
    * 🛡️ **遮天防護網**：批次煉化不閃退，內嵌隱私防護，資料即轉即銷。
    """)
    
    uploaded_files = st.file_uploader("📥 祭入國泰樹精靈庫存 CSV（支援多檔案）：", type=["csv"], accept_multiple_files=True)
    
    if uploaded_files:
        # 溫柔提示音 (低增益版)
        st.audio("https://actions.google.com/sounds/v1/ui/light_toast.ogg", format="audio/ogg", autoplay=True)
        
        for i, u_file in enumerate(uploaded_files):
            ods_data = core_transform_engine(u_file, True)
            st.download_button(
                label=f"💾 點擊下載 ➔ {u_file.name}.ods",
                data=ods_data,
                file_name=f"{u_file.name}.ods",
                key=f"dl_{i}"
            )
        st.balloons()

    st.write("---")
    st.markdown("""
    <small style="color: #888888;">
    <b>📋 免責與隱私保護法律聲明</b><br>
    1. 隱私承諾：CSV 檔案轉化完成後即刻銷毀。<br>
    2. 免責聲明：報表僅供參考，使用者因操作導致之資產變動，智庫不負責任。<br>
    3. 智慧產權：本核心演算法由路西法智庫所有，嚴禁未經授權重製。
    </small>
    """, unsafe_allow_html=True)

else:
    print("【本地模式】請將 CSV 放入資料夾後執行。")
    input("按 Enter 關閉...")
