import streamlit as st
import asyncio
import edge_tts
import io
import base64
import os

# --- 1. 核心工具函数定义 ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except: return None
    return None

# 改为异步生成函数，调用微软 Edge 引擎
async def generate_microsoft_audio(text, voice):
    if not text.strip():
        return None
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return io.BytesIO(audio_data)
    except Exception as e:
        st.error(f"微软语音生成失败: {e}")
        return None

# --- 2. 页面配置 ---
st.set_page_config(page_title="PTE Pro Generator", page_icon="🎙️")

st.title("🎙️ PTE Pro MP3 Generator")
st.caption("Powered by Microsoft Azure Neural TTS (Edge Version)")

# --- 3. 主界面交互 ---
text_input = st.text_area("请输入练习文本：", placeholder="Paste your PTE text here...", height=200)

# 语速调节 (Edge-TTS 支持更精细的语速控制，例如 +0%, -20%)
speed = st.select_slider("选择语速调节", options=["-25%", "-10%", "Default", "+10%", "+25%"], value="Default")
speed_str = "0%" if speed == "Default" else speed

# 按钮布局
col1, col2 = st.columns(2)

# 英文配置 (这里选了微软最自然的两个声音)
EN_VOICE = "en-US-AvaNeural" # 也可以换成 en-AU-NatashaNeural (澳洲口音)
FR_VOICE = "fr-FR-VivienneNeural"

with col1:
    if st.button("生成微软英文 (Ava)", use_container_width=True):
        # 运行异步任务
        audio_fp = asyncio.run(generate_microsoft_audio(text_input, EN_VOICE))
        if audio_fp:
            audio_bytes = audio_fp.getvalue()
            b64 = base64.b64encode(audio_bytes).decode()
            st.markdown(f'<audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
            st.download_button("📥 下载高质量 EN", data=audio_bytes, file_name="en_pro.mp3")

with col2:
    if st.button("生成微软法语 (Vivienne)", use_container_width=True):
        audio_fp = asyncio.run(generate_microsoft_audio(text_input, FR_VOICE))
        if audio_fp:
            audio_bytes = audio_fp.getvalue()
            b64 = base64.b64encode(audio_bytes).decode()
            st.markdown(f'<audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
            st.download_button("📥 下载高质量 FR", data=audio_bytes, file_name="fr_pro.mp3")

# --- 4. 右下角悬浮个人信息 (修正版：Serena & Rocco) ---

# 读取头像 (确保 avatar.png 在根目录)
bin_str = get_base64_of_bin_file('avatar.png')

# 核心 HTML 结构
contact_html = f"""
    <style>
    /* 定义悬浮窗的容器 */
    .footer {{
        position: fixed;
        bottom: 60px; /* 避开 Manage app 条 */
        right: 15px;
        width: auto;
        background-color: rgba(255, 255, 255, 0.95); /* 半透明白色背景 */
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); /* 淡淡的阴影 */
        z-index: 1000; /* 确保悬浮在最上层 */
        transition: transform 0.3s ease; /* 丝滑过渡 */
    }}
    
    /* 悬停效果 (增加互动感) */
    .footer:hover {{
        transform: translateY(-3px); /* 向上飘一点 */
        background-color: rgba(255, 255, 255, 1); /* 变为不透明 */
    }}
    
    /* 头像样式 */
    .avatar {{
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 2px solid #1F6859;
        object-fit: cover;
    }}
    
    /* 文本容器 */
    .info-text {{
        display: flex;
        flex-direction: column;
        line-height: 1.3;
    }}
    
    /* 姓名样式 */
    .name {{
        margin: 0 !important;
        font-size: 14px;
        font-weight: bold;
        color: #1F6859;
    }}
    
    /* 邮箱/联系方式样式 */
    .school {{
        margin: 0 !important;
        font-size: 11px;
        color: #666;
    }}
    </style>
    
    <div class="footer">
        {f'<img src="data:image/png;base64,{bin_str}" class="avatar">' if bin_str else "👤"}
        <div class="info-text">
            <p class="name">Serena Shuo YANG</p>
            <p class="school">📧 Rocco.yang@gmail.com</p>
        </div>
    </div>
"""

# 将 HTML 注入页面
st.markdown(contact_html, unsafe_allow_html=True)