import streamlit as st
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="◆")

st.sidebar.title("Zylo")
if st.sidebar.button("New chat"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_groq(messages):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages
    )
    return response.choices[0].message.content

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["type"] == "image":
            st.image(m["url"], caption=m["text"])
        else:
            st.markdown(m["text"])
            voice = st.audio_input("🎙️ Voice message")

if voice:
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=voice
        ).text
    except Exception as e:
        st.error("Voice error: " + str(e))
        prompt = ""

    if prompt:
        st.session_state.messages.append({"role": "user", "text": "🎙️ " + prompt, "type": "text"})
        st.rerun()

prompt = st.chat_input("Ask Zylo anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "text": prompt, "type": "text"})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last = st.session_state.messages[-1]["text"]

    if last.startswith("🎙️ "):
        question = last[3:]
    elif last.startswith("/image "):
        question = last[7:]
    else:
        question = last

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if last.startswith("/image "):
                image_url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(question) + "?width=768&height=768&nologo=true"
                st.image(image_url, caption=question)
                st.session_state.messages.append({"role": "assistant", "text": question, "url": image_url, "type": "image"})
            else:
                history = [{"role": m["role"], "content": m["text"]} for m in st.session_state.messages if m["type"] == "text"]
                try:
                    answer = ask_groq(history)
                except Exception as e:
                    answer = "Connection issue: " + str(e)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "text": answer, "type": "text"})
