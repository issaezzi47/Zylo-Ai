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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["url"], caption=message["text"])
        else:
            st.markdown(message["text"])
            prompt = st.chat_input("Ask Zylo anything...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "text": prompt,
        "type": "text"
    })
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_message = st.session_state.messages[-1]["text"]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if last_message.startswith("/image "):
                image_prompt = last_message[7:].strip()
                image_url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(image_prompt) + "?width=768&height=768&nologo=true"

                st.image(image_url, caption=image_prompt)

                st.session_state.messages.append({
                    "role": "assistant",
                    "text": image_prompt,
                    "url": image_url,
                    "type": "image"
                })

            else:
                history = []

                for message in st.session_state.messages:
                    if message["type"] == "text":
                        history.append({
                            "role": message["role"],
                            "content": message["text"]
                        })

                try:
                    answer = ask_groq(history)
                except Exception as error:
                    answer = "Connection issue: " + str(error)

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "text": answer,
                    "type": "text"
                })
