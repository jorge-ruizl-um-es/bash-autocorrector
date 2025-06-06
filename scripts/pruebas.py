def extract_block_from_str(num: str) -> int|None:
	block = None

	for letra in num:
		try:
			block = int(letra)
			return block
		except ValueError:
			continue

num = "sadasddvs7a"

print(extract_block_from_str(num))