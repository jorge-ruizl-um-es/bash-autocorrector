#!/bin/bash
# Script para renombrar directorios y sustituir datos personales en sus ficheros.
#
# Formato del directorio: G1-${IDENTIFICADOR_ALUMNO}-0[1-9]-${HASH}-${NOMBRE_ALUMNO}
#
# Cada directorio contiene el fichero "datos_entrega" con las líneas:
#   alumno_dni=xxxx
#   alumno_nombre=yyyy
#   alumno_apellidos=zzzzzz
#   alumno_email=ttttt@um.es
#
# El script:
# 1. Renombra el directorio sustituyendo el identificador y el nombre por valores aleatorios.
# 2. Carga los datos de "datos_entrega" para extraer alumno_nombre y alumno_apellidos.
# 3. En todos los ficheros del directorio, realiza las siguientes sustituciones:
#      a) Reemplaza el nombre completo original (alumno_nombre + " " + alumno_apellidos)
#         por el nuevo nombre aleatorio (usado en el renombrado del directorio).
#      b) Reemplaza el email construido a partir de alumno_nombre (sin espacios y en minúsculas,
#         con dominio @um.es) por "alumno@um.es".
#      c) Busca en cualquier parte del fichero cadenas con formato xxxxx@um.es y las reemplaza
#         por "alumno@um.es".

# Función para generar una cadena aleatoria.
# Parámetros:
#   $1: longitud
#   $2: conjunto de caracteres (por ejemplo, 'A-Za-z0-9' o 'A-Z')
generar_aleatorio() {
    local longitud=$1
    local charset=$2
    LC_ALL=C tr -dc "$charset" < /dev/urandom | head -c "$longitud"
}

#####################
# Paso 1: Renombrar directorios
#####################
# Se recorren los directorios cuyo nombre comienza por "G1-"
for dir in G1-*; do
    if [ -d "$dir" ]; then
        # Separamos los componentes del nombre usando "-" como delimitador.
        # Formato: G1-${IDENTIFICADOR_ALUMNO}-0[1-9]-${HASH}-${NOMBRE_ALUMNO}
        IFS='-' read -r prefijo id_original numero hash nombre_original <<< "$dir"
        
        # Generamos valores aleatorios:
        nuevo_id=$(generar_aleatorio 8 'A-Za-z0-9')
        # Este nuevo nombre será usado para anonimizar
        nuevo_nombre=$(generar_aleatorio 6 'A-Z')
        
        # Reconstruimos el nombre del directorio con el formato original,
        # sustituyendo el identificador y el nombre por los nuevos valores.
        nuevo_directorio="${prefijo}-${nuevo_id}-${numero}-${hash}-${nuevo_nombre}"
        
        echo "Renombrando '$dir' a '$nuevo_directorio'"
        mv "$dir" "$nuevo_directorio"
    fi
done

#####################
# Paso 2: Procesar el contenido de cada directorio
#####################
# Se recorren nuevamente los directorios (ya renombrados) que comienzan por "G1-"
for dir in G1-*; do
    if [ -d "$dir" ]; then
        echo "Procesando directorio '$dir'"
        # Del nombre del directorio se extrae el nuevo nombre (último campo)
        IFS='-' read -r prefijo nuevo_id numero hash nombre_aleatorio <<< "$dir"
        
        # Ruta al fichero "datos_entrega"
        datos="$dir/datos_entrega"
        if [ ! -f "$datos" ]; then
            echo "  No se encontró el fichero 'datos_entrega' en $dir; se omite este directorio."
            continue
        fi
        
        # Cargamos las variables definidas en "datos_entrega".
        # Se espera tener: alumno_dni, alumno_nombre, alumno_apellidos, alumno_email.
        source "$datos"
        if [ -z "$alumno_nombre" ] || [ -z "$alumno_apellidos" ]; then
            echo "  No se pudieron extraer 'alumno_nombre' o 'alumno_apellidos' de $datos; se omite este directorio."
            continue
        fi
        
        # Construimos el nombre completo original.
        original_nombre_completo="${alumno_nombre} ${alumno_apellidos}"
        echo "  Nombre original: '$original_nombre_completo'"
        
        # Construir el email a partir de alumno_nombre:
        # Se eliminan espacios y se pasa a minúsculas.
        email_local=$(echo "$alumno_nombre" | tr -d ' ' | tr '[:upper:]' '[:lower:]')
        email_pattern="${email_local}@um.es"
        echo "  Email patrón obtenido: '$email_pattern'"
        
        # Función auxiliar para escapar caracteres especiales en expresiones regulares de sed.
        escapa() {
            sed 's/[][\/.^$*]/\\&/g' <<< "$1"
        }
        original_nombre_completo_esc=$(escapa "$original_nombre_completo")
        email_pattern_esc=$(escapa "$email_pattern")
        
        # Se recorren todos los ficheros del directorio (incluyendo subdirectorios).
        find "$dir" -type f | while read -r file; do
            echo "    Procesando fichero: $file"
            # Se aplican las siguientes sustituciones:
            # 1) Se reemplaza el nombre completo original por el nuevo nombre aleatorio.
            # 2) Se reemplaza el email obtenido de alumno_nombre por "alumno@um.es".
            # 3) Se reemplaza cualquier cadena que tenga el formato xxxxx@um.es por "alumno@um.es".
            sed -i -E "s/${original_nombre_completo_esc}/${nombre_aleatorio}/g; \
                        s/${email_pattern_esc}/alumno@um.es/g; \
                        s/[A-Za-z0-9._%+-]+@um\.es/alumno@um.es/g" "$file"
        done
    fi
done

echo "Proceso completado."

