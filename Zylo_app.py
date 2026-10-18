import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="◆", layout="centered")

st.markdown("""
<style>
.stApp { background: #070a13; color: #e7eaf3 !important; }
.block-container { padding-bottom: 7rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Zylo")
    if st.button("New chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑‍💻" if m["role"] == "user" else "🤖"):
        if m["type"] == "image":
            st.image(m["content"], caption=m["caption"])
        else:
            st.markdown(m["content"])

def speak(text):
    safe = text.replace('"', "'").replace("
", " ")
    js = 'const u=new SpeechSynthesisUtterance("' + safe + '");u.rate=1;window.speechSynthesis.speak(u);'
    components.html("<script>" + js + "</script>", height=0)

def reply(prompt, history):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are Zylo, a friendly concise AI assistant."},
            *history
        ]
    )
    return response.choices[0].message.content
    voice = st.audio_input("🎙️ Voice message")

if voice:
    prompt = ""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=voice
        ).text
    except Exception as e:
        st.error("Voice error: " + str(e))

    if prompt:
        st.session_state.messages.append({"role": "user", "content": "🎙️ " + prompt, "type": "text"})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown("🎙️ " + prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                    if m["type"] == "text"
                ]
                try:
                    answer = reply(prompt, history)
                except Exception as e:
                    answer = "Connection issue: " + str(e)
            st.markdown(answer)
            if st.button("🔊 Speak", key="voice_speak"):
                speak(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer, "type": "text"})
        prompt = st.chat_input("Ask Zylo anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    if prompt.lower().startswith("/image "):
        image_prompt = prompt[7:].strip()
        image_url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(image_prompt) + "?width=768&height=768&nologo=true"

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Creating image..."):
                st.image(image_url, caption=image_prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": image_url,
            "caption": image_prompt,
            "type": "image"
        })

    else:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                    if m["type"] == "text"
                ]
                try:
                    answer = reply(prompt, history)
                except Exception as e:
                    answer = "Connection issue: " + str(e)
            st.markdown(answer)
            if st.button("🔊 Speak", key="text_speak"):
                speak(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer, "type": "text"})
