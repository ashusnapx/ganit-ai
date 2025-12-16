from typing import Dict, List


class ExplainerAgent:
    """
    Produces a student-friendly explanation
    using verified results and retrieved knowledge.
    """

    def explain(
        self,
        parsed_problem: Dict,
        solver_output: Dict,
        verifier_output: Dict,
        retrieved_chunks: List[Dict]
    ) -> Dict:

        # Safety gate: only explain verified answers
        if verifier_output.get("needs_human_review"):
            return {
                "explanation_steps": [
                    "The solution could not be confidently verified.",
                    "A human review is required before explanation."
                ],
                "final_answer": solver_output.get("final_answer", ""),
                "common_mistakes": []
            }

        domain = parsed_problem.get("topic", "unknown")
        problem_text = parsed_problem.get("problem_text", "")
        final_answer = solver_output.get("final_answer", "")

        steps = []
        mistakes = []

        # -------------------------
        # CALCULUS EXPLANATION
        # -------------------------
        if domain == "calculus" and "limit" in problem_text.lower():
            steps = [
                "First, observe the given limit expression.",
                "Check whether direct substitution leads to an indeterminate form.",
                "Apply standard trigonometric limit identities if applicable.",
                "Evaluate the simplified expression."
            ]

            mistakes = [
                "Directly substituting without checking if the form is indeterminate.",
                "Applying L'Hôpital’s Rule when it is not required.",
                "Ignoring the domain near the point of approach."
            ]

        # -------------------------
        # ALGEBRA EXPLANATION
        # -------------------------
        elif domain == "algebra":
            steps = [
                "Identify the type of algebraic equation given.",
                "Rearrange the equation into a standard form.",
                "Apply the appropriate solving method.",
                "Verify the obtained solution in the original equation."
            ]

            mistakes = [
                "Forgetting to check all possible solutions.",
                "Ignoring restrictions like division by zero.",
                "Missing the ± sign when taking square roots."
            ]

        # -------------------------
        # PROBABILITY EXPLANATION
        # -------------------------
        elif domain == "probability":
            steps = [
                "Clearly define the sample space.",
                "Count the number of favorable outcomes.",
                "Apply the relevant probability formula.",
                "Ensure the final probability lies between 0 and 1."
            ]

            mistakes = [
                "Assuming events are independent without justification.",
                "Counting the same outcome more than once.",
                "Forgetting to divide by total possible outcomes."
            ]

        # -------------------------
        # LINEAR ALGEBRA EXPLANATION
        # -------------------------
        elif domain == "linear_algebra":
            steps = [
                "Identify the matrix or vector operation involved.",
                "Check dimensional compatibility.",
                "Apply the appropriate linear algebra formula.",
                "Verify results using determinant or substitution if applicable."
            ]

            mistakes = [
                "Attempting to invert a matrix with zero determinant.",
                "Confusing matrix multiplication with element-wise multiplication.",
                "Ignoring matrix dimensions."
            ]

        # -------------------------
        # FALLBACK EXPLANATION
        # -------------------------
        else:
            steps = [
                "Understand the problem statement carefully.",
                "Apply known mathematical principles.",
                "Verify the final result logically."
            ]

            mistakes = [
                "Jumping to conclusions without justification.",
                "Applying formulas without checking conditions."
            ]

        return {
            "explanation_steps": steps,
            "final_answer": final_answer,
            "common_mistakes": mistakes
        }
