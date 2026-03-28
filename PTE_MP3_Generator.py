import streamlit as st
from gtts import gTTS
import io

# 页面配置
st.set_page_config(page_title="PTE MP3 Generator", page_icon="🎙️")

st.title("🎙️ PTE MP3 Generator")
st.write("输入文本，一键生成英文或法文音频。")

# 文本输入框
text_input = st.text_area("请输入你想要转换的文本：", placeholder="Type your text here...")

# --- 侧边栏底部个人信息 ---
# 尝试读取头像
bin_str = get_base64_of_bin_file('avatar.png')

if bin_str:
    st.sidebar.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px;">
            <img src="data:image/png;base64,{bin_str}" style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #1F6859; object-fit: cover;">
            <div>
                <p style="margin:0; font-size: 13px; font-weight: bold; color: #1F6859;">Serena Shuo YANG</p>
                <p style="margin:0; font-size: 11px; color: #666;">Shuoyang5@Carleton</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # 如果图片 avatar.png 不存在，则显示备用文字版
    st.sidebar.write("👤 **Serena S YANG**")
    st.sidebar.caption("Shuoyang5@Carleton")

# 添加一个语速开关
slow_mode = st.checkbox("慢速模式 (Slow Mode)")

def generate_audio(text, lang):
    # ... 省略部分代码
    tts = gTTS(text=text, lang=lang, slow=slow_mode) # slow=True 会变慢
    # ...

# 定义生成函数
def generate_audio(text, lang,slow): #增加slow参数
    if not text.strip():
        st.error("请输入一些内容后再点击生成！")
        return None
    
    try:
        # 使用 gTTS 生成语音流
        tts = gTTS(text=text, lang=lang,slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception as e:
        st.error(f"生成失败: {e}")
        return None

# 按钮布局
col1, col2 = st.columns(2)

with col1:
    if st.button("生成英文 (EN)"):
        audio_data = generate_audio(text_input, 'en')
        if audio_data:
            st.audio(audio_data, format="audio/mp3")
            st.download_button("下载英文 MP3", data=audio_data.getvalue(), file_name="english_audio.mp3", mime="audio/mp3")

with col2:
    if st.button("生成法语 (FR)"):
        audio_data = generate_audio(text_input, 'fr')
        if audio_data:
            st.audio(audio_data, format="audio/mp3")
            st.download_button("下载法语 MP3", data=audio_data.getvalue(), file_name="french_audio.mp3", mime="audio/mp3")

            