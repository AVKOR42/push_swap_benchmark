# src/push.py
from src.stack import Stack


def push(a: Stack, b: Stack) -> str:
    """Move top of b onto a."""
    if b.last >= 0:
        a.last += 1
        a.ind[a.last] = b.ind[b.last]
        b.last -= 1
    return f"p{a.name}"