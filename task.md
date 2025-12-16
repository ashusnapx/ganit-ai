## PHASE 0 — Mental Model (sabse pehle yeh dimag mein baithao)

GanitAI =
**Input → Parse → Plan → Retrieve → Solve → Verify → Explain → Learn**

Agar is chain ka koi link weak hua, reviewer pakad lega.

---

## PHASE 1 — Repo + Skeleton (Day 0–0.5)

**Goal:** Project ko professional shape dena before any AI magic.

### Step 1.1 — Repo structure

```
ganitai/
 ├─ app.py (Streamlit entry)
 ├─ agents/
 │   ├─ parser_agent.py
 │   ├─ intent_router.py
 │   ├─ solver_agent.py
 │   ├─ verifier_agent.py
 │   └─ explainer_agent.py
 ├─ rag/
 │   ├─ kb_docs/
 │   ├─ ingest.py
 │   └─ retriever.py
 ├─ memory/
 │   ├─ store.py
 │   └─ recall.py
 ├─ tools/
 │   ├─ ocr.py
 │   ├─ asr.py
 │   └─ calculator.py
 ├─ diagrams/
 │   └─ architecture.mmd
 ├─ .env.example
 ├─ requirements.txt
 └─ README.md
```

**Why recruiter likes this:**
Clear separation = systems thinking.

---

## PHASE 2 — Multimodal Input (Mandatory, no shortcuts)

### Step 2.1 — Image → Text (OCR)

* Use **PaddleOCR / EasyOCR**
* Extract text
* Show **confidence score**
* Display editable textbox

**Trigger HITL if:**

* confidence < threshold
* math symbols missing (√, ^, subscripts)

📌 *Brownie upgrade:*
Auto-detect handwritten vs printed → tweak OCR params.

---

### Step 2.2 — Audio → Text (ASR)

* Whisper / faster-whisper
* Math phrase normalization
  (“square root of x” → √x)

Show transcript → user confirms

📌 *Brownie:*
Highlight uncertain words in yellow.

---

### Step 2.3 — Text Input

* Plain textarea
* Still send through Parser Agent (no bypass)

---

## PHASE 3 — Parser Agent (critical intelligence layer)

### Step 3.1 — Build Parser Agent

Input: raw text
Output (structured JSON):

```
problem_text
topic
variables
constraints
ambiguities
needs_clarification
```

Parser must:

* clean OCR/ASR junk
* detect missing constraints
* detect multiple interpretations

**If needs_clarification = true → HITL**

📌 *Brownie:*
Auto-suggest clarification questions.

---

## PHASE 4 — RAG Pipeline (knowledge grounding)

### Step 4.1 — Knowledge Base (10–30 docs)

Include:

* formulas
* common mistakes
* domain constraints
* solution templates

Small but **curated**. Quality > quantity.

---

### Step 4.2 — Retrieval

* chunk → embed → FAISS/Chroma
* retrieve top-k
* **show retrieved chunks in UI**

🚨 Rule:
If retrieval empty → model must say *“I don’t know”*

📌 *Brownie:*
Tag each chunk with difficulty + topic.

---

## PHASE 5 — Multi-Agent Orchestration (core evaluation signal)

### Step 5.1 — Intent Router Agent

* Decides flow:
  algebra vs probability vs calculus
* Chooses tools (calculator / symbolic)

---

### Step 5.2 — Solver Agent

* Uses:

  * structured problem
  * retrieved context
  * python calculator if needed
* Produces:

  * final answer
  * intermediate reasoning (hidden)

📌 *Brownie:*
Multiple solution strategies → pick best.

---

### Step 5.3 — Verifier / Critic Agent

Checks:

* correctness
* domain validity
* edge cases

Outputs confidence score.

**Low confidence → HITL**

📌 *Brownie:*
Self-check with alternative method.

---

### Step 5.4 — Explainer / Tutor Agent

* Step-by-step
* Student-friendly
* No hallucinated claims

📌 *Brownie:*
Explain *why common mistakes happen*.

---

## PHASE 6 — UI (Streamlit, but serious)

Must-have panels:

* Input selector
* OCR / ASR preview
* Agent trace (who ran, why)
* Retrieved context
* Final answer
* Confidence meter
* Feedback buttons

📌 *Brownie:*
Timeline view of agent execution.

---

## PHASE 7 — HITL (don’t fake it)

Human can:

* edit parsed question
* correct solution
* add comment

Approved correction stored as **learning signal**.

---

## PHASE 8 — Memory & Self-Learning (this is gold)

### Step 8.1 — Store

Save:

* original input
* parsed structure
* retrieved docs
* final answer
* verifier score
* user feedback

### Step 8.2 — Recall

Before solving:

* search similar past problems
* reuse:

  * solution patterns
  * OCR fixes
  * phrasing corrections

📌 *Brownie:*
Show “similar problem solved earlier” badge.

---

## PHASE 9 — Deployment + Proof

* Deploy on Streamlit Cloud / HF Spaces
* Demo video must show:
  image → solve
  audio → solve
  HITL
  memory reuse

---

## PHASE 10 — README that screams “hire me”

Include:

* architecture diagram
* agent responsibilities
* why this is reliable
* limitations (shows maturity)

---

### Final mental shortcut (yaad rakhne ke liye):

**Input → Structure → Ground → Reason → Verify → Teach → Learn**

Agar tum chaho, next step mein hum:

* **exact tech stack lock**
* ya **architecture diagram (Mermaid)**
* ya **agent prompt designs**

Universe chaotic hai, par GanitAI ko hum disciplined rakhenge.
