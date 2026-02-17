"""
input_validation.py
Basic input validation utilities.
"""
def validate_text(text, min_len=1, max_len=100):
    if not isinstance(text, str):
        return False
    text = text.strip()
    return min_len <= len(text) <= max_len and text.isprintable()
