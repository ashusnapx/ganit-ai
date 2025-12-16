from typing import Dict, List
from tools.calculator import safe_calculate


class SolverAgent:
    """
    Solves math problems using RAG context and routing decisions.
    """

    def solve(
        self,
        parsed_problem: Dict,
        retrieved_chunks: List[Dict],
        route_plan: Dict
    ) -> Dict:

        domain = route_plan["domain"]
        style = route_plan["solution_style"]
        tools = route_plan["tools"]

        problem_text = parsed_problem["problem_text"]

        # -------------------------
        # Strategy 1: Symbolic reasoning
        # -------------------------
        symbolic_answer = None
        symbolic_confidence = 0.0
        symbolic_reasoning = ""

        try:
            symbolic_reasoning = (
                "Using retrieved formulas and standard solution templates."
            )

            # Extremely simplified demo logic
            if domain == "calculus" and "sin x / x" in problem_text:
                symbolic_answer = "The limit is 1."
                symbolic_confidence = 0.9

            elif domain == "algebra" and "x^2" in problem_text:
                symbolic_answer = "Solve the quadratic equation using standard methods."
                symbolic_confidence = 0.7

        except Exception:
            pass

        # -------------------------
        # Strategy 2: Numeric calculation (if allowed)
        # -------------------------
        numeric_answer = None
        numeric_confidence = 0.0
        numeric_reasoning = ""

        if "calculator" in tools:
            try:
                numeric_reasoning = "Evaluating numerically using calculator tool."

                # Placeholder example
                numeric_value = safe_calculate("1 + 1")
                numeric_answer = f"Numeric evaluation gives {numeric_value}."
                numeric_confidence = 0.6

            except Exception:
                pass

        # -------------------------
        # Pick best strategy
        # -------------------------
        if symbolic_confidence >= numeric_confidence:
            return {
                "final_answer": symbolic_answer or "Unable to solve symbolically.",
                "confidence": symbolic_confidence,
                "strategy_used": "symbolic",
                "internal_reasoning": symbolic_reasoning
            }
        else:
            return {
                "final_answer": numeric_answer or "Unable to solve numerically.",
                "confidence": numeric_confidence,
                "strategy_used": "numeric",
                "internal_reasoning": numeric_reasoning
            }
