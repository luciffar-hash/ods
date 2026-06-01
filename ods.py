# ==============================================================================
# 項目名稱：路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS
# 檔案名稱：ods.py
# 目前版本：v1.6.3 (Luciffar 智庫宇宙第四神器 - 核心屬性字串完美修復版)
# 更新日期：2026-06-01
# 主要功能：
#   1. 融入 Luciffar 智庫副標題英譯、A選項官方專業文案與智慧中文字元格子拉開機制。
#   2. 網頁端與本地端全面啟動版號（v1.6.3）視覺呈現。
#   3. 完美修復第 177 行屬性設定中字串引號未閉合之 SyntaxError 錯誤。
#   4. 完美嵌入轉換成功音效、動態氣球特效，客製化上傳按鈕文字。
#   5. 精確對準 D成本、G市值、H損益、J手續費、K交易稅，底部注入 INT(SUM) 活公式。
#   6. 底部嚴謹融入「免責與隱私保護法律聲明」防護網。
# ==============================================================================

import sys
import subprocess
import io
import csv
import glob
import os

# 嘗試讀取 Streamlit，若失敗則判定為本地純腳本執行模式
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# 【自動安裝機制】本地執行時如果缺少 odfpy 則自動代裝
try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
    from odf.style import Style, TextProperties, TableCellProperties, TableColumnProperties
    from odf.table import TableColumn
