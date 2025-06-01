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
# Se recorren los directorios cuyo nombre comienza por "jupyter-"
for dir in jupyter-*; do
    if [ -d "$dir" ]; then
        dir_name="${dir%/}"
		prefix="jupyter-"
		new_suffix=$(generar_aleatorio 10 'A-Za-z0-9')
		new_name="${prefix}${new_suffix}"
        
        echo "Renombrando '$dir' a '$nuevo_directorio'"
        mv "$dir_name" "$new_name"
    fi
done


#####################
# Paso 1.5: Renombrar directorios o archivos en profundidad en profundidad
#####################
# Se recorren los directorios cuyo nombre comienza por "jupyter-"
# Busca y renombra recursivamente
find . -depth -name "jupyter-*" | while read -r path; do
    if [ -e "$path" ]; then  # Verifica si existe
        # Extrae directorio padre y nombre base
        parent_dir=$(dirname "$path")
        old_name=$(basename "$path")
        
        # Si es un ARCHIVO, extrae la extensión
        if [ -f "$path" ]; then
            extension="${old_name##*.}"  # Captura todo después del último punto
            base_name="${old_name%.*}"   # Captura todo antes del último punto
            new_name="jupyter-$(generar_aleatorio 10 'A-Za-z0-9').$extension"
        else
            # Si es un DIRECTORIO o archivo sin extensión
            new_name="jupyter-$(generar_aleatorio 10 'A-Za-z0-9')"
        fi
        
        # Renombra (archivo o directorio)
        mv -v "$path" "$parent_dir/$new_name"
    fi
done

#####################
# Paso 2: Procesar el contenido de cada directorio y modificar los notebooks
#####################
# Reemplazar 'jupyter-' en notebooks (.ipynb)
find . -type f -name "*.ipynb" | while read -r notebook; do
	# Reemplaza 'jupyter-' seguido de texto no aleatorio por 'jupyter-XXXXX'
	sed -i -E "s/jupyter-[a-zA-Z0-9_-]+/jupyter-$(generar_aleatorio 10 'A-Za-z0-9')/g" "$notebook"
	echo "Procesado: $notebook"
done

# Elimina líneas con patrones de información personal en notebooks (.ipynb)
find . -type f -name "*.ipynb" -exec sed -i -E '
    # Elimina líneas con "Author: NOMBRE <email>"
    /Author: [^<]+ <[^@]+@[^>]+>/d;
    # Elimina líneas con "user.email=...@..."
    /user\.email=[^@]+@[^[:space:]]+/d;
    # Elimina líneas con "email = ...@..."
    /email[[:space:]]*=[[:space:]]*[^@]+@[^[:space:]]+/d;
    # Elimina líneas con "Correo electrónico: ...@..."
    /Correo electrónico[[:space:]]*:[[:space:]]*[^@]+@[^[:space:]]+/d
	# Elimina líneas con ...@um.es
	/@um\.es/d;
	# Elimina líneas con ".../github.com/..."
	\/github\.com\//d;
' {} \;


echo "Proceso completado."

