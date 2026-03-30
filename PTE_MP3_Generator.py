import streamlit as st
import asyncio
import edge_tts
import io
import base64
import os

# --- 1. 核心功能函数 ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except: return None
    return None

async def generate_microsoft_audio(text, voice, rate):
    if not text.strip(): return None
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
st.set_page_config(page_title="PTE Pro Player", page_icon="🎙️", layout="wide")

# 获取头像
avatar_b64 = get_base64_of_bin_file('avatar.png')

# --- 3. 注入 沉浸式播放器 CSS ---
st.markdown(f"""
    <style>
    /* 1. 隐藏多余组件 */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* 2. 左上角名片区 */
    .personal-card {{
        position: fixed;
        top: 20px;
        left: 30px;
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1000;
    }}
    .card-avatar {{
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 1.5px solid #C0C0C0;
        object-fit: cover;
    }}
    .card-info {{ display: flex; flex-direction: column; }}
    .card-name {{ margin: 0; font-size: 15px; font-weight: 700; color: inherit; }}
    .card-email {{ margin: 0; font-size: 11px; color: #888; }}

    /* 3. 文本框美化 (深/浅色适配) */
    .stTextArea textarea {{
        font-size: 20px !important;
        border-radius: 15px !important;
        padding: 20px !important;
        line-height: 1.6 !important;
    }}
    @media (prefers-color-scheme: dark) {{
        .stTextArea textarea {{ background-color: #1A1A1A !important; color: white !important; border: 1px solid #333 !important; }}
    }}
    @media (prefers-color-scheme: light) {{
        .stTextArea textarea {{ background-color: #FFFFFF !important; color: black !important; border: 1.5px solid #000000 !important; }}
    }}

    /* 4. 银色滑块控制 (对应图中倍速选择) */
    [data-testid="stSlider"] [data-baseweb="slider"] div {{ background-image: none !important; background-color: transparent !important; }}
    [data-testid="stSlider"] [role="none"] {{ background-color: #444 !important; height: 4px !important; }}
    [data-testid="stSlider"] div[role="none"] > div > div:first-child > div {{ background-color: #C0C0C0 !important; }}
    [data-testid="stSlider"] div[role="slider"] {{ background-color: white !important; border: 2px solid #C0C0C0 !important; width: 18px !important; height: 18px !important; }}

    /* 5. 按钮：黑底银边 */
    .stButton button {{
        background-color: black !important;
        color: white !important;
        border: 1px solid #555 !important;
        border-radius: 12px !important;
        height: 3em !important;
        font-weight: bold !important;
    }}
    
    /* 播放器容器 */
    .player-container {{
        background: #F0F2F6;
        border-radius: 20px;
        padding: 20px;
        margin-top: 20px;
        text-align: center;
    }}
    @media (prefers-color-scheme: dark) {{
        .player-container {{ background: #262730; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 侧边/顶部名片渲染 ---
st.markdown(f"""
    <div class="personal-card">
        {f'<img src="data:image/png;base64,{avatar_b64}" class="card-avatar">' if avatar_b64 else "👤"}
        <div class="card-info">
            <p class="card-name">Serena Shuo YANG</p>
            <p class="card-email">✉️ Rocco.yang@gmail.com</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# 腾出顶部空间
st.markdown("<br><br>", unsafe_allow_html=True)

# --- 5. 主体界面 ---
st.title("🎙️ PTE Pro Player")

text_input = st.text_area("", placeholder="请输入练习文本 (WFD/RA/RS)...", height=280)

# 倍速映射 (对应图中右下角 x1.5 逻辑)
speed_map = {
    "x0.5 (极慢)": "-50%",
    "x0.8 (略慢)": "-20%",
    "x1.0 (标准)": "+0%",
    "x1.2 (略快)": "+20%",
    "x1.5 (极快)": "+50%"
}
speed_label = st.select_slider("调节倍速", options=list(speed_map.keys()), value="x1.0 (标准)")
current_speed = speed_map[speed_label]

st.divider()

col1, col2 = st.columns(2)
EN_VOICE = "en-US-EmmaNeural"  # 标准机器音
FR_VOICE = "fr-FR-VivienneNeural"

with col1:
    if st.button("▶ 生成并播放 英文 (EN)", use_container_width=True):
        if text_input:
            with st.spinner('音频合成中...'):
                audio_fp = asyncio.run(generate_microsoft_audio(text_input, EN_VOICE, current_speed))
                if audio_fp:
                    b64 = base64.b64encode(audio_fp.getvalue()).decode()
                    st.markdown(f"""
                        <div class="player-container">
                            <p style="font-size:14px; color:#888;">正在播放: PTE_EN_Audio</p>
                            <audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                        </div>
                    """, unsafe_allow_html=True)
                    st.download_button("📥 下载 MP3", audio_fp.getvalue(), "PTE_EN.mp3", "audio/mp3")

with col2:
    if st.button("▶ 生成并播放 法语 (FR)", use_container_width=True):
        if text_input:
            with st.spinner('音频合成中...'):
                audio_fp = asyncio.run(generate_microsoft_audio(text_input, FR_VOICE, current_speed))
                if audio_fp:
                    b64 = base64.b64encode(audio_fp.getvalue()).decode()
                    st.markdown(f"""
                        <div class="player-container">
                            <p style="font-size:14px; color:#888;">正在播放: PTE_FR_Audio</p>
                            <audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                        </div>
                    """, unsafe_allow_html=True)
                    st.download_button("📥 下载 MP3", audio_fp.getvalue(), "PTE_FR.mp3", "audio/mp3")
