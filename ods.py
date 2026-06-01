import streamlit as st

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="Luciffar AI: Dawnstar Command", 
    layout="centered",
    page_icon="⭐"
)

# --- 2. 戰情室 CSS 樣式 ---
st.markdown("""
    <style>
    .stApp { background-color: #0A0A0A; color: #FFFFFF; }
    h1, h2, h3 { color: #FFD700; }
    
    /* 戰略識別標籤：綠色字體與分層排版 */
    .header-tag { 
        background-color: #1a1a1a; 
        padding: 10px; 
        border-left: 4px solid #00FF41; 
        margin-bottom: 20px;
        display: block;
    }
    .chinese-title { color: #00FF41; font-weight: bold; font-size: 1.1rem; display: block; }
    .english-title { color: #00FF41; font-size: 0.85rem; font-family: monospace; display: block; }
    .version-tag { color: #888; font-size: 0.75rem; margin-top: 5px; }
    
    .stButton>button { 
        width: 100%; border: 1px solid #FFD700; color: #FFD700; 
        background: transparent; border-radius: 0px; margin-top: 10px;
    }
    .stButton>button:hover { background: #FFD700; color: #0A0A0A; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 頁面頂部 ---
# 中文在英文上面，統一綠色字體
st.markdown("""
    <div class='header-tag'>
        <span class='chinese-title'>路西法智庫:AI破曉晨星戰略指揮總部</span>
        <span class='english-title'>Luciffar AI: Dawnstar Command</span>
        <span class='version-tag'>SYSTEM VERSION: 1.0.0</span>
    </div>
""", unsafe_allow_html=True)

try:
    st.image("logo.png", width=250)
except:
    st.error("Error: logo.png not found.")

st.title("Luciffar AI")
st.subheader("Dawnstar Command")
st.markdown("---")

# --- 4. 戰略指揮面板 ---
st.write("#### 🛡️ 戰略指揮模組 (Active Command Deck)")

tools = [
    {"name": "Decision Eye", "url": "https://luciffar-thinktank.streamlit.app/"},
    {"name": "Python Compiler", "url": "https://luciffar-py.streamlit.app/"},
    {"name": "YT Linker", "url": "https://luciffar-yturl.streamlit.app/"},
    {"name": "CSV Converter", "url": "https://luciffar-ods.streamlit.app/"}
]

cols = st.columns(2)
for i, tool in enumerate(tools):
    with cols[i % 2]:
        st.write(f"### {tool['name']}")
        st.link_button(f"EXECUTE", tool['url'], use_container_width=True)
        st.write("") 

# --- 5. 底部狀態列 ---
st.markdown("---")
st.caption("Dawnstar Command | Operational | All Systems Online")
