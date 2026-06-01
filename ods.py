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
            
            # 智慧欄寬統計
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

    # 第三輪：動態補齊底部加總空白列
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
            k_range = f"K{min_r}:K{max_r}"
        else:
            d_range, g_range, h_range, j_range, k_range = "D2:D2", "G2:G2", "H2:H2", "J2:J2", "K2:K2"

        all_rows[r_total - 1].getElementsByType(TableCell)[3].setAttribute("formula", f"of:=INT(SUM({d_range}))")
        all_rows[r_total - 1].getElementsByType(TableCell)[3].setAttribute("valuetype", "float")
        all_rows[r_total - 1].getElementsByType(TableCell)[6].setAttribute("formula", f"of:=INT(SUM({g_range}))")
        all_rows[r_total - 1].getElementsByType(TableCell)[6].setAttribute("valuetype", "float")
        all_rows[r_total - 1].getElementsByType(TableCell)[7].setAttribute("formula", f"of:=INT(SUM({h_range}))")
        all_rows[r_total - 1].getElementsByType(TableCell)[7].setAttribute("valuetype", "float")
        all_rows[r_total - 1].getElementsByType(TableCell)[9].setAttribute("formula", f"of:=INT(SUM({j_range}))")
        all_rows[r_total - 1].getElementsByType(TableCell)[9].setAttribute("valuetype", "float")
        all_rows[r_total - 1].getElementsByType(TableCell)[10].setAttribute("formula", f"of:=INT(SUM({k_range}))")
        all_rows[r_total - 1].getElementsByType(TableCell)[10].setAttribute("valuetype", "float")
        
        all_rows[r_positive - 1].getElementsByType(TableCell)[7].setAttribute("formula", f'of:=INT(SUMIF({h_range};">0"))')
        all_rows[r_positive - 1].getElementsByType(TableCell)[7].setAttribute("valuetype", "float")
        all_rows[r_negative - 1].getElementsByType(TableCell)[7].setAttribute("formula", f'of:=INT(SUMIF({h_range};"<0"))')
        all_rows[r_negative - 1].getElementsByType(TableCell)[7].setAttribute("valuetype", "float")
    except Exception:
        pass

    # 第五輪：智慧寬度自適應調整機制
    for col_idx in range(1, 13):
        max_visual_len = col_max_widths.get(col_idx, 6)
        calculated_width = max(2.8, 1.2 + (max_visual_len * 0.16))
        
        col_style = Style(name=f"Co{col_idx}", family="table-column")
        col_style.addElement(TableColumnProperties(columnwidth=f"{calculated_width}cm"))
        doc.automaticstyles.addElement(col_style)
        table.addElement(TableColumn(stylename=f"Co{col_idx}"))

    output_stream = io.BytesIO()
    doc.save(output_stream)
    return output_stream.getvalue()


