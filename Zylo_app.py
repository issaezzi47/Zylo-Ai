import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="◆", layout="centered")

st.markdown("""
<style>
.stApp {
  background:
    radial-gradient(900px 500px at 15% -10%, rgba(99, 102, 241, .18), transparent 60%),
    radial-gradient(800px 500px at 90% 0%, rgba(236, 72, 153, .10), transparent 55%),
    #070a13;
  color: #e7eaf3 !important;
}
.block-container {
  padding-top: 1.6rem;
  max-width: 760px;
  padding-bottom: 7rem;
}
[data-testid="stSidebar"] {
  background: #0b0f1a;
  border-right: 1px solid #1b2233;
}
[data-testid="stSidebar"] * { color: #dfe4f2 !important; }
h1, h2, h3, p, span, label { color: #e7eaf3 !important; }

.zylo-brand {
  display: flex;
  align-items: center;
  gap: .8rem;
  margin-bottom: 1.6rem;
}
.zylo-mark {
  width: 46px;
  height: 46px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.35rem;
  color: white;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  box-shadow: 0 8px 26px rgba(99, 102, 241, .35);
}
.zylo-title {
  font-size: 1.35rem;
  font-weight: 750;
  margin: 0;
}
.zylo-sub {
  color: #8b93a7;
  font-size: .82rem;
  margin: 0;
}

.zylo-hero {
  text-align: center;
  margin: 2.2rem 0 2.4rem;
}
.zylo-hero h1 {
  font-size: 2.5rem;
  font-weight: 750;
  margin: 0;
}
.zylo-hero p {
  color: #98a0b3;
  margin-top: .5rem;
}

div[data-testid="stChatInput"] {
  background: rgba(19, 24, 38, .92) !important;
  border: 1px solid #232b40 !important;
  border-radius: 24px !important;
  backdrop-filter: blur(12px);
}
div[data-testid="stChatInput"] textarea {
  color: #e7eaf3 !important;
}

div[data-testid="stChatMessage"] {
  background: rgba(18, 23, 38, .78) !important;
  border: 1px solid #212a3f !important;
  border-radius: 20px !important;
  padding: .95rem 1.05rem !important;
  backdrop-filter: blur(10px);
}
div[data-testid="stChatMessage"] * { color: #e7eaf3 !important; }

.stButton > button {
  width: 100%;
  border-radius: 16px;
  background: rgba(19, 24, 38, .85);
  border: 1px solid #232b40;
  color: #e7eaf3 !important;
  padding: .75rem .9rem;
}
.stButton > button:hover {
  border-color: #6366f1;
  box-shadow: 0 0 18px rgba(99, 102, 241, .22);
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="zylo-brand">
      <div class="zylo-mark">Z</div>
      <div>
        <p class="zylo-title">Zylo</p>
        <p class="zylo-sub">AI assistant</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Chat • Voice • Images")

if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="zylo-hero">
      <h1>Hello.</h1>
      <p>I’m Zylo. Ask me anything, speak to me, or create an image.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✍️ Write for me"):
            st.session_state.suggestion = "Write a short, friendly message for my friend."
            st.rerun()
    with col2:
        if st.button("🎨 Create an image"):
            st.session_state.suggestion = "/image a futuristic city at sunset, cinematic"
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("🧠 Explain simply"):
            st.session_state.suggestion = "Explain black holes in simple words."
            st.rerun()
    with col4:
        if st.button("💡 Give me an idea"):
            st.session_state.suggestion = "Give me a creative weekend project idea."
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "Z"):
        if message["type"] == "image":
            st.image(message["content"], caption=message["caption"])
        else:
            st.markdown(message["content"])

def speak(text):
    safe = text.replace(chr(34), chr(39))
    safe = safe.replace(chr(10), chr(32))
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
                    "You are Zylo, a polished, friendly, concise AI assistant. "
                    "Use clear formatting when helpful. "
                    "For images, tell the user to type /image followed by a description."
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

    prompt = ""

    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=voice,
        )
        prompt = transcription.text
    except Exception as e:
        st.error("Could not understand the voice message: " + str(e))

    if prompt:
        label = "🎙️ " + prompt
        st.session_state.messages.append(
            {"role": "user", "content": label, "type": "text"}
        )
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(label)

        with st.chat_message("assistant", avatar="Z"):
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
            if st.button("🔊 Speak reply", key="voice-" + str(len(st.session_state.mess
