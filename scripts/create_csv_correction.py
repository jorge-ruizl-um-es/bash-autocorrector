#!/usr/bin/env python3

from correct_exam import CommandStatus, execute_diff, compare_commands, NUM_BLOQUES
from scores_by_block import count_by_blocks, extraer_bloques_solutions, map_alucommand_to_answer
import os
import shutil
import csv

'''
NOTA: Cada examen en DIR_EXAMS será un directorio: "examen-{NOMBRE}". "NOMBRE", será lo que identifique al alumno en los csv con los resultados
'''

# CAMBIAR CONSTANTES CON LAS RUTAS/NOMBRES DE DIRECTORIO DESEADOS
RUTA_SOL = "examen-resuelto-2024"
DIR_EXAMS = "dir_exams"
OUTPUT_FOLDER = "../../../pruebas-script-correccion/outputs"

# Diccionario en el que cada clave será el id (nombre) del alumno, y el valor será el diccionario en el que se indica, en cada bloque, cuántas preguntas de cada tipo tiene
dict_alumnos = {}
dict_alumnos_por_bloques = {}  # lo mismo, pero con la cuenta separada por bloques
dict_alumnos_completo = {}   # mapea cada respuesta correcta con la respuesta ofrecida por el alumno

# Generar diccionario solo con las correcciones de cada pregunta, obtenidas del examen en RUTA_SOL
dict_respuestas = extraer_bloques_solutions(RUTA_SOL)

# Recorrer los exámenes de los alumnos para ir generando las correcciones (tanto en resumen en dict_alumnos, como en detalleen dict_alumnos_por_bloques)
for exam_dir in os.listdir(DIR_EXAMS):
    # Esta condición es para probar los exámenes viejos, para que no tenga en cuenta los de este año (el examen solucionado es distinto)
    if 'G1' in exam_dir:
        id_alu = exam_dir.split("-", 1)[1]

        # Obtener diccionario con las respuestas del alumno a cada pregunta y las respuestas correctas
        try:
            responses = execute_diff(DIR_EXAMS+'/'+exam_dir, RUTA_SOL)
        except IndexError:
            print(f"Error al ejecutar el diff: {exam_dir}")
            pass

        # Obtener conteo del estado de las respuestas del alumno
        try:
            scores, dict_completo = compare_commands(responses, detail=True)
            dict_alumnos[id_alu] = scores
        except IndexError:
            print(f"Error al realizar la corrección: {exam_dir}")
            break

        # Guardar también el diccionario en el que tenemos la respuesta del alumno asociada a su respuesta correcta (o una cadena vacía si no ha respondido esa pregunta)
        dict_alumnos_completo[id_alu] = map_alucommand_to_answer(dict_completo, dict_respuestas)

        # Generar la cuenta por bloques a partir del dict_completo obtenido, para cada alumno (función count_by_blocks del módulo scores_by_block)
        dict_alumnos_por_bloques[id_alu] = count_by_blocks(dict_completo)


# Obtenemos una lista de los valores que puede tomar el comando en CommandStatus
estados = [str(status) for status in CommandStatus]

# Crear carpeta de salida del programa
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)

os.mkdir(OUTPUT_FOLDER)


# -----------------------------------------------------------------------------------------
# CREACION DE CSV's
# -----------------------------------------------------------------------------------------

# Crear CSV con el conteo general por alumno
with open(f"{OUTPUT_FOLDER}/conteo-general.csv", mode='w', newline="") as file:
    writer = csv.writer(file)

    # Escribir la cabecera
    writer.writerow(["Alumno"] + estados)

    # Escribir las filas
    for name, counts in dict_alumnos.items():
        row = [name] + [counts.get(status, 0) for status in CommandStatus]
        writer.writerow(row)

# Crear CSV con el conteo por bloques
with open(f"{OUTPUT_FOLDER}/conteo-por-bloques.csv", mode='w', newline="") as file:
    writer = csv.writer(file)

    # Construir cabecera de la forma [B_i-estado]
    lista_header = []
    for bloque in range(1, NUM_BLOQUES+1):
        for estado in estados:
            lista_header.append(f"B{bloque}-{str(estado)}")
    
    # Escribir la cabecera
    writer.writerow(["Alumno"] + lista_header)

    # Escribir las filas
    for name, diccionario_bloques in dict_alumnos_por_bloques.items():
        row = [name]
        for bloque, diccionario_estados in diccionario_bloques.items():
            row += [diccionario_estados.get(status,0) for status in CommandStatus]
        
        writer.writerow(row)

# Crear CSV's con el análisis detallado de los exámenes por bloques (mapeo de cada respuesta del alumno con la respuesta correcta)

# Crear el directorio donde los vamos a volcar:
os.mkdir(f"{OUTPUT_FOLDER}/detail")

for bloque in dict_respuestas.keys():
    with open(f"{OUTPUT_FOLDER}/detail/descripcion-respuestas-bloque{bloque}.csv", mode='w', newline="") as file:
        # En el writer, especificamos que queremos que se entrecomillen los campos que se escriban, para que las comas de los comandos no sirvan de separación
        writer = csv.writer(file, quotechar='"', quoting=csv.QUOTE_ALL)

        # Construir cabecera (cada columna será una respuesta almacenada en dict_respuestas[bloque])
        lista_header = []
        for respuesta in dict_respuestas[bloque].values():
            lista_header.append(respuesta)

        # Escribir la cabecera
        writer.writerow(["Alumno"] + lista_header)

        # Escribir las filas (se supone que, tanto en dict_respuestas, como en dict_completo, las preguntas van en el mismo orden)
        for name, diccionario_bloques in dict_alumnos_completo.items():
            row = [name]
            for pregunta in lista_header:
                row += [dict_alumnos_completo[name][bloque][pregunta][0]]

            writer.writerow(row)

# Crear CSV's con la lista detallada de estados (correcciones automáticas) de cada respuesta del alumno por bloques

# Crear el directorio donde los vamos a volcar:
os.mkdir(f"{OUTPUT_FOLDER}/detail/results")

for bloque in dict_respuestas.keys():
    with open(f"{OUTPUT_FOLDER}/detail/results/descripcion-resultados-bloque{bloque}.csv", mode='w', newline="") as file:
        # En el writer, especificamos que queremos que se entrecomillen los campos que se escriban, para que las comas de los comandos no sirvan de separación
        writer = csv.writer(file, quotechar='"', quoting=csv.QUOTE_ALL)

        # Construir cabecera (cada columna será una respuesta almacenada en dict_respuestas[bloque])
        lista_header = []
        for respuesta in dict_respuestas[bloque].values():
            lista_header.append(respuesta)

        writer.writerow(["Alumno"] + lista_header)

        # Escribir las filas
        for name, diccionario_bloques in dict_alumnos_completo.items():
            row2 = [name]
            for pregunta in lista_header:
                row2 += [", ".join(map(str, dict_alumnos_completo[name][bloque][pregunta][1]))]

            writer.writerow(row2)
