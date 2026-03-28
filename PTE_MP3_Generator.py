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
    /* 全局背景 */
    .main { background-color: #0E1117; }
    
    /* 输入框：22px 大字号，黑底白字 */
    .stTextArea textarea { 
        font-size: 22px !important; 
        line-height: 1.6 !important; 
        color: #FFFFFF !important;
        background-color: #1E1E1E !important;
        border: 1px solid #444 !important;
        border-radius: 12px !important;
    }

    /* 标签文字字号与颜色 */
    [data-testid="stWidgetLabel"] p {
        font-size: 20px !important;
        color: #E0E0E0 !important;
        font-weight: bold !important;
    }

    /* 按钮：纯黑背景，银色边框 */
    .stButton button { 
        font-size: 18px !important;
        height: 3.5em !important;
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        border: 1px solid #555 !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }
    .stButton button:hover {
        border-color: #FFFFFF !important;
        background-color: #111111 !important;
    }

    /* 彻底去红 */
    :root { --primary-color: #C0C0C0 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ PTE Pro MP3 Generator")
st.caption("英语: Google Engine | 法语: Microsoft Azure")

# --- 3. 输入区域 ---
text_input = st.text_area("请输入练习文本：", placeholder="在此输入内容...", height=300)

# --- 4. 生成区域 (英语用 Google, 法语用微软) ---
col1, col2 = st.columns(2)

with col1:
    if st.button("生成英文 (EN)", use_container_width=True):
        if text_input:
            with st.spinner('Google 合成中...'):
                audio_fp = generate_google_audio(text_input, lang='en')
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
                audio_fp = asyncio.run(generate_microsoft_audio(text_input, FR_VOICE))
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
