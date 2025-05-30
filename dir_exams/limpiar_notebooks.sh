#!/bin/bash
# Recorre recursivamente todos los ficheros .ipynb y elimina sus salidas

find . -name "*.ipynb" -print0 | while IFS= read -r -d '' nb; do
    echo "Limpiando salidas del notebook: $nb"
    jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace "$nb"
done

