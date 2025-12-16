def extract_solver_bias(similar_memories):
    """
    Convert recalled memories into solver hints.
    """

    if not similar_memories:
        return None

    strategies = []
    warnings = []

    for mem in similar_memories:
        parsed = mem.get("parsed_problem", {})
        topic = parsed.get("topic")

        if topic:
            strategies.append(
                f"Previously solved a {topic} problem using verified approach."
            )

        # Example: capture common assumptions
        assumptions = parsed.get("assumptions", [])
        for a in assumptions:
            warnings.append(f"Assume: {a}")

    return {
        "preferred_strategies": list(set(strategies)),
        "warnings": list(set(warnings))
    }
