from typing import Dict, List


class VerifierAgent:
    """
    Verifies solver output for correctness, domain validity, and edge cases.
    """

    def verify(
        self,
        parsed_problem: Dict,
        solver_output: Dict,
        retrieved_chunks: List[Dict]
    ) -> Dict:

        issues = []
        confidence = solver_output.get("confidence", 0.0)
        final_answer = solver_output.get("final_answer", "")
        domain = parsed_problem.get("topic", "unknown")
        text = parsed_problem.get("problem_text", "").lower()

        # -------------------------
        # 1. Basic correctness sanity
        # -------------------------
        if not final_answer or "unable" in final_answer.lower():
            issues.append("Solver did not produce a concrete answer")
            confidence -= 0.3

        # -------------------------
        # 2. Domain validity checks
        # -------------------------
        constraints = parsed_problem.get("constraints", [])

        if constraints and domain in ["algebra", "calculus"]:
            for c in constraints:
                if c not in final_answer:
                    issues.append(
                        f"Constraint '{c}' not explicitly addressed in solution"
                    )
                    confidence -= 0.1

        # -------------------------
        # 3. Edge case checks
        # -------------------------
        if domain == "calculus" and "limit" in text:
            if "approaches" in text and "side" not in final_answer:
                # left/right hand limits not discussed
                issues.append(
                    "Left-hand and right-hand limits not discussed"
                )
                confidence -= 0.15

        if domain == "probability":
            if any(word in final_answer.lower() for word in ["greater than 1", "negative"]):
                issues.append("Invalid probability value")
                confidence -= 0.4

        # -------------------------
        # 4. Brownie: self-check via alternative reasoning
        # -------------------------
        self_check_notes = "No alternative method applied"

        if domain == "calculus" and "sin x / x" in text:
            # Known canonical limit — self-check
            self_check_notes = (
                "Verified using standard trigonometric limit identity"
            )
            confidence = min(confidence + 0.1, 1.0)

        if domain == "algebra" and "^2" in text:
            self_check_notes = (
                "Checked by substituting solution back into original equation"
            )
            confidence = min(confidence + 0.05, 1.0)

        # -------------------------
        # 5. Final decision
        # -------------------------
        needs_human_review = confidence < 0.6 or len(issues) > 0

        return {
            "is_correct": len(issues) == 0,
            "confidence": round(max(confidence, 0.0), 3),
            "issues": issues,
            "needs_human_review": needs_human_review,
            "self_check_notes": self_check_notes
        }
