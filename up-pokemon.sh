#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "Error: actualizacion interrumpida (linea $LINENO)." >&2' ERR
cd /vps/clientes/pokemon
exec 9>/var/lock/up-pokemon.lock
flock -n 9 || { echo 'Ya hay una actualizacion en curso.' >&2; exit 1; }
echo 'Descargando cambios de GitHub...'
git pull --ff-only
compose=(docker compose --ansi never -p pokemon --env-file .env -f docker-compose.prod.yml)
"${compose[@]}" config --quiet
echo 'Reconstruyendo contenedores...'
"${compose[@]}" build
"${compose[@]}" up -d --wait --wait-timeout 120
curl --fail --silent --show-error --retry 10 --retry-connrefused --retry-delay 2 --max-time 15 http://127.0.0.1:8083/ -o /dev/null
curl --fail --silent --show-error --retry 10 --retry-connrefused --retry-delay 2 --max-time 15 http://127.0.0.1:8084/openapi.json -o /dev/null
echo 'Pokemon actualizado. Web: puerto 8083. API: puerto 8084.'
