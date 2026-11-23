# src/rotate.py
from src.stack import Stack


def rotate(a: Stack) -> str:
    # top element goes to the bottom (index last -> index 0)
    if a.last >= 1:
        tmp = a.ind[a.last]
        a.ind[1:a.last + 1] = a.ind[:a.last]
        a.ind[0] = tmp
    return f"r{a.name}"


def rotate_all(a: Stack, b: Stack) -> str:
    rotate(a)
    rotate(b)
    return "rr"


def rrotate(a: Stack) -> str:
    # bottom element goes to the top (index 0 -> index last)
    if a.last >= 1:
        tmp = a.ind[0]
        a.ind[:a.last] = a.ind[1:a.last + 1]
        a.ind[a.last] = tmp
    return f"rr{a.name}"


def rrotate_all(a: Stack, b: Stack) -> str:
    rrotate(a)
    rrotate(b)
    return "rrr"

def rotate_n(a: Stack, n: int) -> list[str]:
    """
    n > 0: n x rotate (top -> bottom); n < 0: |n| x rrotate (bottom -> top).
    """
    if n >= 0:
        return [rotate(a) for _ in range(n)]
    return [rrotate(a) for _ in range(-n)]