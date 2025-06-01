#!/bin/bash

for a in jupyter*.tar.gz; do
	echo "Descomprimiendo $a..."
	tar -xvf $a || echo "Error con $a"
done


