import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Zylo AI",
    page_icon="✨",
    layout="centered",
)

st.markdown("""
<style>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 12px rgba(139, 92, 246, .35); }
  50% { box-shadow: 0 0 28px rgba(139, 92, 246, .75); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-7px); }
}

.main { background: radial-gradient(circle at top, #151b2b, #0b0f19 70%); }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #101527, #0b0f19);
  border-right: 1px solid #1f2937;
}

.zylo-hero {
  text-align: center;
  animation: fadeUp .8s ease both;
  margin-top: 1rem;
}

.zylo-logo {
  display: inline-block;
  font-size: 3rem;
  animation: float 3s ease-in-out infinite, glow 2.5s ease-in-out infinite;
  border-radius: 50%;
  padding: .5rem;
}

.zylo-title {
  font-size: 2.4rem;
  font-weight: 800;
  color: #f9fafb;
  margin: .2rem 0 0;
}

.zylo-sub {
  color: #9ca3af;
  font-size: 1.05rem;
}

div[data-testid="stChatMessage"] {
  background: rgba(17, 24, 39, .85);
  border: 1px solid #1f2937;
  border-radius: 20px;
  padding: 1rem;
  animation: fadeUp .45s ease both;
}

.stButton > button {
  width: 100%;
  border-radius: 14px;
  background: #111827;
  border: 1px solid #374151;
  color: #e5e7eb;
  transition: all .2s ease;
}

.stButton > button:hover {
  border-color: #8b5cf6;
  box-shadow: 0 0 18px rgba(139, 92, 246, .45);
  transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ✨ Zylo")
    st.caption("Your personal AI assistant")
    if st.button("＋ New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Powered by Groq")

st.markdown("""
<div class="zylo-hero">
  <div class="zylo-logo">✨</div>
  <p class="zylo-title">Hello, I’m Zylo</p>
  <p class="zylo-sub">Ask me anything—ideas, writing, explanations, or planning.</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "✨"):
        st.markdown(message["content"])

if prompt := st.chat_input("Message Zylo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Zylo is thinking..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Zylo, a warm, intelligent, concise AI assistant. "
                                "Use clear formatting and helpful examples when useful."
                            ),
                        },
                        *st.session_state.messages,
                    ],
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"⚠️ I couldn’t connect to Zylo’s brain: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="✨"):
        st.markdown(reply)
