import streamlit as st
from pathlib import Path

from rag_function import rag_answer, CHAT_MODEL, EMBED_MODEL, CHROMA_DIR


# Streamlit UI
IMG_PATH = Path(__file__).resolve().parent / "Eye-of-Sauron.jpeg"
st.sidebar.image(IMG_PATH, use_container_width=True)
st.set_page_config(page_title="Lord of the RAGs", page_icon="🧙🏼‍♂️")
st.title("🧙🏼‍♂️Lord of the Rings Chatbot")

with st.sidebar:
    st.markdown("### Settings")
    k = st.slider("Retrieved chunks (k)", min_value=1, max_value=10, value=4)
    st.caption(f"Chat model: {CHAT_MODEL}")
    st.caption(f"Embed model: {EMBED_MODEL}")
    st.caption(f"DB folder: {CHROMA_DIR}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

question = st.chat_input("Ask something…")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        out = rag_answer(question, k=k)
        st.markdown(out["answer"])

        if out.get("sources"):
            with st.expander("Sources"):
                for src, page in out["sources"]:
                    st.write(f"- {src} — page {page}")

    st.session_state.messages.append({"role": "assistant", "content": out["answer"]})