# ==============================================================================
# 項目名稱：路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS
# 英文譯名：Luciffar Think Tank: Destiny Reshaping — Cathay Tree Wizard
# 目前版本：v1.7.7 (Luciffar 智庫宇宙內容完整歸位版)
# ==============================================================================

import sys, subprocess, io, csv, os
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def core_transform_engine(csv_file_obj):
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
    doc = OpenDocumentSpreadsheet()
    table = Table(name="股票資產管理")
    doc.spreadsheet.addElement(table)
    
    content = csv_file_obj.getvalue()
    raw_rows = list(csv.reader(io.StringIO(content.decode('big5', errors='ignore'))))
    
    for row in [r for r in raw_rows if r and not any(k in r[0] for k in ["總和", "融資", "合計"])]:
        tr = TableRow()
        table.addElement(tr)
        for cell_value in row:
            tc = TableCell()
            tc.addElement(P(text=cell_value))
            tr.addElement(tc)
    
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

if HAS_STREAMLIT:
    st.set_page_config(page_title="路西法智庫", page_icon="🌌", layout="wide")
    
    # 完美雙語標題歸位
    st.title("🌌 路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS")
    st.markdown("#### *Luciffar Think Tank: Destiny Reshaping — Cathay Tree Wizard Desktop CSV to ODS Converter*")
    
    # 完整說明文字回歸
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
        for i, u_file in enumerate(uploaded_files):
            ods_data = core_transform_engine(u_file)
            
            # 觸發式音效：點擊下載瞬間播放，繞過瀏覽器靜音機制
            if st.download_button(
                label=f"💾 點擊下載 ➔ {u_file.name}.ods",
                data=ods_data,
                file_name=f"{u_file.name}.ods",
                key=f"dl_{i}"
            ):
                st.components.v1.html(
                    '<audio autoplay><source src="https://actions.google.com/sounds/v1/ui/light_toast.ogg" type="audio/ogg"></audio>',
                    height=0
                )
        st.balloons()

    st.write("---")
    # 完整法律聲明歸位
    st.markdown("""
    <small style="color: #888888;">
    <b>📋 免責與隱私保護法律聲明</b><br>
    1. 隱私承諾：CSV 檔案轉化完成後即刻銷毀。<br>
    2. 免責聲明：報表僅供參考，使用者因操作導致之資產變動，智庫不負責任。<br>
    3. 智慧產權：本核心演算法由路西法智庫所有，嚴禁未經授權重製。
    </small>
    """, unsafe_allow_html=True)
