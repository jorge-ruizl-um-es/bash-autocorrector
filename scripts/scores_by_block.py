#!/usr/bin/env python3

from correct_exam import execute_diff, compare_commands, CommandStatus, NUM_BLOQUES
from collections import defaultdict
import json
import re

class UnmatchingDicts(Exception):
    pass

"""
Punto de partida: ruta al examen de un alumno junto con la ruta al examen resuelto. A partir de ello, generamos un diccionario de la forma:

{bloque: {pregunta: [list(STATUS), [respuesta_alumno, respuesta_correcta]]}}

IMPORTANTE: Asumimos siempre que trabajamos con un solo alumno (es decir, en el módulo principal, iremos llamando a funciones de este módulo iterativamente para cada alumno)

Con estas funciones, obtendremos:
    - Diccionario en el que tenemos, para cada bloque, para cada pregunta, su estado, el comando que ha puesto el alumno, y el comando correcto (sólo si el alumno la ha contestado, si no, tendremos en el bloque un diccionario de clave 0 que contiene la lista de preguntas en blanco en dicho bloque).
    
    - Diccionario en el que tenemos, para cada bloque, para cada pregunta, cuál es la correcta.
"""

def get_dict_completo(ruta_alu: str, ruta_sol: str) -> defaultdict:
    dict_bloques = execute_diff(ruta_alu, ruta_sol)
    _, dict_completo = compare_commands(dict_bloques, detail=True)
    
    # Vamos a eliminar las claves 0, que contienen una lista en la que tenemos [BLANK, [lista_preguntas_en_blanco]]
    for dict_preguntas in dict_completo.values():
        if 0 in dict_preguntas:
            del dict_preguntas[0]

    return dict_completo

# Función para convertir números romanos a naturales
def roman_to_int(roman):
    roman_numerals = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
    return roman_numerals.get(roman, None)

# Función para extraer los bloques y soluciones del examen resuelto
def extraer_bloques_solutions(ruta_directorio: str) -> dict:
    '''
    Devuelve diccionario en el que para cada pregunta de cada bloque, obtenemos la respuesta en examen-resuelto. Es decir, el diccionario es de la forma:
    {BLOQUE (int): {PREGUNTA (int): COMANDO_RESPUESTA (str), ...}, ...}

    Parámetros:
        - ruta_directorio (str): ruta a la carpeta con el examen resuelto
    '''

    bloques_dict = {}

    # NUM_BLOQUES indicado en el módulo correct_exam
    for bloque in range(1, NUM_BLOQUES+1):
        bloques_dict[bloque] = {}
        # Ruta al fichero del examen resuelto 
        ruta_fichero = f'{ruta_directorio}/examen-fc-bloque{str(bloque)}.ipynb'

        # Abrir notebook en formato JSON
        with open(ruta_fichero, "r", encoding="utf-8") as file:
            notebook = json.load(file)

        bloque_actual = None
        pregunta_actual = None

        for cell in notebook.get("cells", []):
            
            # Analizar celdas de código
            if cell["cell_type"] == "code":
                source = "".join(cell["source"])

                # Buscar el bloque en el que tengamos #(bloque).(pregunta)\n(comando)   #@solution@
                bloque_match = re.search(r'#\s*(I+V*|V+)\.(\d+)\n(.*?)\s+#@solution@', source)
                
                if bloque_match:
                    # Obtener bloque, pregunta, y comando
                    bloque_romano, pregunta, comando = bloque_match.groups()
                    bloque = roman_to_int(bloque_romano)
                    pregunta = int(pregunta)

                    if bloque is not None:
                        pregunta_actual = pregunta
                        bloque_actual = bloque

                    if comando is not None and bloque_actual is not None and pregunta_actual is not None:
                        # añadirlo al diccionario de salida
                        bloques_dict[bloque_actual][pregunta_actual] = comando

    return bloques_dict


"""
El siguiente paso es, a partir del diccionario completo, devolver un conteo por bloques. Es decir, devolveremos un diccionario en el que para cada bloque indiquemos el número de preguntas de cada estado
"""

