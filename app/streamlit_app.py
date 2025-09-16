import os, requests, streamlit as st
API_URL = os.getenv("API_URL", "http://localhost:8000")

msg = st.chat_input("Start a case…")
if msg:
    hist = st.session_state.get("history", [])
    hist.append({"role":"user","content":msg})
    r = requests.post(f"{API_URL}/chat", json={"messages": hist, "max_tokens": 300})
    reply = r.json()["generated_text"]
    hist.append({"role":"assistant","content": reply})
    st.session_state["history"] = hist

for m in st.session_state.get("history", []):
    with st.chat_message(m["role"]): st.markdown(m["content"])