import streamlit as st
import asyncio
import edge_tts
import io
import base64
import os

# --- 1. 核心功能函数 ---

def get_base64_of_bin_file(bin_file):
    """读取本地文件并转换为 Base64，用于显示头像"""
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except: return None
    return None

async def generate_microsoft_audio(text, voice, rate):
    """调用微软 Edge TTS 引擎生成异步语音流"""
    if not text.strip():
        return None
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return io.BytesIO(audio_data)
    except Exception as e:
        st.error(f"语音合成失败: {e}")
        return None

# --- 2. 页面基础配置 ---
st.set_page_config(page_title="PTE/TCF MP3 Generator", page_icon="🎙️")

# --- 3. 获取头像 Base64 ---
avatar_b64 = get_base64_of_bin_file('avatar.png')

# --- 4. 注入 极简黑白灰 CSS (适配深/浅色主题) ---
st.markdown(f"""
    <style>
    /* 1. 徹底抹除所有可能的紅色 (核心變量) */
    :root {{ 
        --primary-color: #C0C0C0 !important; 
    }}

    /* 2. 左上角個人名片區 (黑白灰風格) */
    .stSidebar {{
        background-color: transparent !important;
    }}
    
    [data-testid="stSidebarContent"] {{
        display: none !important; /* 隱藏側邊欄預設內容 */
    }}

    /* 手動創建左上角名片 */
    .stApp > header {{
        display: none !important; /* 隱藏頂部藍色/黑色條 */
    }}
    
    .personal-card {{
        position: absolute;
        top: 20px;
        left: 20px;
        display: flex;
        align-items: center;
        gap: 15px;
        z-index: 10000;
        padding: 5px;
        background-color: transparent;
    }}
    
    .card-avatar {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: 2px solid #C0C0C0; /* 銀色邊框 */
        object-fit: cover;
    }}
    
    .card-info {{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    
    .card-name {{
        margin: 0;
        font-size: 16px;
        font-weight: 700;
        color: inherit; /* 隨主題變化 */
    }}
    
    .card-email {{
        margin: 0;
        font-size: 12px;
        color: #777;
    }}

    /* 3. 徹底抹除滑塊紅線 */
    /* 移除紅色的背景漸變圖 */
    [data-testid="stSlider"] [data-baseweb="slider"] div {{
        background-image: none !important;
        background-color: transparent !important;
    }}
    
    /* 滑塊未選中部分的軌道：深灰色 (深色主題) */
    [data-testid="stSlider"] [role="none"] {{
        background-color: #444444 !important;
        height: 6px !important;
        border-radius: 3px !important;
    }}

    /* 滑塊已選中（左側）部分的軌道：銀灰色 */
    [data-testid="stSlider"] div[role="none"] > div > div:first-child > div {{
        background-color: #C0C0C0 !important;
        background-image: none !important;
    }}

    /* 滑塊圓點：白底銀邊 */
    [data-testid="stSlider"] div[role="slider"] {{
        background-color: #FFFFFF !important;
        border: 2px solid #C0C0C0 !important;
        width: 20px !important;
        height: 20px !important;
        box-shadow: none !important;
    }}

    /* 4. 字號與標籤樣式 */
    [data-testid="stWidgetLabel"] p {{ font-size: 20px !important; color: inherit; font-weight: bold !important; }}
    [data-testid="stSliderTickBar"] div {{ font-size: 15px !important; color: #C0C0C0 !important; }}

    /* 5. 按鈕美化 */
    .stButton button {{ font-size: 18px !important; background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #555 !important; border-radius: 10px !important; }}
    
    /* 隱藏所有紅色刻度小點 */
    [data-testid="stTickBar"] {{ display: none !important; }}

    /* ========================================================== */
    /* 6. 【關鍵】文本框樣式適配 (深色/淺色主題) */
    /* ========================================================== */
    
    /* 文本框通用樣式 (字號、行高、圓角) */
    .stTextArea textarea {{ 
        font-size: 22px !important; 
        line-height: 1.6 !important; 
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }}

    /* --- 深色主題 (Dark Theme) 下的文本框 --- */
    @media (prefers-color-scheme: dark) {{
        .stTextArea textarea {{
            color: #444444 !important;
            background-color: transparent !important;
            border: 1px solid #444444 !important;
        }}
    }}

    /* --- 淺色主題 (Light Theme) 下的文本框 --- */
    @media (prefers-color-scheme: light) {{
        .stTextArea textarea {{
            color: #000000 !important;   /* 黑字 */
            background-color: #FFFFFF !important; /* 白底 */
            border: 1px solid #000000 !important; /* 黑框 */
        }}
        
        /* 淺色主題下調整滑塊底色，防止看不清 */
        [data-testid="stSlider"] [role="none"] {{
            background-color: #DDDDDD !important; /* 淺灰軌道 */
        }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. 左上角個人名片 HTML ---
footer_html = f"""
    <div class="personal-card">
        {f'<img src="data:image/png;base64,{avatar_b64}" class="card-avatar">' if avatar_b64 else "👤"}
        <div class="card-info">
            <p class="card-name">Serena Shuo YANG</p>
            <p class="card-email"> EMAIL: Rocco.yang@gmail.com</p>
        </div>
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)


