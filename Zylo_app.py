import streamlit as st
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="🤖", layout="centered")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
[data-testid="stSidebar"] { background: #f8fafc; border-right: 1px solid #e2e8f0; }
div[data-testid="stChatMessage"] {
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
}
h1 { font-weight: 750; letter-spacing: -0.5px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🤖 Zylo")
    st.caption("Chat and create images")
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("Zylo")
st.caption("Ask anything, or type `/image` to create a picture.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
        if message["type"] == "image":
            st.image(message["content"], caption=message["caption"])
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Message Zylo..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "type": "text"}
    )
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
            {
                "role": "assistant",
                "content": image_url,
                "caption": image_prompt,
                "type": "image",
            }
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
