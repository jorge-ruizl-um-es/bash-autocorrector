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
			solution_cells_info = []
			for i, cell in enumerate(soluciones_cells):
				if cell['cell_type'] == 'code' and '#@solution@' in ''.join(cell['source'].splitlines()):
					# Obtener el código sin la etiqueta #@solution@
					source_lines = cell['source'].splitlines()
					clean_source = '\n'.join([line for line in source_lines if '#@solution@' not in line])
					first_line = source_lines[0].replace('#@solution@', '').strip()
					solution_cells_info.append({
						'sol_index': i,
						'first_line': first_line,
						'clean_source': clean_source
					})

			# Añadir etiquetas a las celdas
			map_int_to_roman: dict[int, str] = {1:"I", 2:"II", 3:"III", 4:"IV", 5:"V", 6:"VI", 7:"VII", 8:"VIII", 9:"IX"}
			num_etiqueta:str = map_int_to_roman[bloque]

			# Para cada celda de solución, buscar la correspondiente en el notebook del alumno
			for i, sol_cell_info in enumerate(solution_cells_info, 1):
				solution_index = sol_cell_info['sol_index']
				tag = f"#{num_etiqueta}.{i}"

				# Etiquetar celdas en el notebook de soluciones
				soluciones_cells[solution_index]['source'] = f"{tag}\n" + soluciones_cells[solution_index]['source']
				
				# Buscar celda correspondiente en el notebook del alumno
				found = False
				for j, alumno_cell in enumerate(alumno_cells):
					if alumno_cell['cell_type'] != 'code':
						continue
						
					# Comprobar si ya está etiquetada
					if alumno_cell['source'].startswith(tag):
						found = True
						break
						
					# Obtener primera línea del alumno
					alumno_source_lines = alumno_cell['source'].splitlines()
					if not alumno_source_lines:
						continue
					alumno_first_line = alumno_source_lines[0].strip()
					
					# Comparar con la primera línea de la solución (sin etiquetas)
					if alumno_first_line == sol_cell_info['first_line']:
						# Etiquetar celda encontrada
						alumno_cells[j]['source'] = f"{tag}\n{alumno_cell['source']}"
						found = True
						break
				
				# Si no se encontró por primera línea, buscar por contenido similar
				if not found:
					for j, alumno_cell in enumerate(alumno_cells):
						if alumno_cell['cell_type'] != 'code':
							continue
							
						# Comprobar si el código del alumno comienza como el de la solución
						alumno_source = alumno_cell['source'].strip()
						if alumno_source.startswith(sol_cell_info['clean_source'].split('\n')[0]):
							alumno_cells[j]['source'] = f"{tag}\n{alumno_cell['source']}"
							found = True
							break
				
				if not found:
					print(f"No se encontró celda correspondiente para {tag} en {ruta_alu_completa}")


			# Guardar los notebooks con las etiquetas añadidas
			alumno_notebook['cells'] = alumno_cells
			soluciones_notebook['cells'] = soluciones_cells

			# Construcción de nuevas rutas
			alumno_notebook_path = ruta_alu_completa[:-6] + "-etiquetados2" + ruta_alu_completa[-6:]
			soluciones_notebook_path = ruta_sol[:-6] + "-etiquetados2" + ruta_sol[-6:]

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