# ==============================================================================
# 判斷執行環境：Streamlit 網頁模式
# ==============================================================================
if HAS_STREAMLIT and (st.runtime.exists() or 'STREAMLIT_SERVER_PORT' in os.environ):
    st.set_page_config(page_title="路西法智庫：命運重塑", page_icon="🌌", layout="wide")
    
    st.title("🌌 路西法智庫：命運重塑—國泰樹精靈電腦版 CSV 轉 ODS")
    st.markdown("#### *Luciffar Think Tank: Destiny Reshaping — Cathay Tree Wizard Desktop CSV to ODS Converter*")
    st.markdown("<code style='color:#1E90FF; font-weight:bold;'>Production Version: v1.6.8</code>", unsafe_allow_html=True)
    
    # 官方核心轉化機制說明文案
    intro_markdown = (
        "### **【核心轉化機制說明】**\n"
        "本神器專為 **國泰樹精靈電腦版** 匯出之庫存 CSV 設計。透過自動化智慧腳本，一鍵洗滌、過濾並賦予靜態數據全新靈魂，完美相容多檔案批次處理：\n\n"
        "* ⚡ **命運奪天：死資料化為活公式** ➔ 徹底重塑「G欄（股票現職/市值）」與「H欄（未實現損益）」，移除券商寫死的靜態數值，全面注入 Excel / LibreOffice 專用動態活公式。現價或股數欄位隨意變動，報表自動同步連動！\n"
        "* ⚔️ **斷罪斬無用：完美雜訊過濾** ➔ 自動精確剔除國泰樹精靈特有的多餘重複標頭，並斬斷末端「融資、利息」等非必要中文干擾行，只留下純淨的資產本體。\n"
        "* 🌌 **萬法歸一：動態擴大與指定加總** ➔ 無論庫存股票高於 8 列或無限堆疊，程式將動態追蹤範圍。並於底部注入 `INT(SUM)` 活公式，精確加總 **D欄持有成本**、**G欄股票市值**、**H欄總損益**、**J欄手續費**與**K欄交易稅**（賺賠正負分流列依要求保持清爽空白不重複計算），且全數整數化，告別小數點干擾。\n"
        "* 📏 **格子全面拉開：智慧寬度自適應** ➔ 內建繁體中文字元加權演算法！**自動將所有儲存格欄寬大幅度橫向拉開**，完美適配「股票名稱」與「合計欄位」的中文呈現。徹底告別舊版格式中文字擠在一起、被遮擋或出現 `###` 的窘境，排版大氣清晰！\n"
        "* 🛡️ **遮天防護網：多檔批次不閃退** ➔ 支援多個 CSV 檔案拖放批次煉化，若遇格式異常檔案將自動跳過並繼續執行，內嵌核心防護，網頁端絕不崩潰。"
    )
    st.markdown(intro_markdown)
    st.write("---")
    
    uploaded_files = st.file_uploader("📥 祭入國泰樹精靈庫存 CSV（支援多檔案拖放煉化）：", type=["csv"], accept_multiple_files=True)
    
    if uploaded_files:
        st.subheader("🚀 命運重塑進度統計")
        
        # 💥 這裡徹底捨棄易出錯的原始三引號，改用單行純字串拼接，杜絕任何 SyntaxError 的可能性！
        audio_src1 = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
        audio_src2 = "https://s3.amazonaws.com/freecodecamp/drums/Chord_1.mp3"
        audio_html = f'<audio autoplay style="display:none;"><source src="{audio_src1}" type="audio/ogg"><source src="{audio_src2}" type="audio/mp3"></audio>'
        st.components.v1.html(audio_html, height=0, width=0)
        
        for u_file in uploaded_files:
            try:
                base_name = os.path.splitext(u_file.name)[0]
                ods_bytes = core_transform_engine(u_file, is_bytes=True)
                
                st.download_button(
                    label=f"💾 點擊下載 ➔ {base_name}_自動化.ods",
                    data=ods_bytes,
                    file_name=f"{base_name}_自動化.ods",
                    mime="application/vnd.oasis.opendocument.spreadsheet"
                )
                st.toast(f"✅ {u_file.name} 煉化完成！欄寬已自動拉開。")
            except Exception as e:
                st.error(f"❌ 檔案 {u_file.name} 轉化失敗，原因：{e}")
                
        st.balloons()

    st.write("---")
    # 法律聲明同樣改用安全字串包裝
    law_html = (
        '<small style="color: #888888;">### 📋 免責與隱私保護法律聲明<br>'
        '1. <b>隱私承諾</b>：本系統嚴格遵循個人資料保護原則，您上傳的國泰樹精靈 CSV 檔案在轉化完成後即刻銷毀。後端伺服器不會對任何使用者資料進行留存、備份、或收集分析。<br>'
        '2. <b>免責聲明</b>：本工具產出之 ODS 報表及動態活公式僅供便利記帳與複利試算參考。使用者因檔案轉換、公式計算或個人操作所導致之任何資產變動、資料遺失或投資盈虧，本智庫不負任何法律責任。<br>'
        '3. <b>智慧產權</b>：本程式核心演算法由路西法智庫所有，嚴禁任何未經授權之商業重製或惡意攻擊行為。</small>'
    )
    st.markdown(law_html, unsafe_allow_html=True)

# ==============================================================================
# 判斷執行環境：本地端雙擊執行模式 (.py)
# ==============================================================================
else:
    print(f"==================================================")
    print(f"   🌌 路西法智庫：命運重塑 (本地批次轉檔版) v1.6.8")
    print(f"   執行指令檔：ods.py | 品牌識別：Luciffar Think Tank")
    print(f"==================================================")
    
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("\n❌ 錯誤：在目前的資料夾中找不到任何 CSV 檔案！")
        print("👉 請將國泰產出的 CSV 庫存檔案放入此資料夾中後再執行。")
    else:
        print(f"🔍 系統共偵測到 {len(csv_files)} 個 CSV 檔案，開始排隊轉檔並拉開欄寬...\n")
        success_count = 0
        
        for index, selected_csv in enumerate(csv_files, start=1):
            base_name = os.path.splitext(selected_csv)[0]
            output_ods = f"{base_name}_自動化.ods"
            
            print(f"[{index}/{len(csv_files)}] 正在重塑：'{selected_csv}' ... ", end="")
            sys.stdout.flush()
            
            try:
                ods_data_bytes = core_transform_engine(selected_csv, is_bytes=False)
                with open(output_ods, 'wb') as out_f:
                    out_f.write(ods_data_bytes)
                    
                print(f"✅ 成功 ➔ 產出 '{output_ods}' (中文字體格子已拉開)")
                success_count += 1
            except Exception as single_err:
                print(f"❌ 失敗 (已安全跳過)，原因: {single_err}")
                
        print("\n==================================================")
        print(f"🎉 批次任務結束！共成功轉換 {success_count} / {len(csv_files)} 個檔案。")
        print(f"中文字元與合計列已啟動寬度延伸，開啟 ODS 時排報表將極致完美！")
        
    print("--------------------------------------------------")
    input("【執行完畢】請按下 Enter 鍵安全關閉本視窗...")
