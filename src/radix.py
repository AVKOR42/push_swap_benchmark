# src/radix.py
from src.push import push
from src.rotate import rotate
from src.stack import Stack


def pull_back(a: Stack, b: Stack) -> list[str]:
    ops = []
    while b.last >= 0:
        ops.append(push(a, b))
    return ops


def sort_radix(a: Stack, b: Stack) -> list[str]:
    ops = []
    size = a.size
    bit = 0
    while size:
        for _ in range(a.size):
            if (a.ind[a.last] >> bit) & 1:
                ops.append(rotate(a))
            else:
                ops.append(push(b, a))
        ops.extend(pull_back(a, b))
        size //= 2
        bit += 1
    return ops