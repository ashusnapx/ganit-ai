from typing import Dict


def route_intent(parsed_problem: Dict) -> Dict:
    """
    Decide solution flow and tool usage based on parsed problem.
    """

    topic = parsed_problem.get("topic", "unknown")
    text = parsed_problem.get("problem_text", "").lower()

    domain = topic
    solution_style = "symbolic"
    tools = []
    reason = ""

    # -------------------------
    # Algebra
    # -------------------------
    if topic == "algebra":
        domain = "algebra"

        if any(k in text for k in ["approx", "value", "evaluate"]):
            solution_style = "numeric"
            tools = ["calculator"]
            reason = "Algebraic problem requiring numeric evaluation"
        else:
            solution_style = "symbolic"
            reason = "Algebraic equation suitable for symbolic solving"

    # -------------------------
    # Calculus
    # -------------------------
    elif topic == "calculus":
        domain = "calculus"

        if "limit" in text:
            solution_style = "symbolic"
            reason = "Limit evaluation using known calculus rules"

        elif any(k in text for k in ["approx", "value"]):
            solution_style = "numeric"
            tools = ["calculator"]
            reason = "Calculus problem requiring numeric approximation"

        else:
            solution_style = "symbolic"
            reason = "Derivative/integral solvable symbolically"

    # -------------------------
    # Probability
    # -------------------------
    elif topic == "probability":
        domain = "probability"
        solution_style = "symbolic"
        reason = "Probability problems solved using formula-based reasoning"

    # -------------------------
    # Linear Algebra
    # -------------------------
    elif topic == "linear_algebra":
        domain = "linear_algebra"

        if "determinant" in text or "inverse" in text:
            solution_style = "numeric"
            tools = ["calculator"]
            reason = "Matrix computation requires numeric calculation"
        else:
            solution_style = "symbolic"
            reason = "Linear algebra reasoning without heavy computation"

    # -------------------------
    # Unknown / fallback
    # -------------------------
    else:
        domain = "unknown"
        solution_style = "symbolic"
        reason = "Unable to classify problem confidently"

    return {
        "domain": domain,
        "solution_style": solution_style,
        "tools": tools,
        "reason": reason
    }
