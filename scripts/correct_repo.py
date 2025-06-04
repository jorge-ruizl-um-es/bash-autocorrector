'''
Módulo en el que adaptamos las funciones básicas de correct_exam para poder aplicar lo mismo a la corrección de repositorios y entregas de alumnos, generando los mismos CSV finales.
'''

from collections import defaultdict
import subprocess
import re

NUM_BLOQUES: int = 7

def int_to_roman_cutrisimo(num: int) -> str:
	if num == 1:
		return "I"
	elif num == 2:
		return "II"
	elif num == 3:
		return "III"
	elif num == 4:
		return "IV"
	else:
		return "V"

def execute_diff(ruta_exam: str, ruta_sol: str) -> defaultdict|None:
	"""
	Dado el examen de un alumno (NUM_BLOQUES bloques), lee las respuestas junto con las del notebook con la solución.

	Parámetros:
		- ruta_exam (str): ruta a la carpeta que contiene el examen del alumno a corregir
		- ruta_sol (str): ruta a la carpeta con el examen resuelto

	Devuelve:
		- Diccionario con la estructura --> {N: {M: [respuesta_alumno, solution]}}, donde N es el número de bloque, y M es el número de la pregunta de dicho bloque. Si el bloque tiene una pregunta 0, esta clave contendrá una lista de preguntas en blanco en el bloque, en formato str.
	"""
	dict_bloques = defaultdict(lambda: defaultdict(list))

	for bloque in range(1, NUM_BLOQUES+1):
		codigo_bash_2 = rf"""
		diff -u {ruta_exam}/examen-fc-bloque{str(bloque)}.ipynb {ruta_sol}/examen-fc-bloque{str(bloque)}.ipynb | grep -E -A4 "#\s*I|#\s*V";
		"""

		resultado = subprocess.run(codigo_bash_2, shell=True, capture_output=True, text=True)
		if resultado.stderr:
			print("Lectura de datos errónea: ")
			print(resultado.stderr)
			return None
		salida = resultado.stdout
		#print(salida)

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
	
	'''
	# DEBUG
	for bloque in range(1,NUM_BLOQUES+1):
		for (preg, lista) in dict_bloques[bloque].items():
			print(f"{bloque}.{preg}: {lista}")
	'''

	return dict_bloques

if __name__ == "__main__":
	