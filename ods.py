# ==============================================================================
# 項目名稱：路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS
# 檔案名稱：ods.py
# 目前版本：v1.6.9 (Luciffar 智庫宇宙純淨無聲版)
# 更新日期：2026-06-01
# 主要功能：
#   1. 融入 Luciffar 智庫副標題英譯、A選項官方專業文案與智慧中文字元格子拉開機制。
#   2. 網頁端與本地端全面啟動版號（v1.6.9）視覺呈現。
#   3. 徹底移除音效，提供極致靜謐的轉檔環境。
#   4. 精確對準 D成本、G市值、H損益、J手續費、K交易稅，底部注入 INT(SUM) 活公式。
#   5. 底部嚴謹融入「免責與隱私保護法律聲明」防護網。
# ==============================================================================

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
    else:
        raise ImportError("請在 requirements.txt 中加入 odfpy 與 streamlit")

def core_transform_engine(csv_file_obj, is_bytes=False):
    """核心萬象重構引擎：負責洗滌數據、注入活公式、並進行智慧中文字元欄寬延展"""
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
            except: continue
    else:
        try:
            with open(csv_file_obj, 'r', encoding='big5', errors='ignore') as f:
                raw_rows = list(csv.reader(f))
        except:
            with open(csv_file_obj, 'r', encoding='utf-8', errors='ignore') as f:
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

    col_max_widths = {}
    for out_row_idx, row in enumerate(processed_rows, start=1):
        tr = TableRow()
        table.addElement(tr)
        while len(row) < 12: row.append("")
        for col_idx, cell_value in enumerate(row, start=1):
            col_letter = chr(64 + col_idx) if col_idx <= 26 else "A" + chr(64 + col_idx - 26)
            tc = TableCell()
            if cell_value:
                visual_len = sum(2 if ord(char) > 127 else 1 for char in cell_value)
                col_max_widths[col_idx] = max(col_max_widths.get(col_idx, 0), visual_len)
            
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

    for _ in range(5):
        tr = TableRow()
        table.addElement(tr)
        for _ in range(12):
            tc = TableCell()
            tc.setAttribute("stylename", data_style)
            tr.addElement(tc)

    try:
        all_rows = table.getElementsByType(TableRow)
        total_rows_count = len(processed_rows)
        r_total, r_pos, r_neg = total_rows_count + 2, total_rows_count + 3, total_rows_count + 4
        all_rows[r_total - 1].getElementsByType(TableCell)[0].addElement(P(text="合計 / 總資產"))
        all_rows[r_pos - 1].getElementsByType(TableCell)[0].addElement(P(text="正損益加總 (賺)"))
        all_rows[r_neg - 1].getElementsByType(TableCell)[0].addElement(P(text="負損益加總 (賠)"))

        if data_row_indices:
            min_r, max_r = min(data_row_indices), max(data_row_indices)
            d, g, h, j, k = f"D{min_r}:D{max_r}", f"G{min_r}:G{max_r}", f"H{min_r}:H{max_r}", f"J{min_r}:J{max_r}", f"K{min_r}:K{max_r}"
        else:
            d, g, h, j, k = "D2:D2", "G2:G2", "H2:H2", "J2:J2", "K2:K2"

        for i, rng in enumerate([d, g, h, j, k]):
            idx = [3, 6, 7, 9, 10][i]
            all_rows[r_total - 1].getElementsByType(TableCell)[idx].setAttribute("formula", f"of:=INT(SUM({rng}))")
            all_rows[r_total - 1].getElementsByType(TableCell)[idx].setAttribute("valuetype", "float")
        
        all_rows[r_pos - 1].getElementsByType(TableCell)[7].setAttribute("formula", f'of:=INT(SUMIF({h};">0"))')
        all_rows[r_neg - 1].getElementsByType(TableCell)[7].setAttribute("formula", f'of:=INT(SUMIF({h};"<0"))')
    except: pass

    for col_idx in range(1, 13):
        max_v = col_max_widths.get(col_idx, 6)
        width = max(2.8, 1.2 + (max_v * 0.16))
        col_style = Style(name=f"Co{col_idx}", family="table-column")
        col_style.addElement(TableColumnProperties(columnwidth=f"{width}cm"))
        doc.automaticstyles.addElement(col_style)
        table.addElement(TableColumn(stylename=f"Co{col_idx}"))

    output_stream = io.BytesIO()
    doc.save(output_stream)
    return output_stream.getvalue()

