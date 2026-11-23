# stack.py
from src.tools import INT_MIN, test_int


class Stack:
	def __init__(self, name: str, size: int):
		self.name = name
		self.size = size
		self.last = -1
		self.data = [0] * size
		self.ind = [0] * size

	def fill_stack(self, av: list, size: int) -> int:
		for i in range(size):
			if test_int(av[i]):
				return 1
			self.last = i
			self.data[self.last] = int(av[i])
		if self.is_duplicated():
			return 1
		self.make_ind()
		return 0

	def is_duplicated(self) -> bool:
		return len(set(self.data[:self.last + 1])) != self.last + 1

	def is_sorted(self) -> bool:
		"""Top of the stack (index last) must hold the smallest rank."""
		return self.ind == sorted(self.ind, reverse=True)

	def make_ind(self) -> None:
		ref = INT_MIN
		for i in range(self.size):
			idx = self.find_min(ref, self.get_data)
			ref = self.data[idx]
			self.ind[idx] = i

	def find_min(self, ref, getter):
		"""
		Index of the smallest value strictly greater than ref (ref=None -> any).
		"""
		best = -1
		values = getter()
		for i in range(self.last + 1):
			v = values[i]
			if (v > ref) and (best == -1 or v < values[best]):
				best = i
		return best

	def find_max(self, ref, getter):
		"""
		Index of the largest value strictly smaller than ref, among live elements.
		"""
		best = -1
		values = getter()
		for i in range(self.last + 1):
			v = values[i]
			if v < ref and (best == -1 or v > values[best]):
				best = i
		return best

	def get_data(self) -> list:
		return self.data

	def get_ind(self) -> list:
		return self.ind