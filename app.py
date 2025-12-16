import streamlit as st
from tools.ocr import run_ocr
from tools.asr import transcribe_audio

st.set_page_config(page_title="GanitAI", layout="centered")

st.title("GanitAI – Multimodal Math Mentor")

# ======================
# IMAGE OCR INPUT
# ======================
st.header("🖼️ Image Input")

uploaded = st.file_uploader(
    "Upload a math problem image",
    type=["png", "jpg", "jpeg"]
)

if uploaded:
    with open("temp.png", "wb") as f:
        f.write(uploaded.getbuffer())

    ocr_result = run_ocr("temp.png")

    st.subheader("Extracted Text (OCR)")
    edited_ocr_text = st.text_area(
        "Edit before solving:",
        value=ocr_result["text"],
        height=200
    )

    st.caption(
        f"OCR type: {ocr_result['ocr_type']} | "
        f"Confidence: {ocr_result['confidence']}"
    )

    if ocr_result["confidence"] < 0.75:
        st.warning(
            "Low OCR confidence — please review carefully (HITL)"
        )

# ======================
# AUDIO ASR INPUT
# ======================
st.header("🎙️ Audio Input")

audio_mode = st.radio(
    "Choose audio input method:",
    ["🎙️ Speak now (record)", "📁 Upload audio file"],
    horizontal=True
)

audio_path = None

# 🎙️ Realtime microphone recording
if audio_mode == "🎙️ Speak now (record)":
    audio_bytes = st.audio_input("Speak your math question")

    if audio_bytes:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes.getbuffer())
        audio_path = "temp_audio.wav"

# 📁 Upload audio file
else:
    audio_file = st.file_uploader(
        "Upload an audio file",
        type=["wav", "mp3", "m4a"]
    )

    if audio_file:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.getbuffer())
        audio_path = "temp_audio.wav"

# ======================
# ASR PROCESSING
# ======================
if audio_path:
    asr_result = transcribe_audio(audio_path)

    st.subheader("Transcription Preview")

    st.markdown(
        asr_result["highlighted_html"],
        unsafe_allow_html=True
    )

    edited_asr_text = st.text_area(
        "Edit transcription before solving:",
        value=asr_result["raw_text"],
        height=150
    )

    st.caption(f"ASR confidence: {asr_result['confidence']}")

    if asr_result["confidence"] < 0.75:
        st.warning(
            "Low transcription confidence — review highlighted words (HITL)"
        )
