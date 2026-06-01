# ==============================================================================
# 項目名稱：路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS
# 檔案名稱：ods.py
# 目前版本：v1.6.8 (Luciffar 智庫宇宙第四神器 - 音效字串結構全面重塑版)
# 更新日期：2026-06-01
# 主要功能：
#   1. 融入 Luciffar 智庫副標題英譯、A選項官方專業文案與智慧中文字元格子拉開機制。
#   2. 網頁端與本地端全面啟動版號（v1.6.8）視覺呈現。
#   3. 徹底修復第 294 行 audio_html 三引號閉合異常之 SyntaxError。
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

    # 第一輪過濾：剔除