except ImportError:
    if not HAS_STREAMLIT:
        print(f"【系統通知】正在自動為您安裝必要的 odfpy 套件，請稍候...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "odfpy"])
            from odf.opendocument import OpenDocumentSpreadsheet
            from odf.table import Table, TableRow, TableCell
            from odf.text import P
            from odf.style import Style, TextProperties, TableCellProperties, TableColumnProperties
            from odf.table import TableColumn
            print("✅ 套件安裝成功！\n")
        except Exception as e:
            print(f"❌ 自動安裝套件失敗，請手動執行 'pip install odfpy'。錯誤: {e}")
            input("請按下 Enter 鍵關閉視窗...")
            exit(1)
    else:
        raise ImportError("請在 requirements.txt 中加入 odfpy 與 streamlit")

def core_transform_engine(csv_file_obj, is_bytes=False):
    """
    核心萬象重構引擎：負責洗滌數據、注入活公式、並進行智慧中文字元欄寬延展
    """
    doc = OpenDocumentSpreadsheet()
    
    # 樣式定義
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
    
    # 讀取 CSV 內容
    raw_rows = []
    if is_bytes:
        content = csv_file_obj.getvalue()
        for encoding in ['big5', 'utf-8', 'gbk']:
            try:
                decoded_content = content.decode(encoding, errors='ignore')
                raw_rows = list(csv.reader(io.StringIO(decoded_content)))
                if raw_rows: break
            except Exception:
                continue
    else:
        try:
            with open(csv_file_obj, 'r', encoding='big5', errors='ignore') as f:
                raw_rows = list(csv.reader(f))
        except Exception:
            with open(csv_file_obj, 'r', encoding='utf-8', errors='ignore') as f:
                raw_rows = list(csv.reader(f))

    processed_rows = []
    data_row_indices = []
    has_header_written = False
    current_out_idx = 0

    # 第一輪過濾：剔除重複標頭與國泰雜訊
    for r in raw_rows:
        if not r or len(r) == 0:
            continue
        r = [cell.strip() for cell in r]
        if not any(cell for cell in r): 
            continue
            
        first_cell = r[0]
        if "股票名稱" in first_cell:
            if not has_header_written:
                processed_rows.append(r)
                current_out_idx += 1
                has_header_written = True
            continue 
            
        if len(r) > 8 and "融資" in r[8]:
            continue
        if any(keyword in first_cell for keyword in ["總和", "加總", "損益", "合計"]):
            continue

        processed_rows.append(r)
        current_out_idx += 1
        data_row_indices.append(current_out_idx)

    # 智慧欄寬字數動態統計追蹤
    col_max_widths = {}

    # 第二輪：資料與活公式注入
    for out_row_idx, row in enumerate(processed_rows, start=1):
        tr = TableRow()
        table.addElement(tr)
        
        is_header = (out_row_idx == 1)
        while len(row) < 12:
            row.append("")
            
        for col_idx, cell_value in enumerate(row, start=1):
            col_letter = chr(64 + col_idx) if col_idx <= 26 else "A" + chr(64 + col_idx - 26)
            tc = TableCell()
            
            # 智慧欄寬統計：中文字元在試算表中實際佔據雙倍寬度，此處進行加權計算防止中文字擠壓
            if cell_value:
                visual_len = sum(2 if ord(char) > 127 else 1 for char in cell_value)
                col_max_widths[col_idx] = max(col_max_widths.get(col_idx, 0), visual_len)
            
            if is_header:
                tc.setAttribute("stylename", header_style)
                tc.addElement(P(text=cell_value))
            else:
                tc.setAttribute("stylename", data_style)
                
                if out_row_idx in data_row_indices:
                    orig_market_val = row[6].replace(',', '') if len(row) > 6 else ""
                    orig_profit_val = row[7].replace(',', '') if len(row) > 7 else ""
                    if '.' in orig_market_val: orig_market_val = orig_market_val.split('.')[0]
                    if '.' in orig_profit_val: orig_profit_val = orig_profit_val.split('.')[0]

                    if col_letter == 'G':
                        tc.setAttribute("formula", f"of:=INT(C{out_row_idx}*F{out_row_idx})")
                        tc.setAttribute("valuetype", "float")
                        if orig_market_val: tc.setAttribute("value", orig_market_val)
                    elif col_letter == 'H':
                        tc.setAttribute("formula", f"of:=G{out_row_idx}-D{out_row_idx}")
                        tc.setAttribute("valuetype", "float")
                        if orig_profit_val: tc.setAttribute("value", orig_profit_val)
                    elif col_letter == 'I':
                        try:
                            pure_num = float(cell_value.replace('%', '').replace(',', ''))
                            clean_percent_str = f"{int(round(pure_num))}%" if '%' in cell_value else f"{int(round(pure_num*100))}%"
                            tc.addElement(P(text=clean_percent_str))
                        except ValueError:
                            tc.addElement(P(text=cell_value))
                    elif col_letter in ['C', 'D', 'J', 'K']:
                        try:
                            clean_num = cell_value.replace(',', '')
                            if '.' in clean_num: clean_num = clean_num.split('.')[0]
                            if clean_num:
                                tc.setAttribute("value", clean_num)
                                tc.setAttribute("valuetype", "float")
                            else:
                                tc.addElement(P(text=cell_value))
                        except ValueError:
                            tc.addElement(P(text=cell_value))
                    elif col_letter in ['E', 'F']:
                        try:
                            tc.setAttribute("value", cell_value.replace(',', ''))
                            tc.setAttribute("valuetype", "float")
                        except ValueError:
                            tc.addElement(P(text=cell_value))
                    else:
                        tc.addElement(P(text=cell_value))
                else:
                    if cell_value: tc.addElement(P(text=cell_value))
                    
            tr.addElement(tc)

    # 第三輪：動態補齊底部加總空白列 (合計、正損益、負損益)
    for _ in range(5):
        tr = TableRow()
        table.addElement(tr)
        for _ in range(12):
            tc = TableCell()
            tc.setAttribute("stylename", data_style)
            tr.addElement(tc)

    # 第四輪：動態計算與精確活公式加總注入
    try:
        all_rows = table.getElementsByType(TableRow)
        total_rows_count = len(processed_rows)
        
        r_total = total_rows_count + 2
        r_positive = total_rows_count + 3
        r_negative = total_rows_count + 4
        
        all_rows[r_total - 1].getElementsByType(TableCell)[0].addElement(P(text="合計 / 總資產"))
        all_rows[r_positive - 1].getElementsByType(TableCell)[0].addElement(P(text="正損益加總 (賺)"))
        all_rows[r_negative - 1].getElementsByType(TableCell)[0].addElement(P(text="負損益加總 (賠)"))

        if data_row_indices:
            min_r, max_r = min(data_row_indices), max(data_row_indices)
            d_range = f"D{min_r}:D{max_r}"
            g_range = f"G{min_r}:G{max_r}"
            h_range = f"H{min_r}:H{max_r}"
            j_range = f"J{min_r}:J{max_r}"
            k_
