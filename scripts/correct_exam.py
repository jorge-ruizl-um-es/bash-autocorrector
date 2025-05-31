#!/usr/bin/env python3

import subprocess
from collections import defaultdict 
from enum import Enum
import re       # para usar regex

# OJO! Los exámenes de este año tienen 5, pero si corregimos alguno del año pasado, como el 5 es todo texto y no hay comandos, hay que poner 4!!!!
# Poner el número de bloques que tiene el examen
NUM_BLOQUES = 4

class CommandStatus(Enum):
    BLANK = 1
    WRONG_COMMAND = 2
    WRONG_OPTIONS = 3
    WRONG_ARGS = 4
    WRONG_PIPE = 5     # si hay que usar tuberías y pone más o menos comandos de los necesarios
    WRONG_SUBSHELL = 6   # si hay que usar subshells y no lo hace o lo hace incorrectamente
    CORRECT = 7

    # Habilitar comparaciones de <
    def __lt__(self, other) -> bool:
        return self.value < other.value

    # Habilitar print
    def __str__(self):
        descriptions = {
            CommandStatus.BLANK: "BLANK",
            CommandStatus.WRONG_COMMAND: "WRONG_COMMAND",
            CommandStatus.WRONG_OPTIONS: "WRONG_OPTIONS",
            CommandStatus.WRONG_ARGS: "WRONG_ARGS",
            CommandStatus.WRONG_PIPE: "WRONG_PIPE",
            CommandStatus.WRONG_SUBSHELL: "WRONG_SUBSHELL",
            CommandStatus.CORRECT: "CORRECT"
        }
        return descriptions.get(self, "Unknown status")


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

