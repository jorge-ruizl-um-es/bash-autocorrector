import nbformat


def etiquetar_practica(bloque:str, fichero:str, ruta_base:str):
	'''
	Función para, dado un bloque, el nombre de un fichero, y una ruta base, etiquetar el fichero en dicho bloque tanto en las soluciones como en los repositorios de alumnos. 
	
	El fichero tendrá que ser un notebook de Jupyter, y el etiquetado consistirá en tomar cada repositorio dentro de una carpeta "entregas_alumnos" en el directorio base, y añadir la etiqueta de la forma "#{bloque}.{ejercicio}" a cada ejercicio (celda de código del notebook que haya que rellenar, con la solución y la etiqueta "#@solution@" en el fichero de solución).
	
	Se buscará la solución en el directorio "practicas" dentro del directorio base".
	'''


	# Construir las rutas a partir de ruta_base (puede cambiar en función de la estructura de directorios personal)

	# Cargar los ficheros
	with open(ruta_alu, 'r', encoding='utf-8') as f:
		alumno_notebook = nbformat.read(f, as_version=4)

	with open(ruta_sol, 'r', encoding='utf-8') as f:
		soluciones_notebook = nbformat.read(f, as_version=4)
          
	
	# Extraer las celdas de cada notebook
	alumno_cells = alumno_notebook['cells']
	soluciones_cells = soluciones_notebook['cells']

	# Revisar las celdas de las soluciones para etiquetar
	solution_indices = []
	for i, cell in enumerate(soluciones_cells):
		if '#@solution@' in ''.join(cell['source'].splitlines()):
			solution_indices.append(i)

	# Añadir etiquetas a las celdas
	for i, solution_index in enumerate(solution_indices, 1):
		# Etiquetar celdas en el notebook de soluciones
		soluciones_cells[solution_index]['source'] = f"#I.{i}\n" + soluciones_cells[solution_index]['source']
		
		# Buscar la respuesta correspondiente en el notebook del alumno
		# Asumir que las celdas corresponden por su orden
		if solution_index < len(alumno_cells):
			alumno_cells[solution_index]['source'] = f"#I.{i}\n" + alumno_cells[solution_index]['source']


	# Guardar los notebooks con las etiquetas añadidas
	alumno_notebook['cells'] = alumno_cells
	soluciones_notebook['cells'] = soluciones_cells

	alumno_notebook_path = '/home/jorge/git_reps/bash-autocorrector/entregas_alumnos/jupyter-7fEZvEiEPC/fc-alumno/P1/practica1-introshell-ejercicios-etiquetados.ipynb'
	soluciones_notebook_path = '/home/jorge/git_reps/bash-autocorrector/practicas/P1/practica1-introshell-ejercicios-etiquetados.ipynb'

	with open(alumno_notebook_path, 'w', encoding='utf-8') as f:
		nbformat.write(alumno_notebook, f)

	with open(soluciones_notebook_path, 'w', encoding='utf-8') as f:
		nbformat.write(soluciones_notebook, f)

	print(f"Etiquetado fichero {ruta_alu.split('/')[-1]}")


if __name__ == "__main__":

	# Lista con las prácticas a procesar (los nombres tendrán que coincidir tanto en los alumnos como en las soluciones)
	files = [
			"practica1-introshell-ejercicios.ipynb",
			"practica2-introgit-ejercicios.ipynb",
			"practica3-okteta-enteros-reales-ejercicios.ipynb", 
			"practica4a-compilacion-ejecucion-ejercicios.ipynb", 
			"practica5a-ficheros-ejercicios.ipynb", 
			"practica5b-busquedas-ejercicios.ipynb", 
			"practica6a-cache-boletin.ipynb", 
			"practica7a-procesos-ejercicios.ipynb",
			"practica7b-tuberias-ejercicios.ipynb"
		]

	# Rutas
	ruta_base = '/home/jorge/git_reps/bash-autocorrector/'