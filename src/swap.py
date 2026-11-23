# src/swap.py
from src.stack import Stack


def swap(a: Stack) -> str:
    if a.last >= 1:
        a.ind[a.last], a.ind[a.last - 1] = a.ind[a.last - 1], a.ind[a.last]
    return f"s{a.name}"


def ss(a: Stack, b: Stack) -> str:
    swap(a)
    swap(b)
    return "ss"