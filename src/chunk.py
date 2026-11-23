from src.push import push
from src.rotate import rotate, rotate_n
from src.stack import Stack
from src.tools import INT_MAX


def chunk_size(n: int) -> int:
    """
    About 15 for 100 numbers, about 35 for 500 numbers.
    """
    if n <= 100:
        return n // 6
    return n // 14


def push_chunks(a: Stack, b: Stack, chunk: int) -> list[str]:
    """
    Phase 1: a -> b in a butterfly shape.

    - small  (rank <= pushed):         pb then rb -> goes to the bottom of b
    - medium (rank <= pushed + chunk): pb         -> stays on top of b
    - large:                           ra, look at the next one
    """
    ops = []
    pushed = 0
    while a.last >= 0:
        top = a.ind[a.last]
        if top <= pushed:
            ops.append(push(b, a))
            ops.append(rotate(b))
            pushed += 1
        elif top <= pushed + chunk:
            ops.append(push(b, a))
            pushed += 1
        else:
            ops.append(rotate(a))
    return ops


def pull_back_chunk(a: Stack, b: Stack) -> list[str]:
    """
    Phase 2: bring the max of b to its top (shortest way), push it onto a.
    """
    ops = []
    while b.last >= 0:
        idx = b.find_max(INT_MAX, b.get_ind)
        up = b.last - idx      # number of rb needed
        down = idx + 1         # number of rrb needed
        ops.extend(rotate_n(b, up if up <= down else -down))
        ops.append(push(a, b))
    return ops


def sort_chunk(a: Stack, b: Stack) -> list[str]:
    """
    Chunk / butterfly sort.
    """
    ops = push_chunks(a, b, chunk_size(a.last + 1))
    ops.extend(pull_back_chunk(a, b))
    return ops