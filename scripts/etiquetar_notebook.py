import nbformat

# Cargar los dos notebooks (modificar rutas)
file_alumno_path = '/home/jorge/git_reps/bash-autocorrector/entregas_alumnos/jupyter-7fEZvEiEPC/fc-alumno/P1/practica1-introshell-ejercicios.ipynb'
file_soluciones_path = '/home/jorge/git_reps/bash-autocorrector/practicas/P1/practica1-introshell-ejercicios.ipynb'

with open(file_alumno_path, 'r', encoding='utf-8') as f:
    alumno_notebook = nbformat.read(f, as_version=4)

with open(file_soluciones_path, 'r', encoding='utf-8') as f:
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

alumno_notebook_path, soluciones_notebook_path
