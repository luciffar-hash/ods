# ==============================================================================
# 項目名稱：路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS
# 英文譯名：Luciffar Think Tank: Destiny Reshaping — Cathay Tree Wizard
# 目前版本：v1.7.6 (Luciffar 智庫宇宙最終音效解鎖版)
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
    st.title("🌌 路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS")
    st.markdown("#### *Luciffar Think Tank: Destiny Reshaping — Cathay Tree Wizard Desktop CSV to ODS Converter*")
    
    uploaded_files = st.file_uploader("📥 祭入國泰樹精靈庫存 CSV：", type=["csv"], accept_multiple_files=True)
    
    if uploaded_files:
        # 在按下下載後，利用按鈕的點擊事件來觸發音效，繞過瀏覽器封鎖
        for i, u_file in enumerate(uploaded_files):
            ods_data = core_transform_engine(u_file)
            
            # 使用 container 容納按鈕與對應音效
            if st.download_button(
                label=f"💾 點擊下載 ➔ {u_file.name}.ods",
                data=ods_data,
                file_name=f"{u_file.name}.ods",
                key=f"dl_{i}",
                on_click=None 
            ):
                # 這裡透過 HTML5 嵌入，並由下載按鈕點擊後產生的互動權限來允許播放
                st.components.v1.html(
                    '<audio autoplay><source src="https://actions.google.com/sounds/v1/ui/light_toast.ogg" type="audio/ogg"></audio>',
                    height=0
                )
        st.balloons()

    st.write("---")
    st.markdown("""
    <small style="color: #888888;">
    <b>📋 免責聲明</b>：點擊下載後將會播放輕柔提示音。若仍無聲，請確認瀏覽器分頁是否被靜音。
    </small>
    """, unsafe_allow_html=True)
