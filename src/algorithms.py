# src/algorithms.py
from collections.abc import Callable

from src.direct import sort_direct
from src.chunk import sort_chunk
from src.turk import sort_turk
from src.radix import sort_radix
from src.stack import Stack

Algorithm = Callable[[Stack, Stack], list[str]]

# Add direct / chunk / turk here later: name -> function(a, b) -> list of ops

ALGORITHMS: dict[str, Algorithm] = {
	"radix": sort_radix,
	"chunk": sort_chunk,
	"turk": sort_turk,
	"direct": sort_direct,
}