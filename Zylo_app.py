import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="💬", layout="centered")

st.markdown("""
<style>
.stApp {
  background: #0b141a;
  color: #e9edef !important;
}
.block-container {
  padding-top: .8rem;
  max-width: 760px;
  padding-bottom: 5rem;
}
[data-testid="stSidebar"] {
  background: #111b21;
  border-right: 1px solid #222d34;
}
[data-testid="stSidebar"] * { color: #e9edef !important; }
h1, h2, h3, p, span, label { color: #e9edef !important; }

.zylo-header {
  display: flex;
  align-items: center;
  gap: .75rem;
  background: #202c33;
  padding: .7rem 1rem;
  border-radius: 14px;
  border: 1px solid #2a3942;
  margin-bottom: 1rem;
}
.zylo-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #00a884;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
}
.zylo-name { font-weight: 700; margin: 0; }
.zylo-status { color: #8696a0; font-size: .78rem; margin: 0; }

div[data-testid="stChatMessage"] {
  background: #005c4b !important;
  border: none !important;
  border-radius: 16px !important;
  padding: .7rem .95rem !important;
  max-width: 85%;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: #202c33 !important;
  margin-left: auto !important;
}
div[data-testid="stChatMessage"] * { color: #e9edef !important; }

div[data-testid="stChatInput"] textarea {
  background: #2a3942 !important;
  color: #e9edef !important;
  border-radius: 12px !important;
}

.stButton > button {
  width: 100%;
  border-radius: 12px;
  background: #202c33;
  border: 1px solid #2a3942;
  color: #e9edef !important;
}
.stButton > button:hover {
  border-color: #00a884;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("💬 Zylo")
    st.caption("Chat • Voice • Images • Videos")
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Type /image or /video")

st.markdown("""
<div class="zylo-header">
  <div class="zylo-avatar">🤖</div>
  <div>
    <p class="zylo-name">Zylo</p>
    <p class="zylo-status">online • AI assistant</p>
  </div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
        if message["type"] == "image":
            st.image(message["content"], caption=message["caption"])
        elif message["type"] == "video":
            st.video(message["content"])
        else:
            st.markdown(message["content"])

def speak(text):
    safe = text.replace('"', "'")
    safe = safe.replace("
", " ")
    js = "const u = new SpeechSynthesisUtterance(" + repr(safe) + ");"
    js += "u.rate = 1;"
    js += "window.speechSynthesis.speak(u);"
    components.html("<script>" + js + "</script>", height=0)

def zylo_reply(prompt, history):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Zylo, a friendly, concise AI assistant in a WhatsApp-style chat. "
                    "For images, tell the user to type /image plus a description. "
                    "For videos, tell them to type /video plus a description."
                ),
            },
            *history,
        ],
    )
    return response.choices[0].message.content

voice = st.audio_input("🎙️ Voice message")

if voice:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.audio(voice)

    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=voice,
        )
        prompt = transcription.text
    except Exception as e:
        prompt = ""
        st.error(f"Could not understand the voice message: {e}")

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": "🎙️ " + prompt, "type": "text"}
        )
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown("🎙️ " + prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Zylo is thinking..."):
                try:
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                        if m["type"] == "text"
                    ]
                    reply = zylo_reply(prompt, history)
                except Exception as e:
                    reply = "⚠️ Connection issue: " + str(e)

            st.markdown(reply)
            if st.button("🔊 Play reply", key="voice-play-" + str(len(st.session_state.messages))):
                speak(reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "type": "text"}
        )

if prompt := st.chat_input("Message Zylo..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    command = prompt.lower()

    if command.startswith("/image "):
        description = prompt[7:].strip()
        encoded = urllib.parse.quote(description)
        url = "https://image.pollinations.ai/prompt/" + encoded + "?width=768&height=768&nologo=true"

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Creating image..."):
                st.image(url, caption=description)

        st.session_state.messages.append(
            {"role": "assistant", "content": url, "caption": description, "type": "image"}
        )

    elif command.startswith("/video "):
        description = prompt[7:].strip()
        encoded = urllib.parse.quote(description)
        url = (
            "https://gen.pollinations.ai/video/"
            + encoded
            + "?model=wan-fast&duration=8&aspectRatio=9:16&width=720&height=1280"
        )

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Creating an 8-second video. This may take several minutes..."):
                st.video(url)

        st.session_state.messages.append(
            {"role": "assistant", "content": url, "type": "video"}
        )

    else:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Zylo is thinking..."):
                try:
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                        if m["type"] == "text"
                    ]
                    reply = zylo_reply(prompt, history)
                except Exception as e:
                    reply = "⚠️ Connection issue: " + str(e)

            st.markdown(reply)
            if st.button("🔊 Play reply", key="text-play-" + str(len(st.session_state.messages))):
                speak(reply)

        st.session_state.messages.append(
            {"ro
