#!/usr/bin/env python3

'''
Módulo en el que adaptamos las funciones básicas de correct_exam para poder aplicar lo mismo a la corrección de repositorios y entregas de alumnos, generando los mismos CSV finales.
'''

from collections import defaultdict
import subprocess
import re
import os


# CONSTANTE - diccionario con cada bloque a estudiar y los ficheros que contiene cada uno
IMPORTANT_FILES = {
			"1": "practica1-introshell-ejercicios-etiquetados2.ipynb",
			"2": "practica2-introgit-ejercicios-etiquetados2.ipynb",
			"3": "practica3-okteta-enteros-reales-ejercicios-etiquetados2.ipynb", 
			"4": "practica4a-compilacion-ejecucion-ejercicios-etiquetados2.ipynb", 
			"5a": "practica5a-ficheros-ejercicios-etiquetados2.ipynb", 
			"5b": "practica5b-busquedas-ejercicios-etiquetados2.ipynb", 
			"7a": "practica7a-procesos-ejercicios-etiquetados2.ipynb", 
			"7b": "practica7b-tuberias-ejercicios-etiquetados2.ipynb"
}


# Funciones auxiliares "tontas" para la lectura 
def str_to_roman_cutrisimo(num: str) -> str:
	if "1" in num:
		return "I"
	elif "2" in num:
		return "II"
	elif "3" in num:
		return "III"
	elif "4" in num:
		return "IV"
	elif "5" in num:
		return "V"
	elif "6" in num:
		return "VI"
	else:
		return "VII"
	
def extract_block_from_str(num: str) -> int|None:
	block = None

	for letra in num:
		try:
			block = int(letra)
			return block
		except ValueError:
			continue

def execute_diff(ruta_repo_alu: str, ruta_sol: str, important_files: dict[str, str] = IMPORTANT_FILES) -> defaultdict|None:
	"""
	Dado el repositorio de un alumno, lee las respuestas a cada uno de los ejercicios de cada bloque junto con las del notebook con la solución.

	Parámetros:
		- ruta_repo_alu (str): ruta a la carpeta que contiene el repositorio del alumno con los directorios correspondientes a cada bloque de prácticas y, dentro, los notebooks con sus entregas.
		- ruta_sol (str): ruta a la carpeta con los ejercicios de las prácticas resueltos
		- important_files (dict): diccionario en el que se indica el bloque de cada notebook a corregir, y el nombre del fichero en el que se tiene que encontrar.

	Devuelve:
		- Diccionario con la estructura --> {N: {M: [respuesta_alumno, solution]}}, donde N es el número de bloque, y M es el número de la pregunta de dicho bloque. Si el bloque tiene una pregunta 0, esta clave contendrá una lista de preguntas en blanco en el bloque, en formato str.
	"""
	dict_bloques = defaultdict(lambda: defaultdict(list))

	for bloque, archivo in important_files.items():
		codigo_bash_2 = rf"""
		diff -u {ruta_repo_alu}/fc-alumno/P{str(extract_block_from_str(bloque))}/{archivo} {ruta_sol}/P{str(extract_block_from_str(bloque))}/{archivo} | grep -E -A4 "#\s*{str_to_roman_cutrisimo(bloque)}";
		"""

		# Comprobación de existencia de práctica en el repositorio del alumno
		if not os.path.exists(os.path.join(ruta_repo_alu, "fc-alumno", f"P{str(extract_block_from_str(bloque))}", archivo)):
			print(f"El alumno {ruta_repo_alu.split('jupyter-')[-1]} no ha entregado la práctica {archivo}")
			continue
		
		# Ejecución del diff
		resultado = subprocess.run(codigo_bash_2, shell=True, capture_output=True, text=True)
		if resultado.stderr:
			print("Lectura de datos errónea: ")
			print(resultado.stderr)
			return None
		salida = resultado.stdout
		print(salida)
		
	'''
		roman = int_to_roman_cutrisimo(bloque)
		patron = rf'\"#\s*{roman}\.\d+\\n\",\n- *\"(.*?)\",*\n'
		patron_sol = r'\+.*?"(.*?)\s+#@solution@\"\n'
		# Para preguntas en blanco, detectamos el número de la pregunta no contestada dentro del bloque
		patron_blank = rf'\"#\s*{roman}\.\d+\\n\"\n\+ *\"#\s*{roman}\.(.*?)\\n\",\n'
		comandos = re.findall(patron, salida)
		comandos_sol = re.findall(patron_sol, salida)
		comandos_blank = re.findall(patron_blank, salida)
		comandos_out: list[int] = []  # lista de preguntas sin contestar en el bloque

		# Caso extraño (en examen-suspenso hay una pregunta donde la solución no aparece en el diff, no sé por qué):
		lista_bloques = salida.split('--\n')
		for monton in lista_bloques:
			if 'Comprobación' in monton:
				pass
			elif 'solution' not in monton:
				numero = re.findall(rf'\"#\s*{roman}\.(.*?)\\n\",\n', monton)
				comandos_out.append(int(numero[0]))

		# Preguntas ignoradas:
		for pregunta in comandos_out:
			comandos[pregunta-1] = None
			comandos_sol.insert(pregunta-1, None)

		# Ha detectado preguntas en blanco
		if len(comandos_blank) > 0:
			dict_bloques[bloque][0] = comandos_blank       
			
			# Meter None en el hueco donde debería ir esa pregunta
			for preg_en_blanco in comandos_blank:
				num = int(preg_en_blanco)
				comandos.insert(num-1, None)
				comandos_sol.insert(num-1, None)

		# Rellenar el diccionario en el bloque que estemos estudiando, metiendo la respuesta del alumno y la correcta en ese orden en una lista dentro de la clave de la pregunta
		for i in range(1, (len(comandos))+1):
			dict_bloques[bloque][i].append(comandos[i-1].strip('\\n').strip() if comandos[i-1] is not None else comandos[i-1])
			dict_bloques[bloque][i].append(comandos_sol[i-1].strip('\\n').strip() if comandos_sol[i-1] is not None else comandos_sol[i-1])
		
		# Meter preguntas ignoradas como en blanco (sus números)
		dict_bloques[bloque][0] += comandos_out

	return dict_bloques
	'''

if __name__ == "__main__":
	ruta_repo_alu = "/home/jorge/git_reps/bash-autocorrector/entregas_alumnos/jupyter-7fEZvEiEPC"
	ruta_sol = "/home/jorge/git_reps/bash-autocorrector/practicas"

	execute_diff(ruta_repo_alu, ruta_sol)