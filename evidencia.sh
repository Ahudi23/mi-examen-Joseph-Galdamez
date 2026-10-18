#!/usr/bin/env bash
# Construye y levanta el contenedor, y guarda la evidencia REAL de los límites
# y del consumo en la carpeta evidencia/. Ejecutar desde la raíz del proyecto.
set -euo pipefail

mkdir -p evidencia

docker compose up -d --build

echo "Esperando a que la aplicación responda..."
for _ in $(seq 1 30); do
  if curl -fsS -o /dev/null http://localhost:8000/; then break; fi
  sleep 1
done

# Un poco de tráfico para que docker stats muestre actividad.
for _ in $(seq 1 20); do
  curl -s -o /dev/null http://localhost:8000/ || true
done

{
  echo "# $(date '+%Y-%m-%d %H:%M:%S') — docker stats (una lectura)"
  docker stats --no-stream analizador
  echo
  echo "# Límites configurados (bytes de RAM / nano-CPUs; 268435456 = 256 MiB, 1000000000 = 1 CPU)"
  docker inspect -f 'Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}}' analizador
  echo
  echo "# docker ps"
  docker ps --filter name=analizador
} | tee evidencia/docker-stats.txt

echo
echo "Evidencia guardada en evidencia/docker-stats.txt"
