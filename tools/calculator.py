def safe_calculate(expression: str):
    """
    Safely evaluate basic mathematical expressions.
    """
    allowed_chars = "0123456789+-*/(). "
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Unsafe expression")

    return eval(expression)
