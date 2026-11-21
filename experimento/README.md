# Ensayo con Docker Compose

Estado: lógica del cliente corregida y probada fuera de Docker (ver abajo); la corrida completa
con `docker compose` todavía no se ejecutó en un entorno con el demonio de Docker disponible —
falta confirmarla antes de usarla como ensayo final.
Ensaya el procedimiento antes del laboratorio: 30 clientes, enlace limitado, con y sin caché.
Los datos sintéticos validan el método; la medición real se hace en el laboratorio (OE1–OE3).

Arreglado: el cliente usaba `bc`/`date +%N`, que no existen en `alpine:3` (BusyBox `date` no
soporta `%N` y `bc` no viene instalado), así que la corrida fallaba o escribía campos vacíos.
Se reescribió como `scripts/cliente.py` (solo biblioteca estándar, imagen `python:3.12-alpine`),
con `time.monotonic()` en vez de `date` — coherente con el reloj monotónico que pide
`docs/PLAN_MEDICION.md`. También se corrigió que `USE_CACHE` no llegaba al contenedor en el
perfil `cache`: ahora se reenvía por `environment` en `docker-compose.yml`.
Probado sin Docker: un servidor HTTP local sirviendo `datos/paquete.bin` y `scripts/cliente.py`
apuntando a él, caso de éxito y de fallo de red, con el formato de salida esperado.
Pendiente: correr `docker compose --profile baseline up --scale cliente=30` y
`USE_CACHE=1 docker compose --profile cache up --scale cliente=30` de verdad (enlace limitado +
proxy de caché juntos) para confirmar el ensayo completo.
