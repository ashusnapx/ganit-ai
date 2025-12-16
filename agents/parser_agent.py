import re
from typing import Dict, List

# ----------------------
# Topic inference rules
# ----------------------
TOPIC_KEYWORDS = {
    "algebra": ["solve", "equation", "root", "polynomial"],
    "probability": ["probability", "chance", "random", "dice", "coin"],
    "calculus": ["limit", "derivative", "integral", "differentiate"],
    "linear_algebra": ["matrix", "determinant", "vector", "eigen"]
}


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def infer_topic(text: str) -> str:
    lowered = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return topic
    return "unknown"


def extract_variables(text: str) -> List[str]:
    # Single-letter variables (x, y, z etc.)
    return sorted(set(re.findall(r"\b[a-z]\b", text)))


def extract_constraints(text: str) -> List[str]:
    constraints = []

    patterns = [
        r"[a-z]\s*>\s*0",
        r"[a-z]\s*<\s*0",
        r"[a-z]\s*≥\s*0",
        r"[a-z]\s*≤\s*0"
    ]

    for pattern in patterns:
        constraints.extend(re.findall(pattern, text))

    return constraints


def detect_ambiguity(text: str, variables: List[str]) -> Dict:
    questions = []
    lowered = text.lower()

    if "find" in lowered and "?" not in lowered:
        questions.append("What exactly needs to be found?")

    if variables and "real" not in lowered:
        questions.append("Should the variables be assumed real numbers?")

    return {
        "needs_clarification": len(questions) > 0,
        "clarification_questions": questions
    }


def parse_problem(raw_text: str) -> Dict:
    cleaned = clean_text(raw_text)
    variables = extract_variables(cleaned)
    ambiguity = detect_ambiguity(cleaned, variables)

    return {
        "problem_text": cleaned,
        "topic": infer_topic(cleaned),
        "variables": variables,
        "constraints": extract_constraints(cleaned),
        "assumptions": ["variables are real unless specified"],
        "needs_clarification": ambiguity["needs_clarification"],
        "clarification_questions": ambiguity["clarification_questions"]
    }
