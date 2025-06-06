#!/usr/bin/env python3

import nbformat
import os
import re


def etiquetar_practica(bloque:int, fichero:str, ruta_base:str):
	'''
	Función para, dado un bloque, el nombre de un fichero, y una ruta base, etiquetar el fichero en dicho bloque tanto en las soluciones como en los repositorios de alumnos. 
	
	El fichero tendrá que ser un notebook de Jupyter, y el etiquetado consistirá en tomar cada repositorio dentro de una carpeta "entregas_alumnos" en el directorio base, y añadir la etiqueta de la forma "#{bloque}.{ejercicio}" a cada ejercicio (celda de código del notebook que haya que rellenar, con la solución y la etiqueta "#@solution@" en el fichero de solución).
	
	Se buscará la solución en el directorio "practicas" dentro del directorio base".
	'''

	# Construir las rutas a partir de ruta_base (puede cambiar en función de la estructura de directorios personal)
	ruta_alu = ruta_base+"entregas_alumnos/"
	ruta_sol = ruta_base+f"practicas/P{str(bloque)}/{fichero}"

	# Recorrer todos los repositorios que haya en ruta_alu
	for user_dir in os.listdir(ruta_alu):
        # construir ruta completa con la carpeta de usuario
		user_path = os.path.join(ruta_alu, user_dir)

        # comprobar que es un directorio que empieza por "jupyter-" 
		if os.path.isdir(user_path) and user_dir.startswith("jupyter-"):
			ruta_alu_completa = os.path.join(user_path, "fc-alumno", f"P{str(bloque)}", fichero)

			# Comprobar que la ruta al notebook existe
			if not os.path.exists(ruta_alu_completa):
				print(f"No se encontró el notebook con ruta {ruta_alu_completa}")
				continue

			# Cargar los ficheros
			with open(ruta_alu_completa, 'r', encoding='utf-8') as f:
				alumno_notebook = nbformat.read(f, as_version=4)

			with open(ruta_sol, 'r', encoding='utf-8') as f:
				soluciones_notebook = nbformat.read(f, as_version=4)
				
			
			# PROCESAMIENTO
			# Extraer las celdas de cada notebook
			alumno_cells = alumno_notebook['cells']
			soluciones_cells = soluciones_notebook['cells']

			# Revisar las celdas de las soluciones para etiquetar
			solution_indices = []
			for i, cell in enumerate(soluciones_cells):
				if '#@solution@' in ''.join(cell['source'].splitlines()):
					solution_indices.append(i)

			# Añadir etiquetas a las celdas
			map_int_to_roman: dict[int, str] = {1:"I", 2:"II", 3:"III", 4:"IV", 5:"V", 6:"VI", 7:"VII", 8:"VIII", 9:"IX"}
			num_etiqueta:str = map_int_to_roman[bloque]

			for i, solution_index in enumerate(solution_indices, 1):
				# Etiquetar celdas en el notebook de soluciones
				soluciones_cells[solution_index]['source'] = f"#{num_etiqueta}.{i}\n" + soluciones_cells[solution_index]['source']
				
				# Buscar la respuesta correspondiente en el notebook del alumno
				# Asumir que las celdas corresponden por su orden
				if solution_index < len(alumno_cells):
					alumno_cells[solution_index]['source'] = f"#{num_etiqueta}.{i}\n" + alumno_cells[solution_index]['source']


			# Guardar los notebooks con las etiquetas añadidas
			alumno_notebook['cells'] = alumno_cells
			soluciones_notebook['cells'] = soluciones_cells

			# Construcción de nuevas rutas
			alumno_notebook_path = ruta_alu_completa[:-6] + "-etiquetados" + ruta_alu_completa[-6:]
			soluciones_notebook_path = ruta_sol[:-6] + "-etiquetados" + ruta_sol[-6:]

			with open(alumno_notebook_path, 'w', encoding='utf-8') as f:
				nbformat.write(alumno_notebook, f)

			with open(soluciones_notebook_path, 'w', encoding='utf-8') as f:
				nbformat.write(soluciones_notebook, f)

			print(f"Etiquetado fichero {ruta_alu_completa.split('/')[-1]}")


if __name__ == "__main__":

	# Lista con las prácticas a procesar (los nombres tendrán que coincidir tanto en los alumnos como en las soluciones)
	files = [
			"practica1-introshell-ejercicios.ipynb",
			"practica2-introgit-ejercicios.ipynb",
			"practica3-okteta-enteros-reales-ejercicios.ipynb", 
			"practica4a-compilacion-ejecucion-ejercicios.ipynb", 
			"practica5a-ficheros-ejercicios.ipynb", 
			"practica5b-busquedas-ejercicios.ipynb", 
			"practica7a-procesos-ejercicios.ipynb",
			"practica7b-tuberias-ejercicios.ipynb"
		]

	# Rutas
	ruta_base = '/home/jorge/git_reps/bash-autocorrector/'

	# Llamada a la función para todos los bloques
	for file in files:
		bloque = int(re.findall(r'practica(\d+)', file)[0])
		etiquetar_practica(bloque, file, ruta_base)
