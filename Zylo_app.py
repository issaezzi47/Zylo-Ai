import streamlit as st
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="🤖", layout="centered")

st.markdown("""
<style>
@keyframes waveMove {
  0% { background-position: 0 0; }
  100% { background-position: 1200px 0; }
}

.block-container {
  padding-top: 1.2rem;
  max-width: 850px;
}

.stApp {
  background:
    linear-gradient(180deg, rgba(0,0,0,.88), rgba(0,0,0,.96)),
    repeating-linear-gradient(
      90deg,
      rgba(0, 90, 255, .16) 0px,
      rgba(0, 170, 255, .07) 120px,
      rgba(0, 40, 120, .16) 240px
    );
  background-size: auto, 1200px 100%;
  animation: waveMove 18s linear infinite;
  color: #e5e7eb !important;
}

[data-testid="stSidebar"] {
  background: rgba(5, 10, 20, .92);
  border-right: 1px solid #12233f;
  color: #e5e7eb !important;
}

[data-testid="stSidebar"] * {
  color: #e5e7eb !important;
}

h1, h2, h3, p, span, label {
  color: #e5e7eb !important;
}

div[data-testid="stChatMessage"] {
  background: #0b1220 !important;
  border: 1px solid #17335c !important;
  border-radius: 18px !important;
  color: #e5e7eb !important;
}

div[data-testid="stChatMessage"] * {
  color: #e5e7eb !important;
}

div[data-testid="stChatInput"] textarea {
  color: #e5e7eb !important;
  background: #0b1220 !important;
}

.stButton > button {
  width: 100%;
  border-radius: 12px;
  background: #0b1220;
  border: 1px solid #17335c;
  color: #e5e7eb !important;
}

.stButton > button:hover {
  border-color: #38bdf8;
  box-shadow: 0 0 16px rgba(56, 189, 248, .35);
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🤖 Zylo")
    st.caption("Chat and create images")
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("Zylo")
st.caption("Ask anything, or type /image to create a picture.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
        if message["type"] == "image":
            st.image(message["content"], caption=message["caption"])
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Message Zylo..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    if prompt.lower().startswith("/image "):
        image_prompt = prompt[7:].strip()
        encoded = urllib.parse.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true"

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Creating your image..."):
                st.image(image_url, caption=image_prompt)

        st.session_state.messages.append(
            {"role": "assistant", "content": image_url, "caption": image_prompt, "type": "image"}
        )

    else:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Zylo is thinking..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are Zylo, a helpful, friendly, concise AI assistant. "
                                    "If the user wants an image, tell them to type /image followed by a description."
                                ),
                            },
                            *[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages
                                if m["type"] == "text"
                            ],
                        ],
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"⚠️ Connection issue: {e}"

            st.markdown(reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "type": "text"}
        )
