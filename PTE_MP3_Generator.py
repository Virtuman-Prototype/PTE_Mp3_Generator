import streamlit as st
import asyncio
import edge_tts
from gtts import gTTS
import io
import base64
import os

# --- 1. 核心功能函数 ---

def get_base64_of_bin_file(bin_file):
    """读取头像文件"""
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except: return None
    return None

def generate_google_audio(text, lang='en'):
    """使用 gTTS 生成英语语音 (Google)"""
    if not text.strip(): return None
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception as e:
        st.error(f"Google 语音合成失败: {e}")
        return None

async def generate_microsoft_audio(text, voice, rate="+0%"):
    """使用 Edge TTS 生成法语语音 (Microsoft)"""
    if not text.strip(): return None
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return io.BytesIO(audio_data)
    except Exception as e:
        st.error(f"微软语音合成失败: {e}")
        return None

# --- 2. 页面配置与黑白灰深色主题 ---
st.set_page_config(page_title="PTE Pro", page_icon="🎙️")

st.markdown("""
    <style>
    /* 1. 全局去红：将 Streamlit 主色调改为银色 */
    :root { --primary-color: #C0C0C0 !important; }

    /* 2. 彻底抹除滑块红线 */
    /* 移除红色的背景渐变图 */
    [data-testid="stSlider"] [data-baseweb="slider"] div {
        background-image: none !important;
        background-color: transparent !important;
    }
    
    /* 滑块未选中部分的轨道：深灰色 */
    [data-testid="stSlider"] [role="none"] {
        background-color: #444444 !important;
        height: 6px !important;
        border-radius: 3px !important;
    }

    /* 滑块已选中（左侧）部分的轨道：银灰色 */
    [data-testid="stSlider"] div[role="none"] > div > div:first-child > div {
        background-color: #C0C0C0 !important;
        background-image: none !important;
    }

    /* 滑块圆点：白底银边 */
    [data-testid="stSlider"] div[role="slider"] {
        background-color: #FFFFFF !important;
        border: 2px solid #C0C0C0 !important;
        width: 20px !important;
        height: 20px !important;
        box-shadow: none !important;
    }

    /* 3. 文字大小与颜色 */
    .stTextArea textarea { font-size: 22px !important; line-height: 1.6 !important; color: #FFFFFF !important; background-color: #1E1E1E !important; }
    [data-testid="stWidgetLabel"] p { font-size: 20px !important; color: #E0E0E0 !important; font-weight: bold !important; }
    [data-testid="stSliderTickBar"] div { font-size: 15px !important; color: #C0C0C0 !important; }

    /* 4. 按钮美化 */
    .stButton button { font-size: 18px !important; background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #555 !important; border-radius: 10px !important; }
    
    /* 隐藏所有红色刻度小点 */
    [data-testid="stTickBar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ PTE & TCF MP3 Generator")
st.caption("Test in COUV Edu.")

# --- 3. 输入区域 ---
text_input = st.text_area("请输入练习文本：", placeholder="在此输入内容...", height=300)

# --- 3.5 语速调节逻辑 ---
speed_options = {
    "极慢 (-50%)": "-50%",
    "略慢 (-20%)": "-20%",
    "标准速度": "+0%",
    "略快 (+15%)": "+15%",
    "极快 (+30%)": "+30%"
}

# 这里的 select_slider 会自动应用上面的 CSS 变色
speed_label = st.select_slider(
    "调节语速 (PTE 练习建议选择标准或略快)", 
    options=list(speed_options.keys()), 
    value="标准速度"
)
current_speed = speed_options[speed_label]

# --- 4. 生成区域 (英语用 Google, 法语用微软) ---
col1, col2 = st.columns(2)

with col1:
    if st.button("生成英文 (EN)", use_container_width=True):
        if text_input:
            with st.spinner('Google 合成中...'):
                audio_fp = asyncio.run(generate_google_audio(text_input, EN_VOICE, current_speed))
                if audio_fp:
                    audio_bytes = audio_fp.getvalue()
                    b64 = base64.b64encode(audio_bytes).decode()
                    st.markdown(f'<audio controls style="width: 100%; margin-top:10px;"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
                    st.download_button("📥 下载 MP3", data=audio_bytes, file_name="PTE_EN_Google.mp3")

with col2:
    if st.button("生成法语 (FR)", use_container_width=True):
        if text_input:
            with st.spinner('微软合成中...'):
                FR_VOICE = "fr-FR-VivienneNeural"
                audio_fp = asyncio.run(generate_microsoft_audio(text_input, FR_VOICE, current_speed))
                if audio_fp:
                    audio_bytes = audio_fp.getvalue()
                    b64 = base64.b64encode(audio_bytes).decode()
                    st.markdown(f'<audio controls style="width: 100%; margin-top:10px;"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
                    st.download_button("📥 下载 MP3", data=audio_bytes, file_name="PTE_FR_MS.mp3")

# --- 5. 右下角悬浮个人信息 ---
avatar_b64 = get_base64_of_bin_file('avatar.png')
footer_html = f"""
    <div style="position: fixed; bottom: 70px; right: 20px; background: rgba(255, 255, 255, 0.95); 
                border-radius: 15px; padding: 12px 18px; display: flex; align-items: center; gap: 12px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.2); z-index: 9999;">
        {f'<img src="data:image/png;base64,{avatar_b64}" style="width:45px; height:45px; border-radius:50%; border:2px solid #333;">' if avatar_b64 else "👤"}
        <div style="display: flex; flex-direction: column;">
            <p style="margin:0; font-size:14px; font-weight:700; color:#333;">Serena Shuo YANG</p>
            <p style="margin:0; font-size:11px; color:#666;">📧 Rocco.yang@gmail.com</p>
        </div>
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
