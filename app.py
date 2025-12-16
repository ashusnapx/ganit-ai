import streamlit as st
from tools.ocr import run_ocr
from tools.asr import transcribe_audio

st.set_page_config(page_title="GanitAI", layout="centered")
st.title("GanitAI – Multimodal Math Mentor")

# ======================
# INPUT MODE SELECTOR
# ======================
input_mode = st.radio(
    "Choose input type:",
    ["🖼️ Image", "🎙️ Audio", "⌨️ Text"],
    horizontal=True
)

final_input_text = None
input_confidence = None
input_source = None

# ======================
# IMAGE INPUT (OCR)
# ======================
if input_mode == "🖼️ Image":
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
        final_input_text = st.text_area(
            "Edit before solving:",
            value=ocr_result["text"],
            height=200
        )

        input_confidence = ocr_result["confidence"]
        input_source = "image"

        st.caption(
            f"OCR type: {ocr_result['ocr_type']} | "
            f"Confidence: {ocr_result['confidence']}"
        )

        if ocr_result["confidence"] < 0.75:
            st.warning(
                "Low OCR confidence — human review recommended (HITL)"
            )

# ======================
# AUDIO INPUT (ASR)
# ======================
elif input_mode == "🎙️ Audio":
    st.header("🎙️ Audio Input")

    audio_mode = st.radio(
        "Choose audio input method:",
        ["🎙️ Speak now (record)", "📁 Upload audio file"],
        horizontal=True
    )

    audio_path = None

    if audio_mode == "🎙️ Speak now (record)":
        audio_bytes = st.audio_input("Speak your math question")

        if audio_bytes:
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_bytes.getbuffer())
            audio_path = "temp_audio.wav"

    else:
        audio_file = st.file_uploader(
            "Upload an audio file",
            type=["wav", "mp3", "m4a"]
        )

        if audio_file:
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_file.getbuffer())
            audio_path = "temp_audio.wav"

    if audio_path:
        asr_result = transcribe_audio(audio_path)

        st.subheader("Transcription Preview")

        st.markdown(
            asr_result["highlighted_html"],
            unsafe_allow_html=True
        )

        final_input_text = st.text_area(
            "Edit transcription before solving:",
            value=asr_result["raw_text"],
            height=150
        )

        input_confidence = asr_result["confidence"]
        input_source = "audio"

        st.caption(f"ASR confidence: {asr_result['confidence']}")

        if asr_result["confidence"] < 0.75:
            st.warning(
                "Low transcription confidence — please review highlighted words (HITL)"
            )

# ======================
# TEXT INPUT (STEP 2.3)
# ======================
elif input_mode == "⌨️ Text":
    st.header("⌨️ Text Input")

    final_input_text = st.text_area(
        "Type your math question:",
        placeholder=(
            "Example:\n"
            "Find the limit of sin(x)/x as x approaches 0."
        ),
        height=180
    )

    input_confidence = 1.0  # user-typed input assumed high confidence
    input_source = "text"

    st.caption("Confidence: user-provided text (assumed high)")

# ======================
# DEBUG / PREVIEW (temporary)
# ======================
if final_input_text:
    st.divider()
    st.subheader("🧪 Final Normalized Input (Preview)")

    st.code(final_input_text)
    st.caption(
        f"Source: {input_source} | "
        f"Confidence: {input_confidence}"
    )
