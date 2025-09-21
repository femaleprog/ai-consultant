# app/streamlit_app.py
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

# --- config / env ---
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env", override=True)
HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("MODEL_ID", "openai/gpt-oss-20b")
TGI_BASE_URL = os.getenv("TGI_BASE_URL", "https://router.huggingface.co/v1")

# --- client ---
client = OpenAI(base_url=TGI_BASE_URL, api_key=HF_TOKEN)

st.set_page_config(page_title="AI Consultant Coach", page_icon="🧭", layout="wide")
st.title("🧭 AI Consultant Coach")
st.caption("Powered by GPT-OSS-20B via Hugging Face (TGI / OpenAI-compatible API)")

st.sidebar.markdown(f"**API base:** `{TGI_BASE_URL}`")
st.sidebar.markdown("**HF token loaded:** " + ("✅" if bool(HF_TOKEN) else "❌"))
st.sidebar.markdown(f"**Model:** `{MODEL_ID}`")

# --- sidebar controls ---
with st.sidebar:
    st.subheader("Controls")
    model = st.text_input("Model", value=MODEL_ID, help="HF model id")
    lang = st.selectbox("Language", ["English", "Français", "Darija"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
    max_tokens = st.slider("Max tokens", 64, 2048, 600, 32)
    st.divider()

    st.subheader("System Preset")
    preset = st.selectbox(
        "Role",
        [
            "Consultant Coach (default)",
            "Strict Interviewer",
            "Evaluator-lite (gives brief feedback)"
        ],
    )

    def system_prompt_for(preset_name: str, lang_: str) -> str:
        base = {
            "Consultant Coach (default)": (
                "You are an AI Consultant Coach. Be concise, MECE, and actionable. "
                "Guide step-by-step: ask clarifying questions, encourage structured thinking, "
                "and summarize at the end with next actions."
            ),
            "Strict Interviewer": (
                "Act as a case interviewer. Ask one question at a time, be terse, reveal data only when asked, "
                "and keep the candidate focused on structure and quantification."
            ),
            "Evaluator-lite (gives brief feedback)": (
                "Act as a brief evaluator. After the candidate answer, provide a short rubric comment on structure, "
                "quant reasoning, and insight. Keep guidance to 3 bullets."
            ),
        }[preset_name]
        if lang_ == "Français":
            base += " Réponds en français."
        elif lang_ == "Darija":
            base += " Jawb b darija w khalli l’style sahl w mfhum."
        return base

    system_prompt = system_prompt_for(preset, lang)
    st.text_area("System prompt (editable)", value=system_prompt, height=140)

    st.divider()
    st.subheader("Start a case")
    industry = st.selectbox("Industry", ["Energy", "Banking", "Retail", "Transport", "Healthcare"])
    case_seed = st.text_area(
        "Case brief",
        value=(
            "A client reports declining profitability despite stable revenue. "
            "Diagnose the drivers and outline a prioritized plan."
        ),
        height=90,
    )
    if st.button("Start new case", use_container_width=True):
        st.session_state.history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"[{industry}] {case_seed}"},
        ]
        st.session_state.notes = ""
        st.session_state.start_time = time.time()
        st.toast("New case started.", icon="🟢")

# --- init session state ---
if "history" not in st.session_state:
    st.session_state.history = [{"role": "system", "content": system_prompt}]
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# --- layout: chat (left) and tools (right) ---
left, right = st.columns([0.65, 0.35])

with left:
    st.subheader("Chat")
    # display past turns
    for msg in st.session_state.history:
        if msg["role"] == "system":
            continue
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])

    user_msg = st.chat_input("Type your answer, ask for data, or outline your structure…")
    if user_msg:
        st.session_state.history.append({"role": "user", "content": user_msg})

        # streaming response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            stream_text = ""
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.history,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for event in stream:
                delta = event.choices[0].delta.content or ""
                stream_text += delta
                placeholder.markdown(stream_text)
            st.session_state.history.append({"role": "assistant", "content": stream_text})

with right:
    st.subheader("⏱️ Timer")
    elapsed = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
    st.metric("Elapsed (min)", f"{elapsed//60}:{elapsed%60:02d}")

    st.divider()
    st.subheader("📝 Notes")
    st.session_state.notes = st.text_area("Your scratchpad", value=st.session_state.notes, height=220)

    st.divider()
    st.subheader("📦 Export")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export JSON"):
            import json, datetime
            payload = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "history": st.session_state.history,
                "notes": st.session_state.notes,
                "controls": {
                    "model": model, "temperature": temperature, "max_tokens": max_tokens,
                    "language": lang, "preset": preset
                },
            }
            st.download_button(
                "Download chat.json",
                data=json.dumps(payload, ensure_ascii=False, indent=2),
                file_name="chat.json",
                mime="application/json",
                use_container_width=True,
            )
    with col2:
        if st.button("Export Markdown"):
            md = "# Conversation\n\n" + "\n\n".join(
                [f"**{m['role'].upper()}**: {m['content']}" for m in st.session_state.history if m["role"] != "system"]
            ) + "\n\n---\n## Notes\n" + st.session_state.notes
            st.download_button(
                "Download chat.md",
                data=md,
                file_name="chat.md",
                mime="text/markdown",
                use_container_width=True,
            )

st.markdown(
    "<style>.stChatMessageContent p{margin-bottom:0.4rem}</style>",
    unsafe_allow_html=True,
)
