#!/bin/sh
# Descarga el paquete y guarda: id_estacion,segundos,bytes,estado
URL="${OBJETIVO}"; [ -n "$USE_CACHE" ] && URL="http://cache/paquete.bin"
ini=$(date +%s.%N 2>/dev/null || date +%s)
wget -q -O /tmp/p "$URL"; est=$?
fin=$(date +%s.%N 2>/dev/null || date +%s)
echo "$(hostname),$(echo "$fin - $ini" | bc 2>/dev/null),$(wc -c </tmp/p),$est" >> /resultados/corrida.csv
