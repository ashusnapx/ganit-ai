import streamlit as st
from datetime import datetime

from tools.ocr import run_ocr
from tools.asr import transcribe_audio
from agents.parser_agent import parse_problem
from agents.intent_router import route_intent
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from agents.explainer_agent import ExplainerAgent
from rag.retriever import Retriever
from memory.recall_memory import recall_similar
from memory.solver_bias import extract_solver_bias
from memory.store_hitl import store_hitl_signal
# from memory.store_memory import store_solved_example


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="GanitAI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SESSION STATE (CRITICAL FOR STABILITY)
# =========================================================
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "pipeline" not in st.session_state:
    st.session_state.pipeline = {}

if "run_id" not in st.session_state:
    st.session_state.run_id = datetime.utcnow().isoformat()

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
    uploaded = st.file_uploader("Upload a math problem image", type=["png", "jpg", "jpeg"])
    if uploaded:
        with st.spinner("Extracting text from image…"):
            with open("temp.png", "wb") as f:
                f.write(uploaded.getbuffer())
            ocr = run_ocr("temp.png")
        raw_input = st.text_area("Review OCR text", ocr["text"], height=160)

elif input_mode == "🎙️ Audio":
    audio = st.audio_input("Speak your math question")
    if audio:
        with open("temp.wav", "wb") as f:
            f.write(audio.getbuffer())
        with st.spinner("Transcribing audio…"):
            asr = transcribe_audio("temp.wav")
        st.markdown(asr["highlighted_html"], unsafe_allow_html=True)
        raw_input = st.text_area("Review transcription", asr["raw_text"], height=140)

elif input_mode == "⌨️ Text":
    raw_input = st.text_area(
        "Type your math problem",
        height=160,
        placeholder="Example: Find the limit of sin(x)/x as x → 0"
    )

# ---------------------------------------------------------
# SUBMIT BUTTON (RETENTION + STABILITY)
# ---------------------------------------------------------
st.markdown("###")
if st.button("🚀 Submit & Analyze", use_container_width=True):
    if raw_input.strip():
        st.session_state.submitted = True
        st.session_state.pipeline = {
            "raw_input": raw_input.strip()
        }
    else:
        st.warning("Please enter a valid math problem before submitting.")

if not st.session_state.submitted:
    st.stop()

# =========================================================
# STEP 2 — PARSER
# =========================================================
st.divider()
st.subheader("Step 2 · Understanding the problem")

with st.spinner("Analyzing problem structure…"):
    parsed_problem = parse_problem(st.session_state.pipeline["raw_input"])

st.session_state.pipeline["parsed_problem"] = parsed_problem

with st.expander("How GanitAI understands your problem"):
    st.json(parsed_problem)

# =========================================================
# STEP 3 — MEMORY RECALL (PHASE 8)
# =========================================================
st.divider()
st.subheader("Step 3 · Learning from past problems")

similar_memories = recall_similar(parsed_problem["problem_text"])
memory_bias = extract_solver_bias(similar_memories)

if similar_memories:
    st.success("🧠 Similar problem solved earlier — using learned patterns")
    for mem in similar_memories:
        with st.expander(f"Similarity score: {mem['similarity']}"):
            st.code(mem["final_answer"])
else:
    st.info("No similar solved problems found. Solving fresh.")

# =========================================================
# STEP 4 — RAG
# =========================================================
st.divider()
st.subheader("Step 4 · Grounding with knowledge")

with st.spinner("Retrieving trusted math knowledge…"):
    retrieved_chunks = retriever.retrieve(parsed_problem["problem_text"])

if not retrieved_chunks:
    st.error("I don’t know. No relevant knowledge found.")
    st.stop()

st.session_state.pipeline["retrieved_chunks"] = retrieved_chunks

for i, chunk in enumerate(retrieved_chunks, 1):
    with st.expander(f"Context {i} · {chunk['topic']} · {chunk['difficulty']}"):
        st.write(chunk["text"])

# =========================================================
# STEP 5 — REASONING + VERIFICATION
# =========================================================
st.divider()
st.subheader("Step 5 · Reasoning & verification")

router = route_intent(parsed_problem)

solver = SolverAgent()
verifier = VerifierAgent()
explainer = ExplainerAgent()

with st.spinner("Solving the problem…"):
    solver_output = solver.solve(
        parsed_problem=parsed_problem,
        retrieved_chunks=retrieved_chunks,
        route_plan=router,
        memory_bias=memory_bias
    )

with st.spinner("Verifying correctness…"):
    verifier_output = verifier.verify(
        parsed_problem,
        solver_output,
        retrieved_chunks
    )

confidence = verifier_output["confidence"]
st.progress(confidence)

# =========================================================
# STEP 6 — HITL (REAL)
# =========================================================
if verifier_output["needs_human_review"]:
    st.error("Low confidence — human review required")

    corrected_q = st.text_area(
        "Edit the problem (if incorrect)",
        parsed_problem["problem_text"]
    )

    corrected_a = st.text_area(
        "Correct the final answer",
        solver_output["final_answer"]
    )

    comment = st.text_area("Reviewer comment")

    if st.checkbox("Approve correction as ground truth"):
        if st.button("✅ Save correction"):
            store_hitl_signal({
                "original_question": parsed_problem["problem_text"],
                "ai_answer": solver_output["final_answer"],
                "human_corrected_question": corrected_q,
                "human_corrected_answer": corrected_a,
                "comment": comment,
                "approved": True
            })
            st.success("Correction saved. Thank you for improving GanitAI.")
            st.stop()

# =========================================================
# STEP 7 — FINAL ANSWER
# =========================================================
st.divider()
st.subheader("Step 6 · Final Answer")

explanation = explainer.explain(
    parsed_problem,
    solver_output,
    verifier_output,
    retrieved_chunks
)

st.markdown(f"### ✅ {explanation['final_answer']}")

st.markdown("#### 📖 Step-by-step explanation")
for i, step in enumerate(explanation["explanation_steps"], 1):
    st.write(f"{i}. {step}")

st.markdown("#### ⚠️ Common mistakes students make")
for m in explanation["common_mistakes"]:
    st.write(f"• {m}")

# =========================================================
# STEP 8 — STORE VERIFIED MEMORY
# =========================================================
if confidence >= 0.8:
    store_solved_example({
        "original_input": parsed_problem["problem_text"],
        "parsed_problem": parsed_problem,
        "retrieved_context": retrieved_chunks,
        "final_answer": explanation["final_answer"],
        "verifier_confidence": confidence,
        "user_feedback": None
    })

# =========================================================
# FOOTER (RETENTION)
# =========================================================
st.divider()
st.markdown(
    """
    <center>
    Built with care by <b>Ashutosh Kumar</b> · 
    <a href="https://github.com/ashusnapx" target="_blank">@ashusnapx</a><br>
    GanitAI learns from verified answers and human feedback.
    </center>
    """,
    unsafe_allow_html=True
)
