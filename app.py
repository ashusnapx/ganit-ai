import streamlit as st
from tools.ocr import run_ocr
from tools.asr import transcribe_audio
from agents.parser_agent import parse_problem

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
# IMAGE INPUT
# ======================
if input_mode == "🖼️ Image":
    uploaded = st.file_uploader(
        "Upload a math problem image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded:
        with open("temp.png", "wb") as f:
            f.write(uploaded.getbuffer())

        ocr_result = run_ocr("temp.png")

        final_input_text = st.text_area(
            "Edit extracted text:",
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
            st.warning("Low OCR confidence — human review recommended (HITL)")

# ======================
# AUDIO INPUT
# ======================
elif input_mode == "🎙️ Audio":
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

        st.markdown(asr_result["highlighted_html"], unsafe_allow_html=True)

        final_input_text = st.text_area(
            "Edit transcription:",
            value=asr_result["raw_text"],
            height=150
        )

        input_confidence = asr_result["confidence"]
        input_source = "audio"

        st.caption(f"ASR confidence: {asr_result['confidence']}")

        if asr_result["confidence"] < 0.75:
            st.warning("Low transcription confidence — review required (HITL)")

# ======================
# TEXT INPUT
# ======================
elif input_mode == "⌨️ Text":
    final_input_text = st.text_area(
        "Type your math question:",
        height=180
    )
    input_confidence = 1.0
    input_source = "text"

# ======================
# PARSER AGENT + HITL
# ======================
if final_input_text:
    st.divider()
    st.header("🧠 Parser Agent")

    parsed_problem = parse_problem(final_input_text)

    with st.expander("Structured representation"):
        st.json(parsed_problem)

    if parsed_problem["needs_clarification"]:
        st.warning("Clarification required before solving")

        answers = []
        for i, q in enumerate(parsed_problem["clarification_questions"]):
            ans = st.text_input(f"{i+1}. {q}")
            if ans:
                answers.append(ans)

        if answers:
            refined_text = (
                parsed_problem["problem_text"]
                + " | Clarifications: "
                + "; ".join(answers)
            )

            st.success("Clarifications applied")
            st.code(refined_text)

            refined_parsed = parse_problem(refined_text)

            with st.expander("Updated structured problem"):
                st.json(refined_parsed)
    else:
        st.success("Problem is well-defined and ready for solving")