def count_by_blocks(dict_completo: defaultdict) -> dict:
    dict_salida = {}

    # Para cada bloque en el diccionario con el estado de cada pregunta de un alumno
    for bloque in dict_completo.keys():
        dict_salida[bloque] = {}

        # Inicializar diccionario para llevar la cuenta de la aparición de cada valor de CommandStatus en el bloque 
        for status in CommandStatus:
            dict_salida[bloque][status] = 0

        # Extraer el estado de cada pregunta (dentro de la lista asociada a su pregunta)
        for (preg, lista) in dict_completo[bloque].items():
            lista_estados= lista[0]
            
            for estado in lista_estados:
                dict_salida[bloque][estado] += 1
    
    return dict_salida


"""
Ahora toca unir en una función el diccionario dict_completo con el detalle de las respuestas del alumno, su estado, etc. con el diccionario en el que almacenamos las respuestas. Para cada respuesta del alumno, la pondremos como valor de un diccionario en el que la clave es la respuesta correcta. Esto lo haremos dentro de un diccionario para cada bloque, es decir:
{BLOQUE: {respuesta_correcta: respuesta_alumno, ...}, ...}
"""

def map_alucommand_to_answer(dict_completo: defaultdict, dict_answers: dict) -> dict:
    '''
    Parámetros:
        - dict_completo: diccionario en detalle, con el bloque, la pregunta, el estado, el comando del alumno y el comando correcto al que se corresponde --> {bloque: {pregunta(num): [estado, [respuesta_alu, respuesta_sol]], ...}, ...}- Es la salida de get_dict_completo.
        - dict_answers: diccionario con las respuestas a cada pregunta de cada bloque, generado por la función extraer_bloques_solutions.

    Devuelve:
        - Diccionario dict_command_to_answer en el que, para cada bloque, tenemos como clave la respuesta a la pregunta correspondiente, y como valor la respuesta ofrecida por el alumno. 
            AÑADIDO: los valores son una lista --> [respuesta-alumno, valor-de-correccion]
    '''

    # Si no hay el mismo número de bloques (claves) en los diccionarios, no podemos generar la salida
    if len(dict_completo) != len(dict_answers):
        raise UnmatchingDicts

    dict_command_to_answer = {}  # salida

    for bloque in dict_answers.keys():
        # Vamos a definir dentro de cada bloque un defaultdict, de forma que si buscamos un comando de respuesta para el cual no existe el comando del alumno (es decir, lo ha dejado en blanco), se le asigna a esa pregunta la cadena vacía.
        dict_command_to_answer[bloque] = defaultdict(str)

        # Almacenar preguntas respondidas por el alumno
        for pregunta in dict_answers[bloque].keys():
            respuesta_correcta = dict_answers[bloque][pregunta]
            
            if pregunta in dict_completo[bloque]:
                # Respuesta del alumno --> acceder a la primera posición de la sgunda lista almacenada en bloque:pregunta
                dict_command_to_answer[bloque][respuesta_correcta] = [dict_completo[bloque][pregunta][1][0]] 
                
                # Añadir el estado de la corrección
                dict_command_to_answer[bloque][respuesta_correcta].append(dict_completo[bloque][pregunta][0])
                
            else:
                # Si la pregunta no está en el dict_completo, entonces el alumno la ha dejado en blanco...
                dict_command_to_answer[bloque][respuesta_correcta] = [" ", [CommandStatus.BLANK]]
    
    return dict_command_to_answer



if __name__ == '__main__':
    
    ruta_prueba_alu = 'dir_exams/G1-ZeT31f5J-01-ef8073-TMTTWD'
    ruta_prueba_sol = 'examen-resuelto-2024'
    
    dict_debug = get_dict_completo(ruta_prueba_alu, ruta_prueba_sol)
    '''
    for (bloque, dict) in dict_debug.items():
        for (pregunta, valor) in dict.items():
            print(f'{bloque}.{pregunta}: {valor}\n')'''
    
    dict_sol = extraer_bloques_solutions(ruta_prueba_sol)
    dict_command_to_answer = map_alucommand_to_answer(dict_debug, dict_sol)
    print(dict_command_to_answer[1]['ls -l image/png/b*'][1])
    for (bloque, dict_preg_resp) in dict_command_to_answer.items():
        for (pregunta, respuesta) in dict_preg_resp.items():
            print(f'{bloque}.{pregunta} --> {respuesta}\n') 
    