# --- 6. 页面标题 ---
# 为了给左上角腾出空间，标题增加一点间距
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
st.title("🎙️ PTE Pro MP3 Generator")
st.write("输入文本，一键生成英文或法文音频。")

# --- 7. 用户输入区域 ---
text_input = st.text_area(
    "请输入你想要转换的文本：", 
    placeholder="在此粘贴阅读或口语文本...", 
    height=380
)

# 语速调节逻辑：将滑块选项转换为 edge-tts 识别的百分比字符串
speed_options = {
    "极慢 (-50%)": "-50%",
    "略慢 (-20%)": "-20%",
    "标准速度": "+0%",
    "略快 (+15%)": "+15%",
    "极快 (+30%)": "+30%"
}
speed_label = st.select_slider("调节语速 (PTE 练习建议选择标准或略慢)", options=list(speed_options.keys()), value="标准速度")
current_speed = speed_options[speed_label]

# --- 8. 生成与播放区域 ---
col1, col2 = st.columns(2)

# 配置微软声音 (推荐用这两个，滑块精准)
EN_VOICE = "en-US-EmmaNeural"   # 机器感标准女声
FR_VOICE = "fr-FR-VivienneNeural" # 优雅的法国女声

with col1:
    if st.button("生成英文 (EN)", use_container_width=True):
        if text_input:
            with st.spinner('正在合成机器音...'):
                audio_fp = asyncio.run(generate_microsoft_audio(text_input, EN_VOICE, current_speed))
                if audio_fp:
                    audio_bytes = audio_fp.getvalue()
                    b64 = base64.b64encode(audio_bytes).decode()
                    st.markdown(f'<audio controls style="width: 100%; margin-top:10px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    st.download_button("📥 下载 MP3", data=audio_bytes, file_name="PTE_EN.mp3", mime="audio/mp3")
        else:
            st.warning("请先输入文本")

with col2:
    if st.button("生成法语 (FR)", use_container_width=True):
        if text_input:
            with st.spinner('正在合成法语...'):
                audio_fp = asyncio.run(generate_microsoft_audio(text_input, FR_VOICE, current_speed))
                if audio_fp:
                    audio_bytes = audio_fp.getvalue()
                    b64 = base64.b64encode(audio_bytes).decode()
                    st.markdown(f'<audio controls style="width: 100%; margin-top:10px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    st.download_button("📥 下载 MP3", data=audio_bytes, file_name="PTE_FR.mp3", mime="audio/mp3")
        else:
            st.warning("请先输入文本")