if HAS_STREAMLIT and (st.runtime.exists() or 'STREAMLIT_SERVER_PORT' in os.environ):
    st.set_page_config(page_title="路西法智庫：命運重塑", page_icon="🌌", layout="wide")
    st.title("🌌 路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS")
    st.markdown("#### *Luciffar Think Tank: Destiny Reshaping — Cathay Tree Wizard Desktop CSV to ODS Converter*")
    st.markdown("<code style='color:#1E90FF; font-weight:bold;'>Production Version: v1.6.9 (Clean/Silent)</code>", unsafe_allow_html=True)
    
    intro_markdown = (
        "### **【核心轉化機制說明】**\n"
        "本神器專為 **國泰樹精靈電腦版** 匯出之庫存 CSV 設計。透過自動化智慧腳本，一鍵洗滌、過濾並賦予靜態數據全新靈魂：\n\n"
        "* ⚡ **命運奪天：死資料化為活公式** ➔ 徹底重塑市值與損益欄，自動注入 Excel / LibreOffice 專用動態活公式，告別券商死數值。\n"
        "* ⚔️ **斷罪斬無用：完美雜訊過濾** ➔ 自動精確剔除重複標頭與末端雜訊，只留下純淨資產本體。\n"
        "* 🌌 **萬法歸一：動態擴大與指定加總** ➔ 無論庫存長度，程式將動態追蹤並於底部注入 `INT(SUM)` 活公式，整數化呈現告別小數點。\n"
        "* 📏 **格子全面拉開：智慧寬度自適應** ➔ 內建繁體中文字元加權演算法！自動將儲存格欄寬大幅拉開，排版大氣清晰。"
    )
    st.markdown(intro_markdown)
    st.write("---")
    
    uploaded_files = st.file_uploader("📥 祭入國泰樹精靈庫存 CSV（支援多檔案批次煉化）：", type=["csv"], accept_multiple_files=True)
    if uploaded_files:
        st.subheader("🚀 命運重塑進度")
        for u_file in uploaded_files:
            try:
                base = os.path.splitext(u_file.name)[0]
                st.download_button(f"💾 下載 ➔ {base}_自動化.ods", core_transform_engine(u_file, True), f"{base}_自動化.ods", "application/vnd.oasis.opendocument.spreadsheet")
                st.toast(f"✅ {u_file.name} 煉化完成")
            except Exception as e: st.error(f"❌ 煉化失敗: {e}")
        st.balloons()
    
    st.write("---")
    law_html = (
        '<small style="color: #888888;">### 📋 免責與隱私保護法律聲明<br>'
        '1. <b>隱私承諾</b>：您上傳的資料僅供轉化，即轉即銷，不留存任何個人數據。<br>'
        '2. <b>免責聲明</b>：本工具產出之報表僅供便利記帳與複利試算參考。使用者因檔案轉換或公式計算導致之投資盈虧，本智庫不負法律責任。<br>'
        '3. <b>智慧產權</b>：核心演算法由路西法智庫所有，嚴禁未經授權之商業重製。</small>'
    )
    st.markdown(law_html, unsafe_allow_html=True)
else:
    print("\n[本地模式] 執行中...")
    csv_files = glob.glob("*.csv")
    for s in csv_files:
        with open(f"{os.path.splitext(s)[0]}_自動化.ods", "wb") as f: f.write(core_transform_engine(s))
        print(f"✅ 成功: {s}")
    input("\n執行完畢，按 Enter
