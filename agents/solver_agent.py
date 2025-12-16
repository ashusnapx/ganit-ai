from typing import Dict, List, Optional
from tools.calculator import safe_calculate


class SolverAgent:
    """
    Solves math problems using:
    - structured parsed problem
    - retrieved RAG context
    - intent routing decisions
    - optional memory-aware solver bias
    """

    def solve(
        self,
        parsed_problem: Dict,
        retrieved_chunks: List[Dict],
        route_plan: Dict,
        memory_bias: Optional[Dict] = None
    ) -> Dict:

        # -------------------------
        # Defensive guards
        # -------------------------
        if not parsed_problem or not route_plan:
            return {
                "final_answer": "Insufficient information to solve the problem.",
                "confidence": 0.0,
                "strategy_used": "none",
                "internal_reasoning": "Missing parsed problem or routing plan."
            }

        domain = route_plan.get("domain", "unknown")
        style = route_plan.get("solution_style", "symbolic")
        tools = route_plan.get("tools", [])

        problem_text = parsed_problem.get("problem_text", "").lower()

        reasoning_notes = []

        # -------------------------
        # Apply MEMORY-AWARE BIAS (PHASE 9)
        # -------------------------
        if memory_bias:
            reasoning_notes.append(
                "Incorporating guidance from previously verified similar problems."
            )

            for s in memory_bias.get("preferred_strategies", []):
                reasoning_notes.append(f"Strategy hint: {s}")

            for w in memory_bias.get("warnings", []):
                reasoning_notes.append(f"Constraint reminder: {w}")

        # -------------------------
        # Strategy 1: Symbolic reasoning
        # -------------------------
        symbolic_answer = None
        symbolic_confidence = 0.0

        try:
            reasoning_notes.append(
                "Attempting symbolic reasoning using known formulas and templates."
            )

            # ---- DEMO symbolic patterns (intentionally simple) ----
            if domain == "calculus":
                if "sin" in problem_text and "/ x" in problem_text:
                    symbolic_answer = "The limit is 1."
                    symbolic_confidence = 0.9

            elif domain == "algebra":
                if "x^2" in problem_text or "quadratic" in problem_text:
                    symbolic_answer = (
                        "Solve the quadratic equation using factorization "
                        "or the quadratic formula."
                    )
                    symbolic_confidence = 0.7

        except Exception as e:
            reasoning_notes.append(
                f"Symbolic reasoning failed safely: {str(e)}"
            )

        # -------------------------
        # Strategy 2: Numeric calculation (if allowed)
        # -------------------------
        numeric_answer = None
        numeric_confidence = 0.0

        if "calculator" in tools:
            try:
                reasoning_notes.append(
                    "Attempting numeric evaluation using calculator tool."
                )

                # Placeholder safe numeric example
                numeric_value = safe_calculate("1 + 1")
                numeric_answer = f"Numeric evaluation gives {numeric_value}."
                numeric_confidence = 0.6

            except Exception as e:
                reasoning_notes.append(
                    f"Numeric calculation failed safely: {str(e)}"
                )

        # -------------------------
        # Pick best strategy
        # -------------------------
        if symbolic_confidence >= numeric_confidence:
            return {
                "final_answer": symbolic_answer or "Unable to derive a symbolic solution.",
                "confidence": round(symbolic_confidence, 3),
                "strategy_used": "symbolic",
                "internal_reasoning": reasoning_notes
            }

        return {
            "final_answer": numeric_answer or "Unable to compute numeric solution.",
            "confidence": round(numeric_confidence, 3),
            "strategy_used": "numeric",
            "internal_reasoning": reasoning_notes
        }
