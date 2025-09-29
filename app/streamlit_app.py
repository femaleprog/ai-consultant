# app/streamlit_app.py  (updated)
import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from modes import system_prompt_for_mode

# --- env & client ---
load_dotenv(override=True)
HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("MODEL_ID", "openai/gpt-oss-20b")
TGI_BASE_URL = os.getenv("TGI_BASE_URL", "https://router.huggingface.co/v1")
client = OpenAI(base_url=TGI_BASE_URL, api_key=HF_TOKEN)

st.set_page_config(page_title="AI Consultant Coach", page_icon="🧭", layout="wide")
st.title("🧭 AI Consultant Coach")

# --- sidebar controls ---
with st.sidebar:
    st.subheader("Controls")
    mode = st.selectbox("Mode", ["Mentor", "Interviewer"], index=0)
    model = st.text_input("Model", value=MODEL_ID, help="HF model id")
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
    max_tokens = st.slider("Max tokens", 64, 2048, 600, 32)
    st.divider()

    system_prompt = system_prompt_for_mode(mode)
    st.text_area("System prompt (editable)", value=system_prompt, height=140)

# --- top of main page: INTERVIEWER + fixed controls ---
st.header("Interviewer")
with st.container():
    col1, col2 = st.columns([0.35, 0.65])
    with col1:
        industry = st.selectbox(
            "Industry",
            ["Energy", "Banking", "Retail", "Transport", "Healthcare"],
            key="top_industry",
        )
    with col2:
        case_seed = st.text_area(
            "Case brief",
            value=("A client reports declining profitability despite stable revenue. "
                   "Diagnose the drivers and outline a prioritized plan."),
            height=90,
            key="top_case_seed",
        )
    start = st.button("Start new case", use_container_width=True)

if start:
    st.session_state.history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"[{industry}] {case_seed}"},
    ]
    st.session_state.notes = ""
    st.session_state.start_time = time.time()
    st.toast(f"New case started in {mode} mode.", icon="🟢")
    # --- chat area (interleaved) ---
st.subheader("Chat")

# 1) Render history in order (skip system)
for msg in st.session_state.history:
    if msg["role"] == "system":
        continue
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        st.markdown(msg["content"])

# 2) Input box
user_msg = st.chat_input("Type your message for the interviewer…")
if user_msg:
    # append + render user immediately
    st.session_state.history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # call model
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=st.session_state.history,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        assistant_text = resp.choices[0].message.content
    except Exception as e:
        assistant_text = f"⚠️ Error calling model: {e}"

    # append + render assistant
    st.session_state.history.append({"role": "assistant", "content": assistant_text})
    with st.chat_message("assistant"):
        st.markdown(assistant_text)

    # force a clean rerun so next render shows the full, interleaved history once
    st.rerun()


# --- init session state ---
if "history" not in st.session_state:
    st.session_state.history = [{"role": "system", "content": system_prompt}]
