import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
from groq import Groq

st.set_page_config(page_title="Zylo", page_icon="◆", layout="centered")
st.markdown("<style>.stApp{background:#070a13;color:#e7eaf3!important}.block-container{padding-bottom:7rem}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("Zylo")
    if st.button("New chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑‍💻" if m["role"] == "user" else "Z"):
        if m["type"] == "image":
            st.image(m["content"], caption=m["caption"])
        else:
            st.markdown(m["content"])

def speak(text):
    safe = text.replace(chr(34), chr(39)).replace(chr(10), chr(32))
    js = "const u=new SpeechSynthesisUtterance(" + repr(safe) + ");u.rate=1;window.speechSynthesis.speak(u);"
    components.html("<script>" + js + "</script>", height=0)

def reply(prompt, history):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    r = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":"You are Zylo, a friendly concise AI assistant."}, *history])
    return r.choices[0].message.content

voice = st.audio_input("🎙️ Voice message")
if voice:
    prompt = ""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = client.audio.transcriptions.create(model="whisper-large-v3", file=voice).text
    except Exception as e:
        st.error("Voice error: " + str(e))
    if prompt:
        st.session_state.messages.append({"role":"user","content":"🎙️ "+prompt,"type":"text"})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown("🎙️ "+prompt)
        with st.chat_message("assistant", avatar="Z"):
            with st.spinner("Thinking..."):
                try:
                    history=[{"role":m["role"],"content":m["content"]} for m in st.session_state.messages if m["type"]=="text"]
                    answer=reply(prompt,history)
                except Exception as e:
                    answer="Connection issue: "+str(e)
            st.markdown(answer)
            if st.button("🔊 Speak", key="v"+str(len(st.session_state.messages))):
                speak(answer)
        st.session_state.messages.append({"role":"assistant","content":answer,"type":"text"})

if prompt := st.chat_input("Ask Zylo anything..."):
    st.session_state.messages.append({"role":"user","content":prompt,"type":"text"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    if prompt.lower().startswith("/image "):
        desc=prompt[7:].strip()
        url="https://image.pollinations.ai/prompt/"+urllib.parse.quote(desc)+"?width=768&height=768&nologo=true"
        with st.chat_message("assistant", avatar="Z"):
            with st.spinner("Creating image..."):
                st.image(url, caption=desc)
        st.session_state.messages.append({"role":"assistant","content":url,"caption":desc,"type":"image"})
    else:
        with st.chat_message("assistant", avatar="Z"):
            with st.spinner("Thinking..."):
                try:
                    history=[{"role":m["role"],"content":m["content"]} for m in st.session_state.messages if m["type"]=="text"]
                    answer=reply(prompt,history)
                except Exception as e:
                    answer="Connection issue: "+str(e)
            st.markdown(answer)
            if st.button("🔊 Speak", key="t"+str(len(st.session_state.messages))):
                speak(answer)
        st.session_state.messages.append({"role":"assistant","content":answer,"type":"text"})
