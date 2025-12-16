import streamlit as st
from tools.ocr import run_ocr
from tools.asr import transcribe_audio
from agents.parser_agent import parse_problem
from agents.intent_router import route_intent
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from agents.explainer_agent import ExplainerAgent
from rag.retriever import Retriever

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="GanitAI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# BRAND HEADER
# =========================================================
st.markdown(
    """
    <h1 style="margin-bottom:0;">GanitAI</h1>
    <p style="color:gray; margin-top:0;">
    Multimodal Math Mentor • Reliable • Explainable • HITL-Safe<br>
    <b>Made by Ashutosh Kumar</b> — <a href="https://github.com/ashusnapx" target="_blank">@ashusnapx</a>
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# LOAD RAG (CACHED)
# =========================================================
@st.cache_resource
def load_retriever():
    return Retriever(top_k=4)

retriever = load_retriever()

# =========================================================
# STEP 1 — INPUT MODE
# =========================================================
st.subheader("Step 1 · Provide the problem")

input_mode = st.radio(
    "Choose input type",
    ["🖼️ Image", "🎙️ Audio", "⌨️ Text"],
    horizontal=True
)

final_input_text = None
refined_input_text = None
parsed_problem = None

# =========================================================
# IMAGE INPUT
# =========================================================
if input_mode == "🖼️ Image":
    uploaded = st.file_uploader(
        "Upload a math problem image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded:
        with st.spinner("Running OCR…"):
            with open("temp.png", "wb") as f:
                f.write(uploaded.getbuffer())
            ocr_result = run_ocr("temp.png")

        final_input_text = st.text_area(
            "Edit extracted text if needed",
            value=ocr_result["text"],
            height=180
        )

        st.caption(
            f"OCR confidence: {ocr_result['confidence']} | "
            f"Type: {ocr_result['ocr_type']}"
        )

# =========================================================
# AUDIO INPUT
# =========================================================
elif input_mode == "🎙️ Audio":
    audio_mode = st.radio(
        "Audio input method",
        ["🎙️ Speak now", "📁 Upload file"],
        horizontal=True
    )

    audio_path = None

    if audio_mode == "🎙️ Speak now":
        audio_bytes = st.audio_input("Speak your math question")
        if audio_bytes:
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_bytes.getbuffer())
            audio_path = "temp_audio.wav"
    else:
        audio_file = st.file_uploader(
            "Upload audio",
            type=["wav", "mp3", "m4a"]
        )
        if audio_file:
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_file.getbuffer())
            audio_path = "temp_audio.wav"

    if audio_path:
        with st.spinner("Transcribing audio…"):
            asr_result = transcribe_audio(audio_path)

        st.markdown(asr_result["highlighted_html"], unsafe_allow_html=True)

        final_input_text = st.text_area(
            "Edit transcription",
            value=asr_result["raw_text"],
            height=150
        )

        st.caption(f"ASR confidence: {asr_result['confidence']}")

# =========================================================
# TEXT INPUT
# =========================================================
elif input_mode == "⌨️ Text":
    final_input_text = st.text_area(
        "Type your math problem",
        height=180,
        placeholder="e.g. Find the limit of sin(x)/x as x → 0"
    )

# =========================================================
# STEP 2 — PARSER + HITL
# =========================================================
if final_input_text:
    st.divider()
    st.subheader("Step 2 · Understanding the problem")

    with st.spinner("Parsing problem…"):
        parsed_problem = parse_problem(final_input_text)

    with st.expander("Parser output (structured view)"):
        st.json(parsed_problem)

    if parsed_problem["needs_clarification"]:
        st.warning("Clarification required")

        answers = []
        for i, q in enumerate(parsed_problem["clarification_questions"]):
            ans = st.text_input(f"{i+1}. {q}")
            if ans:
                answers.append(ans)

        if answers:
            refined_input_text = (
                parsed_problem["problem_text"]
                + " | Clarifications: "
                + "; ".join(answers)
            )
            parsed_problem = parse_problem(refined_input_text)

            st.success("Clarifications applied")
    else:
        refined_input_text = parsed_problem["problem_text"]
        st.success("Problem understood")

# =========================================================
# STEP 3 — KNOWLEDGE RETRIEVAL (RAG)
# =========================================================
if refined_input_text:
    st.divider()
    st.subheader("Step 3 · Grounding with knowledge")

    with st.spinner("Retrieving relevant knowledge…"):
        retrieved_chunks = retriever.retrieve(refined_input_text)

    if not retrieved_chunks:
        st.error("I don’t know. No relevant knowledge found.")
        st.stop()

    for i, chunk in enumerate(retrieved_chunks, 1):
        with st.expander(
            f"Context {i} · {chunk['topic']} · {chunk['difficulty']}"
        ):
            st.write(chunk["text"])
            st.caption(f"Source: {chunk['source']}")

# =========================================================
# STEP 4 — REASONING AGENTS
# =========================================================
if refined_input_text and isinstance(parsed_problem, dict):
    st.divider()
    st.subheader("Step 4 · Reasoning & verification")

    # ---------- Intent Router ----------
    with st.spinner("Routing intent…"):
        route_plan = route_intent(parsed_problem)

    with st.expander("Intent Router decision"):
        st.json(route_plan)

    # ---------- Solver ----------
    solver = SolverAgent()

    with st.spinner("Solving problem…"):
        solver_output = solver.solve(
            parsed_problem=parsed_problem,
            retrieved_chunks=retrieved_chunks,
            route_plan=route_plan
        )

    # ---------- Verifier ----------
    verifier = VerifierAgent()

    with st.spinner("Verifying solution…"):
        verifier_output = verifier.verify(
            parsed_problem=parsed_problem,
            solver_output=solver_output,
            retrieved_chunks=retrieved_chunks
        )

    # ---------- Confidence Indicator ----------
    confidence = verifier_output["confidence"]

    st.progress(confidence)

    if verifier_output["needs_human_review"]:
        st.error("Low confidence — human review required")
        st.stop()
else:
    st.warning(
        "Problem not fully parsed yet. "
        "Please complete previous steps."
    )
    st.stop()

# =========================================================
# STEP 5 — FINAL EXPLANATION
# =========================================================
st.divider()
st.subheader("Step 5 · Final Answer")

explanation = explainer.explain(
    parsed_problem,
    solver_output,
    verifier_output,
    retrieved_chunks
)

st.markdown(f"### ✅ {explanation['final_answer']}")

st.markdown("#### 📖 Explanation")
for i, step in enumerate(explanation["explanation_steps"], 1):
    st.write(f"{i}. {step}")

st.markdown("#### ⚠️ Common mistakes")
for m in explanation["common_mistakes"]:
    st.write(f"• {m}")

# =========================================================
# FEEDBACK
# =========================================================
st.divider()
st.subheader("Feedback")

c1, c2 = st.columns(2)
with c1:
    if st.button("👍 Correct"):
        st.success("Thanks! Feedback recorded.")
with c2:
    if st.button("👎 Incorrect"):
        st.text_area("Tell us what was wrong")

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <hr>
    <center>
    Built with care by <b>Ashutosh Kumar</b> · 
    <a href="https://github.com/ashusnapx" target="_blank">@ashusnapx</a>
    </center>
    """,
    unsafe_allow_html=True
)
