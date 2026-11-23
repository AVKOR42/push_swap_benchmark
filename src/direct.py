# src/direct.py
from src.push import push
from src.radix import pull_back
from src.rotate import rotate, rotate_n, rrotate
from src.stack import Stack
from src.swap import swap
from src.tools import INT_MIN


def sort3(a: Stack) -> list[str]:
	"""Sort up to 3 elements; the top (index last) must hold the smallest rank."""
	ops = []
	if a.last == 1:
		if a.ind[1] > a.ind[0]:
			ops.append(swap(a))
		return ops
	if a.last != 2:
		return ops
	x, y, z = a.ind[2], a.ind[1], a.ind[0]	  # top, middle, bottom
	if x < y < z:
		pass
	elif y < x < z:							 # 1 0 2
		ops.append(swap(a))
	elif x > y > z:							 # 2 1 0
		ops.append(swap(a))
		ops.append(rrotate(a))
	elif x > z > y:							 # 2 0 1
		ops.append(rotate(a))
	elif x < z < y:							 # 0 2 1
		ops.append(swap(a))
		ops.append(rotate(a))
	else:									   # 1 2 0
		ops.append(rrotate(a))
	return ops


def sort_direct(a: Stack, b: Stack) -> list[str]:
	"""Selection sort: push the min to b each time, then pull everything back."""
	ops = []
	while a.last > 2:
		idx = a.find_min(INT_MIN, a.get_ind)
		up = a.last - idx	   # number of ra to bring it to the top
		down = idx + 1		  # number of rra to bring it to the top
		if down > up:
			if up:
				# stop one short, then sa puts it on top
				ops.extend(rotate_n(a, up - 1))
				ops.append(swap(a))
		else:
			ops.extend(rotate_n(a, -down))
		ops.append(push(b, a))
	ops.extend(sort3(a))
	ops.extend(pull_back(a, b))
	return ops
