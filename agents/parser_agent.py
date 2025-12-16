import re
from typing import Dict, List


TOPIC_KEYWORDS = {
    "algebra": ["solve", "equation", "root", "polynomial"],
    "probability": ["probability", "chance", "random", "dice", "coin"],
    "calculus": ["limit", "derivative", "integral", "differentiate"],
    "linear_algebra": ["matrix", "determinant", "vector", "eigen"]
}


def infer_topic(text: str) -> str:
    lowered = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return topic
    return "unknown"


def extract_variables(text: str) -> List[str]:
    # Single-letter variables common in JEE problems
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
        matches = re.findall(pattern, text)
        constraints.extend(matches)

    return constraints


def detect_ambiguity(text: str) -> Dict:
    questions = []

    if "find" in text.lower() and "?" not in text:
        questions.append("What exactly needs to be found?")

    if "x" in text and "real" not in text.lower():
        questions.append("Should variables be assumed real numbers?")

    return {
        "needs_clarification": len(questions) > 0,
        "clarification_questions": questions
    }


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def parse_problem(raw_text: str) -> Dict:
    cleaned = clean_text(raw_text)
    topic = infer_topic(cleaned)
    variables = extract_variables(cleaned)
    constraints = extract_constraints(cleaned)
    ambiguity = detect_ambiguity(cleaned)

    return {
        "problem_text": cleaned,
        "topic": topic,
        "variables": variables,
        "constraints": constraints,
        "assumptions": ["variables are real unless specified"],
        "needs_clarification": ambiguity["needs_clarification"],
        "clarification_questions": ambiguity["clarification_questions"]
    }
