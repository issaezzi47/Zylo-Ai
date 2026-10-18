import streamlit as st
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="🤖")
st.title("🤖 Zylo")
st.caption("Your private AI assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Ask Zylo anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are Zylo, a helpful, friendly AI assistant."},
                *st.session_state.messages,
            ],
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Sorry, I had trouble connecting: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