# NOTA: Esta función puede utilizarse para un notebook de prácticas en general. Podemos etiquetarlos con el número de bloque
# y la pregunta, y localizar en un directorio base la ruta de cada notebook (usar alguna función de repo-summary), cuyo
# nombre tiene que empezar por "practica<BLOQUE>-" y terminar con "-ejercicios.ipynb". Una vez localizados tanto los de
# un alumno (dentro de su repositorio) como los del solucionario, se procede igual que antes (añadir parámetro exam:bool).

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
        # Podria usarse tambien "grep -E"
        codigo_bash_2 = f"""
        diff -u {ruta_exam}/examen-fc-bloque{str(bloque)}.ipynb {ruta_sol}/examen-fc-bloque{str(bloque)}.ipynb | egrep -A4 "#\s*I|#\s*V";
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
        comandos_out = []  # lista de preguntas sin contestar en el bloque

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

# ----------------------------- Funciones anexas para corregir un comando por partes --------------------------------------

# NOTA: Aquí puedo hacer que aunque no tengan la misma longitud, se intente corregir, añadiendo a la lista de estados
# lo de WRONG_PIPE

def divide_pipeline_composed(resp_alumno:str, solution:str) -> list:
    """
    Dado el comando de un alumno y el de la solución, teniendo estos tuberías o siendo compuestos (;), se dividen en todos los subcomandos que contengan.

    Devuelve:
        Lista con el estado de cada subcomando, o estado WRONG_PIPE si no hay el mismo número de subcomandos en la versión del alumno y en la solución.
    """
    # Dividir los comandos
    lista_comandos_alu = re.split(r'[;\|]', resp_alumno)
    lista_comandos_sol = re.split(r'[;\|]', solution)

    # No hay el mismo número de comandos en la tubería o comando compuesto
    if len(lista_comandos_alu) != len(lista_comandos_sol):
        return [CommandStatus.WRONG_PIPE]
    
    else:
        # Para cada comando de la tubería, decir su estado
        set_scores = set()
        for i in range(len(lista_comandos_alu)):
            lista_comandos_alu[i] = lista_comandos_alu[i].strip()
            lista_comandos_sol[i] = lista_comandos_sol[i].strip()

        for i in range(len(lista_comandos_alu)):
            alu = lista_comandos_alu[i]
            sol = lista_comandos_sol[i]

            # Corregir cada comando por separado
            if len(alu)==0:
                score = [CommandStatus.WRONG_PIPE] # ha puesto la separación sin nada después
            else:
                # devuelve lista con los estados de un comando
                score = correction2(alu, sol)
            set_scores = set_scores.union(set(score))
        
        # Devolver lista de todos los estados de cada comando (sin repetir)
        return list(set_scores)
    
def correct_subshell(resp_alumno:str, solution:str) -> list:
    """
    Dado el comando de un alumno y el de la solución, teniendo estos subshells, corrige la parte externa y luego trata el interior del subshell como un comando.

    Devuelve:
        Lista con el estado de cada subcomando, o estado WRONG_PIPE si no hay el mismo número de subcomandos en la versión del alumno y en la solución.
    """

    separacion = resp_alumno.split('$(', 1)
    separacion_sol = solution.split('$(', 1)

    if len(separacion) != len(separacion_sol):
        return [CommandStatus.WRONG_SUBSHELL]
    
    else:
        set_correcciones_salida = set()
        result_externo = correction2(separacion[0].strip(), separacion_sol[0].strip())
        result_interno = correction2(separacion[1].strip().strip(')'), separacion[1].strip().strip(')'))
        set_correcciones_salida = set_correcciones_salida.union(set(result_externo))
        set_correcciones_salida = set_correcciones_salida.union(set(result_interno))
        
        return list(set_correcciones_salida)


def check_options(lista_partes_alu: list, lista_partes_sol: list) -> bool:
    '''
    Tomar las palabras que empiecen por "-" en el comando, dado que serán opciones, y comprobar que hay las mismas letras en ambos comandos (asumiendo que se ponen todas las opciones en su forma corta, con una sola letra, y que el orden de aparición no importa)
    '''
    
    lista_opt_alu = [t for t in lista_partes_alu[1:] if t.startswith("-")]
    set_opt_alu = set()
    for opt in lista_opt_alu:
        set_opt_alu = set_opt_alu.union(set(opt))

    lista_opt_sol = [t for t in lista_partes_sol[1:] if t.startswith("-")]
    set_opt_sol = set()
    for opt in lista_opt_sol:
        set_opt_sol = set_opt_sol.union(set(opt))

    # Si ambos son distintos es que, independientemente del orden, el alumno ha puesto otras opciones o que le falta/sobra algo
    if set_opt_sol != set_opt_alu:
        return False  # mal
    else:
        return True   # bien
    
def absolutize_route(arg_alu: str) -> str:
    # PENDIENTE	
    return arg_alu   # la cosa sería hacer el cambio para que funcione
    
def check_arguments(lista_partes_alu: list, lista_partes_sol: list) -> CommandStatus:
    # Todo lo que no sea comando y no empiece por "-" será argumento
    # MEJORA: Si un argumento es ., no se tiene en cuenta (es opcional, puede ponerse o no)
    args_alu = [t for t in lista_partes_alu[1:] if not t.startswith("-") and t!='.']
    args_sol = [t for t in lista_partes_sol[1:] if not t.startswith("-") and t!='.']

    if len(args_alu) != len(args_sol):  # distinto número de argumentos
        return CommandStatus.WRONG_ARGS
    
    else:
        for i in range(len(args_alu)):
            # obtener argumentos uno a uno
            arg_alu = args_alu[i].strip('\\n').strip('\\"').strip(' ')  # vamos a no tener en cuenta saltos de líneas, comillas...
            arg_sol = args_sol[i].strip('\\n').strip('\\"').strip(' ')  
            
            # Limpiar el ./ en caso de que esté
            if arg_alu.startswith('./'):
                arg_alu = arg_alu[2:]
            if arg_sol.startswith('./'):
                arg_sol = arg_sol[2:]
            
            # Si el alumno ha puesto ruta relativa y el comando tiene una ruta absoluta, conviene pasar la ruta relativa
            # a absoluta para poder compararlas bien
            if not arg_alu.startswith('/') and arg_sol.startswith('/'):     # ruta relativa
                arg_alu = absolutize_route(arg_alu)

            if arg_alu != arg_sol:
                return CommandStatus.WRONG_ARGS
        
        # Si todos han ido coincidiendo, la respuesta es correcta
        return CommandStatus.CORRECT

def check_commit(lista_partes_alu: list, lista_partes_sol: list) -> list:
    # Solo hay que comprobar que el alumno haya usado commit y que haya puesto la opción "-m"
    # No hay que comprobar los argumentos porque el único que se le pone al commit es el texto

    lista_correcciones_salida = []

    if lista_partes_alu[0] != 'commit':
        lista_correcciones_salida.append(CommandStatus.WRONG_COMMAND)
    
    result = check_options(lista_partes_alu, lista_partes_sol)
    if result and len(lista_correcciones_salida) == 0:
        lista_correcciones_salida.append(CommandStatus.CORRECT)
    else:
        lista_correcciones_salida.append(CommandStatus.WRONG_OPTIONS)
    
    return lista_correcciones_salida

def correct_find(lista_partes_alu: list, lista_partes_sol: list) -> list:
    # En un find, lo más común es que haya varias opciones con un nombre concreto (no son solo letras), de forma que cada una va acompañada de un valor (argumento) concreto

    # ARGUMENTOS
    args_alu = [t.strip("\\n") for t in lista_partes_alu[1:] if (not t.startswith("-") or t[1].isdigit())]
    args_sol = [t.strip("\\n") for t in lista_partes_sol[1:] if (not t.startswith("-") or t[1].isdigit())]

    # OPCIONES
    lista_opt_alu = [t for t in lista_partes_alu[1:] if (t.startswith("-") and not t[1].isdigit())]
    lista_opt_sol = [t for t in lista_partes_sol[1:] if (t.startswith("-") and not t[1].isdigit())]

    # si aparece una opción sin argumento, será False indicando que el comando está incompleto, y devolveremos WRONG_OPTIONS
    complete = True 

    # Como las opciones del find van acompañadas cada una de su correspondiente argumento, mapearemos cada opción con su argumento asociado en alu y sol (en ese orden)
    map_opt_arg = defaultdict(list)
    for i in range(len(lista_partes_alu)):
        if lista_partes_alu[i] in lista_opt_alu:
            try:
                add = lista_partes_alu[i+1]
                map_opt_arg[lista_partes_alu[i]].append(add.strip('\\n'))  # el siguiente a la opción será su argumento
            except IndexError:
                complete = False

    if not complete:
        return [CommandStatus.WRONG_OPTIONS]
    
    for i in range(len(lista_partes_sol)):
        if lista_partes_sol[i] in lista_opt_sol:
            add = lista_partes_sol[i+1]
            map_opt_arg[lista_partes_sol[i]].append(add.strip('\\n'))
    
    # Si alguna lista asociada a alguna clave no tiene longitud par, entonces las opciones utilizadas no coinciden en ambos comandos
    for lista in map_opt_arg.values():
        if len(lista)%2 != 0:
            return [CommandStatus.WRONG_OPTIONS]
        
        # Si no, hay que comparar que los elementos de cada lista coincidan por pares -> podemos hacerlo fácilmente definiendo un conjunto a partir de la lista y comprobando que su longitud sea la mitad que la de la lista
        set_args = set(lista)
        if len(set_args) != len(lista)//2:
            return [CommandStatus.WRONG_ARGS]
        
    # Por último, hacemos un cleanout, estudiando los argumentos que no estén asociados a ninguna opción
    for arg in args_alu:
        if arg not in args_sol:
            return [CommandStatus.WRONG_ARGS]
        
    # Si todo ha ido bien, el find es correcto
    return [CommandStatus.CORRECT]

# -------------------------------- Función de corrección general ----------------------------------------------------

def correction2(resp_alumno: str, solution: str) -> list:
    """
    Divide el comando resp_alumno y el comando solution en partes. Va comparando cada parte por orden hasta devolver su estado (CommandStatus)

    MEJORA: Devuelve una lista de CommandStatus
    """

    # Lista de salida con las correcciones de un comando
    lista_correcciones = []

    # Si detecta que el comando es compuesto/pipeline, lo trata a parte
    if ';' in solution or '|' in solution:
        result = divide_pipeline_composed(resp_alumno, solution)
        return result
        
    # Detección de subshell -> corregir el comando "de fuera", y luego entrar al subshell
    if '$(' in solution:
        result = correct_subshell(resp_alumno, solution)
        return result

    # Separar el comando por partes
    lista_partes_alu = resp_alumno.split()
    lista_partes_sol = solution.split()

    # Primera parte de cualquier comando -> comando en sí:
    if lista_partes_alu[0] != lista_partes_sol[0]:
        lista_correcciones.append(CommandStatus.WRONG_COMMAND)
    
    elif lista_partes_alu[0] == 'git':  # Comando de git detectado
        # Es commit
        if lista_partes_sol[1] == 'commit':
            return check_commit(lista_partes_alu[1:], lista_partes_sol[1:])
        # No es commit
        else:
            # corregir como si el comando no tuviera el 'git' delante (para que, por ejemplo, si el alumno usa git add cuando tiene que usar git push, el fallo sea WRONG_COMMAND)
            return correction2(" ".join(lista_partes_alu[1:]), " ".join(lista_partes_sol[1:]))
            
    elif lista_partes_sol[0] == 'find':  # Comando find detectado -> tratar por separado porque plantea problemas
        return correct_find(lista_partes_alu, lista_partes_sol)
    
    
    correct_options = check_options(lista_partes_alu, lista_partes_sol)  # True si coinciden (no tiene por qué ser en orden)
    if not correct_options:
        lista_correcciones.append(CommandStatus.WRONG_OPTIONS)
    
    resultado_arg = check_arguments(lista_partes_alu, lista_partes_sol)
    if (resultado_arg == CommandStatus.CORRECT and len(lista_correcciones) == 0) or resultado_arg != CommandStatus.CORRECT:
        lista_correcciones.append(resultado_arg)
    
    return lista_correcciones

# ---------------------------- Función de corrección final, aplicando conteo ---------------------------------

def compare_commands(dict_bloques: defaultdict, detail=False):
    '''
	Para la salida correspondiente a leer un examen (conjunto de notebooks) y compararlos con la solución, cuenta cuántas veces aparece en la corrección cada uno de los estados especificados como resultado de la corrección de cada comando.
    
    Modificación: si le pasamos la opción "detail = True", devolverá el diccionario en el que vemos una a una las preguntas y los estados que les asigna, así como la lista con la respuesta del alumno a dicha pregunta, y la respuesta correcta.
    '''
    
    # Para el alumno que consideremos, contabilizar cuántas preguntas tiene en blanco, comando incorrecto...
    scores = defaultdict(int) 
    
    # Diccionario que se devuelve al pedir detail. A cada bloque, mapeará un diccionario que a su vez mapea a cada pregunta una lista con: [[estados tras la correccion], [comando_respuesta, comando_solution]].
    dict_debug = defaultdict(dict)

    for bloque in range(1, NUM_BLOQUES+1):
        for (pregunta, lista) in dict_bloques[bloque].items():
            if pregunta == 0: 
                if len(lista)>0:       # tratamiento de preguntas en blanco
                    scores[CommandStatus.BLANK] += len(lista)
                    dict_debug[bloque][0] = [[CommandStatus.BLANK], lista]
            else:
                resp_alumno = lista[0]
                solution = lista[1]
                
                if resp_alumno is not None:
                    try:
                        list_status = correction2(resp_alumno, solution)
                    except IndexError:
                        print(pregunta, lista)

                    for status in list_status:    
                        scores[status] += 1

                    dict_debug[bloque][pregunta] = [list_status, lista]
    if not detail:
        return scores
    else:
        return scores, dict_debug


# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    # Pruebas
    ruta_exam_viejo = './dir_exams/G1-I0f5JGEC-01-6a6a45-BCZQUV'
    ruta_exam_nuevo = './dir_exams/examen-suspenso'
    ruta_sol_viejo = './examen-resuelto-2024'
    ruta_sol_nuevo = './scripts_jorge/examen-resuelto'
    comando_alu = 'touch copyright;'
    comando_sol = 'grep Copyright LICENSE > copyright; echo "Nombre Apellidos" >> copyright'
    #print(correction2(comando_alu, comando_sol))
    

    dict_bloques = execute_diff(ruta_exam_viejo, ruta_sol_viejo)
    
    ''' 
    for bloque in dict_bloques:
        for (pregunta, respuestas) in dict_bloques[bloque].items():
            print(f"{bloque}.{pregunta}: {respuestas}")
    '''
    
    scores, dict_debug = compare_commands(dict_bloques, detail=True)
    for (bloque, dict_preguntas) in dict_debug.items():
        for (pregunta, lista) in dict_preguntas.items():
            print(f'{bloque}.{pregunta}: {lista}\n')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    