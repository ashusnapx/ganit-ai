import streamlit as st

from tools.ocr import run_ocr
from tools.asr import transcribe_audio
from agents.parser_agent import parse_problem
from agents.intent_router import route_intent
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from agents.explainer_agent import ExplainerAgent
from rag.retriever import Retriever
from memory.store_hitl import store_hitl_signal

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="GanitAI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SESSION STATE INIT (CRITICAL)
# =========================================================
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "pipeline" not in st.session_state:
    st.session_state.pipeline = {}

# =========================================================
# BRAND HEADER
# =========================================================
st.markdown(
    """
    <h1 style="margin-bottom:0;">GanitAI</h1>
    <p style="color:gray; margin-top:0;">
    Multimodal Math Mentor • Reliable • Explainable • HITL-Safe<br>
    <b>Made by Ashutosh Kumar</b> — 
    <a href="https://github.com/ashusnapx" target="_blank">@ashusnapx</a>
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
# STEP 1 — INPUT
# =========================================================
st.subheader("Step 1 · Provide the problem")

input_mode = st.radio(
    "Choose input type",
    ["🖼️ Image", "🎙️ Audio", "⌨️ Text"],
    horizontal=True
)

raw_input = ""

if input_mode == "🖼️ Image":
    uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    if uploaded:
        with st.spinner("Running OCR…"):
            with open("temp.png", "wb") as f:
                f.write(uploaded.getbuffer())
            ocr = run_ocr("temp.png")
        raw_input = st.text_area("Edit OCR text", ocr["text"], height=160)

elif input_mode == "🎙️ Audio":
    audio = st.audio_input("Speak your question")
    if audio:
        with open("temp.wav", "wb") as f:
            f.write(audio.getbuffer())
        with st.spinner("Transcribing…"):
            asr = transcribe_audio("temp.wav")
        raw_input = st.text_area("Edit transcription", asr["raw_text"], height=140)

elif input_mode == "⌨️ Text":
    raw_input = st.text_area(
        "Type your math problem",
        height=160,
        placeholder="Find the limit of sin(x)/x as x → 0"
    )

# ---------- SUBMIT BUTTON (IMPORTANT FIX) ----------
if st.button("🚀 Submit problem"):
    if raw_input.strip():
        st.session_state.submitted = True
        st.session_state.pipeline = {
            "raw_input": raw_input.strip()
        }
    else:
        st.warning("Please enter a problem before submitting.")

# =========================================================
# STOP IF NOT SUBMITTED
# =========================================================
if not st.session_state.submitted:
    st.stop()

# =========================================================
# STEP 2 — PARSER
# =========================================================
st.divider()
st.subheader("Step 2 · Understanding the problem")

with st.spinner("Parsing problem…"):
    parsed = parse_problem(st.session_state.pipeline["raw_input"])

st.session_state.pipeline["parsed_problem"] = parsed

with st.expander("Parser output"):
    st.json(parsed)

# =========================================================
# STEP 3 — RAG
# =========================================================
st.divider()
st.subheader("Step 3 · Grounding with knowledge")

with st.spinner("Retrieving knowledge…"):
    retrieved = retriever.retrieve(parsed["problem_text"])

if not retrieved:
    st.error("I don’t know. No relevant knowledge found.")
    st.stop()

st.session_state.pipeline["retrieved_chunks"] = retrieved

for i, c in enumerate(retrieved, 1):
    with st.expander(f"Context {i} · {c['topic']}"):
        st.write(c["text"])

# =========================================================
# STEP 4 — REASONING
# =========================================================
st.divider()
st.subheader("Step 4 · Reasoning & verification")

router = route_intent(parsed)

solver = SolverAgent()
verifier = VerifierAgent()
explainer = ExplainerAgent()

with st.spinner("Solving…"):
    solution = solver.solve(parsed, retrieved, router)

with st.spinner("Verifying…"):
    verification = verifier.verify(parsed, solution, retrieved)

st.session_state.pipeline["solution"] = solution
st.session_state.pipeline["verification"] = verification

st.progress(verification["confidence"])

# =========================================================
# STEP 5 — HITL
# =========================================================
if verification["needs_human_review"]:
    st.warning("Low confidence — human review required")

    corrected_q = st.text_area(
        "Correct question",
        parsed["problem_text"]
    )

    corrected_a = st.text_area(
        "Correct answer",
        solution["final_answer"]
    )

    comment = st.text_area("Reviewer comment")

    if st.checkbox("Approve correction as ground truth"):
        if st.button("✅ Save correction"):
            store_hitl_signal({
                "original_question": parsed["problem_text"],
                "ai_answer": solution["final_answer"],
                "human_corrected_question": corrected_q,
                "human_corrected_answer": corrected_a,
                "comment": comment,
                "approved": True
            })
            st.success("Correction stored.")
            st.stop()

# =========================================================
# STEP 6 — FINAL EXPLANATION
# =========================================================
st.divider()
st.subheader("Step 5 · Final Answer")

explanation = explainer.explain(
    parsed,
    solution,
    verification,
    retrieved
)

st.markdown(f"### ✅ {explanation['final_answer']}")

st.markdown("#### 📖 Explanation")
for i, step in enumerate(explanation["explanation_steps"], 1):
    st.write(f"{i}. {step}")

st.markdown("#### ⚠️ Common mistakes")
for m in explanation["common_mistakes"]:
    st.write(f"• {m}")

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
