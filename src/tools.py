# tools.py
INT_MIN = -2**31
INT_MAX = 2**31 - 1


def test_int(value_str: str) -> bool:
    """Returns True on error (mirrors C: non-zero means invalid)."""
    try:
        v = int(value_str)
    except ValueError:
        return True
    return not (INT_MIN <= v <= INT_MAX)
