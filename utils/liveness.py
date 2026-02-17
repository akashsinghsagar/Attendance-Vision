"""
liveness.py
Basic liveness detection stub (optional, can be extended).
"""
def is_live(frame, boxes):
    # Implement blink detection or other liveness checks here
    # For now, always return True for all faces
    return [True for _ in boxes]
