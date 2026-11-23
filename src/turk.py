# src/turk.py
from src.direct import sort3
from src.push import push
from src.rotate import rotate, rotate_all, rotate_n, rrotate_all
from src.stack import Stack
from src.tools import INT_MAX, INT_MIN


def target_in_a(a: Stack, ref: int) -> int:
    """
    Index in a of the smallest rank greater than ref (wraps to the minimum).
    """
    best = a.find_min(ref, a.get_ind)
    if best != -1:
        return best
    return a.find_min(INT_MIN, a.get_ind)


def target_in_b(b: Stack, ref: int) -> int:
    """
    Index in b of the largest rank smaller than ref (wraps to the maximum).
    """
    best = b.find_max(ref, b.get_ind)
    if best != -1:
        return best
    return b.find_max(INT_MAX, b.get_ind)


def calc_rot_cost(a: Stack, idx: int) -> int:
    """
    > 0: that many rotate; < 0: that many rrotate (shortest way to the top).
    """
    up = a.last - idx
    down = idx + 1
    return up if up <= down else -down


def estimate_rotations(cost_a: int, cost_b: int) -> int:
    if cost_a * cost_b < 0:                 # opposite directions: no rr/rrr sharing
        return abs(cost_a) + abs(cost_b)
    return max(abs(cost_a), abs(cost_b))    # same direction: rr/rrr shared


def find_cheapest(a: Stack, b: Stack) -> tuple[int, int]:
    best = INT_MAX
    best_a = best_b = 0
    for i in range(a.last + 1):
        cost_a = calc_rot_cost(a, i)
        cost_b = calc_rot_cost(b, target_in_b(b, a.ind[i]))
        tmp = estimate_rotations(cost_a, cost_b)
        if tmp < best:
            best, best_a, best_b = tmp, cost_a, cost_b
    return best_a, best_b


def exec_rotations(a: Stack, b: Stack, cost_a: int, cost_b: int) -> list[str]:
    ops = []
    while cost_a > 0 and cost_b > 0:
        ops.append(rotate_all(a, b))
        cost_a -= 1
        cost_b -= 1
    while cost_a < 0 and cost_b < 0:
        ops.append(rrotate_all(a, b))
        cost_a += 1
        cost_b += 1
    ops.extend(rotate_n(a, cost_a))
    ops.extend(rotate_n(b, cost_b))
    return ops


def pull_back_turk(a: Stack, b: Stack) -> list[str]:
    ops = []
    while b.last >= 0:
        cost = calc_rot_cost(a, target_in_a(a, b.ind[b.last]))
        ops.extend(rotate_n(a, cost))
        ops.append(push(a, b))
    # final alignment: smallest rank on top
    cost = calc_rot_cost(a, a.find_min(INT_MIN, a.get_ind))
    ops.extend(rotate_n(a, cost))
    return ops


def sort_turk(a: Stack, b: Stack) -> list[str]:
    """
    Turk algorithm: always push the element with the cheapest combined rotation cost.
    """
    if a.last < 3:                          # n <= 3: nothing to optimize
        return sort3(a)
    ops = [push(b, a), push(b, a)]
    while a.last > 2:
        cost_a, cost_b = find_cheapest(a, b)
        ops.extend(exec_rotations(a, b, cost_a, cost_b))
        ops.append(push(b, a))
    ops.extend(sort3(a))
    ops.extend(pull_back_turk(a, b))
    return ops
