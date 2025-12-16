import streamlit as st
from tools.ocr import run_ocr

st.title("GanitAI – Math OCR")

uploaded = st.file_uploader("Upload math problem image", type=["png", "jpg", "jpeg"])

if uploaded:
    with open("temp.png", "wb") as f:
        f.write(uploaded.getbuffer())

    ocr_result = run_ocr("temp.png")

    st.subheader("Extracted Text")
    edited_text = st.text_area(
        "You can edit before solving:",
        value=ocr_result["text"],
        height=200
    )

    st.caption(
        f"OCR type: {ocr_result['ocr_type']} | "
        f"Confidence: {ocr_result['confidence']}"
    )

    if ocr_result["confidence"] < 0.75:
        st.warning("Low OCR confidence — human review recommended (HITL)")
