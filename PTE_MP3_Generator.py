import streamlit as st
from gtts import gTTS
import io

# 页面配置
st.set_page_config(page_title="PTE MP3 Generator", page_icon="🎙️")

st.title("🎙️ PTE MP3 Generator")
st.write("输入文本，一键生成英文或法文音频。")

# 文本输入框
text_input = st.text_area("请输入你想要转换的文本：", placeholder="Type your text here...")

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

            