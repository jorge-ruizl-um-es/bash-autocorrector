# Adaptacion del script "fc-alumno-instalar" para el uso del alumno Jorge Ruiz
# Sirve de prueba para ver si comprende el funcionamiento de estos scripts (y le es útil para su uso personal)

#!/bin/bash

set -u

color() {
    # "$#" es el numero de argumentos de la funcion
    [ $# -ne 2 ] && { echo "color necesita 2 argumentos" >&2 ; exit 1 ; }

    if [ "$1" = "rojo" ] ; then
        echo -en '\e[31m'
    elif [ "$1" = "verde" ] ; then
        echo -en '\e[32m'
    elif [ "$1" = "amarillo" ] ; then
        echo -en '\e[33m'
    else
        echo "color «$1» incorrecto"
    fi
    echo -en "$2"'\e[0m'
}

# Pedir el nombre de la asignatura
echo "Indica la asignatura para la que quieres crear un repositorio (el nombre empleado será el que tenga el directorio):"
# Leer de teclado un caracter
read asignatura
echo "Se creará un repositorio para la asignatura $asignatura"

# Direcciones y rutas
github_username="jorge-ruizl-um-es"
repo_dir="$HOME/Escritorio/uni/$asignatura"
github_repo_url="https://github.com/$github_username/$asignatura"


echo "Instalando bitácora del usuario $github_username..."

echo "Se instalará en el directorio $repo_dir"

cd

if [ -d $repo_dir ]; then
    # -d comprueba si la variable apunta a un directorio valido

    echo "El directorio $repo_dir ya existe. Comprobando si es un repositorio Git válido... "
    cd $repo_dir

    # Obtiene lista de commits locales en el repositorio $repo_dir
    LOCAL_COMMITS=$(git --no-pager log --decorate=short --date=short --pretty=format:"%h" 2> /dev/null)

    if [[ $LOCAL_COMMITS != "" ]]; then
        echo "$(color verde "[OK] El repositorio para la asignatura $asignatura parece estar instalado")"

        # Ruta absoluta del directorio con la bitácora
        repo_local_path_full="$(readlink -f .)"
    else
        echo "$(color rojo "[ERROR]")"
        echo "$(color rojo "El directorio $repo_dir ya existe. Bórralo para realizar una nueva instalación")"
        exit 1
    fi

else
    # No existe el directorio -> crearlo

    mkdir $repo_dir
    cd $repo_dir
    echo "Creando repositorio Git en $PWD"
    git init

    # Crear README
    README="README.md"
    echo "# Repositorio de $asignatura" > "$README"
    echo "" >> "$README"
    echo "- Curso: 2024/25" >> "$README"
    echo "- Autor: $USER" >> "$README"
    echo "- Usuario de GitHub: $github_username" >> "$README"
    
    git add $README
    git commit -m "Commit inicial: Añadir README"
    git log --stat --oneline
    echo
    echo "$(color verde "La instalación del repositorio local se ha completado satisfactoriamente".)"
    repo_local_path_full="$(readlink -f .)"
    echo "Repositorio local ubicado en ${repo_local_path_full}"
fi

# Añadir el repositorio local creado a un repositorio remoto en Github
echo "¿Quieres crear una copia del repositorio-bitácora en GitHub ahora? (s/n)"
# Leer de teclado un caracter
read -n 1 -s tecla

if [ "$tecla" == "s" ]; then
    if git ls-remote --exit-code origin > /dev/null 2>&1; then
        echo "$(color amarillo "[WARNING] La bitácora ya parece estar enlazada con GitHub")"
        echo "Ya existe un remoto llamado 'origin' cuya URL es $(git config --get remote.origin.url)"
        echo "Ejecuta 'git pull origin main' para obtener los cambios del repositorio remoto"
        echo "Ejecuta 'git push origin main' para enviar tus cambios locales al repositorio remoto"
        echo "Si se produce error en el push/pull, es posible que local y remoto hayan divergido..."
        exit
    fi
    # Requires: github CLI (gh) -> comprueba que está instalado
    if ! command -v gh >/dev/null 2>&1; then
        echo "GitHub CLI (gh) no está instalado. Puedes instalarlo con: sudo apt install gh"
        exit
    fi

    echo "Se va a proceder a autenticarse en GitHub con el usuario: $github_username"
    echo "La copia remota del repositorio-bitácora estará ubicada en $github_repo_url"
    echo "Pulsa una tecla para continuar:"
    read -n 1 -s tecla

    # Autenticar usuario en GitHub
    gh auth login

    cloned_dir="${repo_dir}_gh_cloned"
    rm -rf $cloned_dir
    git clone --quiet $github_repo_url $cloned_dir 2> /dev/null

    if [ -d $cloned_dir ]; then
        # Existe un directorio con la direccion del clonado
        if [[ $(git ls-remote $github_repo_url  2>&1 | wc -l) == 0 ]]; then
            # Repo existe pero no tiene commits
            echo "$(color amarillo [WARNING])"
            echo "Ya existe un repositorio remoto sin contenido en ${github_repo_url}. Se vinculará como copia remota del repositorio local en ${repo_dir}"
            git remote add origin $github_repo_url.git
            git branch -M main
            git push  --quiet -u origin main
            rm -rf $cloned_dir
        else
            # Repo existe y tiene commits
            echo "$(color rojo [ERROR])"
            echo "Ya existe un repositorio remoto con contenido en $github_repo_url. Bórralo para realizar una nueva instalación."
            echo "El repositorio encontrado en $github_repo_url tiene los siguientes commits:"
            cd $cloned_dir
            git --no-pager log --decorate=short --date=short --pretty=format:"%ad%x09%an%x09%x09%s"
            echo
            cd -
            rm -rf $cloned_dir
            exit
        fi
    else
        # Crear repositorio remoto
        gh repo create $asignatura --private --source=. --push # --remote=origin
        #git push --quiet -u origin main
        #git pull
        echo "$(color verde [OK])"
        echo "$(color verde "Se ha creado una copia del repositorio bitácora en GitHub, enlazada satisfactoriamente".)"
        echo "A partir de ahora, puedes hacer 'git push' y 'git pull' para sincronizar tus cambios con GitHub"
        echo "Copia local:  ${repo_local_path_full} (directorio en este servidor de JupyterHub)"
        echo "Copia remota: ${github_repo_url} (en GitHub)"
    fi
else
    exit
fi
