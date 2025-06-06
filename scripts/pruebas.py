import os

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

ruta_repo_alu = "/home/jorge/entregas_alumnos/jupyter-ou34io82o4hf"
print(ruta_repo_alu.split("jupyter-")[-1])

ruta = os.path.join(ruta_repo_alu, "fc-alumno", "peos.ipynb")
print(ruta.split("/")[-1])