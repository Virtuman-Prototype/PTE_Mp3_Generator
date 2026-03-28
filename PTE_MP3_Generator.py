import streamlit as st
from gtts import gTTS
import io
import base64
import os

# --- 1. 核心工具函数定义 ---
def get_base64_of_bin_file(bin_file):
    """将本地图片转换为 base64 字符串，如果文件不存在则返回 None"""
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except Exception:
            return None # 读取失败也返回 None
    return None

def generate_audio(text, lang, slow):
    """生成语音流函数"""
    if not text.strip():
        st.error("请输入一些内容后再点击生成！")
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0) # <--- 重点：重置文件指针到开头
        return fp
    except Exception as e:
        st.error(f"生成失败: {e}")
        return None

# --- 2. 页面配置 ---
st.set_page_config(page_title="PTE/TCF MP3 Generator", page_icon="🎙️")

st.title("🎙️ PTE/TCF MP3 Generator")
st.write("输入文本，一键生成英文或法文音频。")

# --- 3. 主界面交互 ---
text_input = st.text_area("请输入你想要转换的文本：", placeholder="Type your text here...", height=200)

# 语速开关
slow_mode = st.checkbox("🐢 慢速模式 (Slow Mode) - 适合跟读练习")

# 按钮布局
col1, col2 = st.columns(2)

with col1:
    if st.button("生成英文 (EN)", use_container_width=True):
        audio_data = generate_audio(text_input, 'en', slow_mode)
        if audio_data:
            st.audio(audio_data.getvalue(), format="audio/mp3")
            st.download_button("下载英文 MP3", data=audio_data.getvalue(), file_name="english.mp3", mime="audio/mp3")

with col2:
    if st.button("生成法语 (FR)", use_container_width=True):
        audio_data = generate_audio(text_input, 'fr', slow_mode)
        if audio_data:
            st.audio(audio_data.getvalue(), format="audio/mp3")
            st.download_button("下载法语 MP3", data=audio_data.getvalue(), file_name="french.mp3", mime="audio/mp3")

# --- 4. 右下角悬浮个人信息 ---

# 读取头像 (确保 avatar.png 在 GitHub 仓库根目录)
bin_str = get_base64_of_bin_file('avatar.png')

if bin_str:
    # 方案 A：有头像时的 HTML
    contact_html = f"""
    <div class="footer">
        <img src="data:image/png;base64,{bin_str}" class="avatar">
        <div class="info-text">
            <p class="name">Serena Shuo YANG</p>
            <p class="school">Shuoyang5@Carleton</p>
        </div>
    </div>
    """
else:
    # 方案 B：没有头像时的备用 HTML
    contact_html = """
    <div class="footer">
        <div class="info-text">
            <p class="name">👤 Serena S YANG</p>
            <p class="school">Shuoyang5@Carleton</p>
        </div>
    </div>
    """

# 核心 CSS：关键在于 position: fixed; bottom: 10px; right: 10px;
st.markdown(
    f"""
    <style>
    /* 定义悬浮窗的容器 */
    .footer {{
        position: fixed;
        bottom: 10px;
        right: 10px;
        width: auto;
        background-color: rgba(255, 255, 255, 0.9); /* 半透明白色背景 */
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 8px 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); /* 淡淡的阴影 */
        z-index: 1000; /* 确保悬浮在最上层 */
    }}
    
    /* 头像样式 */
    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 2px solid #1F6859;
        object-fit: cover;
    }}
    
    /* 文本容器 */
    .info-text {{
        display: flex;
        flex-direction: column;
    }}
    
    /* 姓名样式 */
    .name {{
        margin: 0 !important;
        font-size: 13px;
        font-weight: bold;
        color: #1F6859;
        line-height: 1.2;
    }}
    
    /* 学校样式 */
    .school {{
        margin: 0 !important;
        font-size: 11px;
        color: #666;
        line-height: 1.2;
    }}
    </style>
    {contact_html}
    """,
    unsafe_allow_html=True
)
