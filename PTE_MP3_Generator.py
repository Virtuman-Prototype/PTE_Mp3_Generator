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
        # rate 参数格式为 "+0%", "+25%", "-10%" 等
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
st.set_page_config(page_title="PTE Pro Generator", page_icon="🎙️")

# 注入 CSS：专门适配深色背景的黑底银白风格
st.markdown("""
    <style>
    /* 1. 彻底封杀红色滑块轨道 -> 换成银灰色 */
    [data-testid="stSlider"] [data-baseweb="slider"] div div {
        background-image: none !important;
        background-color: #444444 !important; /* 轨道未选中部分：深灰 */
    }
    
    /* 滑块左侧（已选中部分）的颜色 -> 亮银色 */
    [data-testid="stSlider"] div[role="none"] > div > div:first-child > div {
        background: #C0C0C0 !important; 
    }

    /* 滑块圆点 -> 纯白配合黑色边框 */
    [data-testid="stSlider"] div[role="slider"] {
        background-color: #FFFFFF !important; 
        border: 2px solid #C0C0C0 !important;
        box-shadow: 0 0 8px rgba(255,255,255,0.2) !important;
    }

    /* 2. 把所有标签文字（“极慢”、“标准”）改为亮银白色，确保黑底看得清 */
    [data-testid="stSliderTickBar"] div,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stSliderWidget"] label p,
    [data-testid="stMarkdownContainer"] p,
    span[data-baseweb="tag"] {
        color: #E0E0E0 !important; 
        font-weight: 500 !important;
    }
    
    /* 彻底隐藏那个顽固的红色刻度点 */
    [data-testid="stTickBar"] {
        display: none !important;
    }

    /* 3. 输入框：深色背景，银色边框 */
    .stTextArea textarea { 
        font-size: 16px !important; 
        border-radius: 8px !important; 
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #444 !important;
    }

    /* 4. 按钮：纯黑背景，银色文字 */
    .stButton button { 
        height: 3.2em; 
        border-radius: 8px; 
        background-color: #000000 !important; 
        color: #E0E0E0 !important;
        border: 1px solid #555 !important;
    }
    .stButton button:hover {
        border-color: #FFFFFF !important;
        color: #FFFFFF !important;
        background-color: #111111 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ PTE Pro MP3 Generator")
st.caption("基于微软 Azure Neural TTS 技术 | 高保真真人语调")

# --- 3. 用户输入区域 ---
text_input = st.text_area(
    "请输入练习文本：", 
    placeholder="在此粘贴 PTE 阅读或口语文本...", 
    height=250
)

# 语速调节逻辑：将滑块选项转换为 edge-tts 识别的百分比字符串
speed_options = {
    "极慢 (-50%)": "-50%",
    "略慢 (-20%)": "-20%",
    "标准速度": "+0%",
    "略快 (+15%)": "+15%",
    "极快 (+30%)": "+30%"
}
speed_label = st.select_slider("调节语速 (PTE 练习建议选择标准或略快)", options=list(speed_options.keys()), value="标准速度")
current_speed = speed_options[speed_label]

# --- 4. 生成与播放区域 ---
col1, col2 = st.columns(2)

# 配置微软最自然的配音角色
EN_VOICE = "en-US-AvaNeural"   # 极自然的美国女声
FR_VOICE = "fr-FR-VivienneNeural" # 优雅的法国女声

with col1:
    if st.button("生成英文 (EN)", use_container_width=True):
        if text_input:
            with st.spinner('正在合成美音...'):
                audio_fp = asyncio.run(generate_microsoft_audio(text_input, EN_VOICE, current_speed))
                if audio_fp:
                    audio_bytes = audio_fp.getvalue()
                    b64 = base64.b64encode(audio_bytes).decode()
                    # HTML5 播放器解决手机 Error 问题
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

# --- 5. 右下角个人信息悬浮窗 ---
avatar_b64 = get_base64_of_bin_file('avatar.png')
footer_html = f"""
    <style>
    .custom-footer {{
        position: fixed;
        bottom: 70px;
        right: 20px;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #ddd;
        border-radius: 15px;
        padding: 12px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        z-index: 9999;
        transition: all 0.3s ease;
    }}
    .custom-footer:hover {{
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }}
    .footer-avatar {{
        width: 45px;
        height: 45px;
        border-radius: 50%;
        border: 2px solid #1F6859;
        object-fit: cover;
    }}
    .footer-info {{
        display: flex;
        flex-direction: column;
    }}
    .footer-name {{
        margin: 0;
        font-size: 14px;
        font-weight: 700;
        color: #1F6859;
    }}
    .footer-email {{
        margin: 0;
        font-size: 11px;
        color: #777;
    }}
    </style>
    <div class="custom-footer">
        {f'<img src="data:image/png;base64,{avatar_b64}" class="footer-avatar">' if avatar_b64 else "👤"}
        <div class="footer-info">
            <p class="footer-name">Serena Shuo YANG</p>
            <p class="footer-email">📧 Rocco.yang@gmail.com</p>
        </div>
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)