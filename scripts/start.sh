#!/bin/sh
set -eu

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required. Install Docker Desktop (https://www.docker.com/products/docker-desktop/) or Docker Engine with Compose v2." >&2
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Docker Compose v2 is required. Install/update Docker Desktop or the Docker Compose plugin." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running. Start Docker Desktop or the Docker daemon, then run this script again." >&2
    exit 1
fi

cd "$(dirname "$0")/.."
# BuildKit checks cached layers and downloads dependencies only when needed.
docker compose up --build --detach --wait

echo "TwinForge is ready. Published addresses:"
docker compose port frontend 80
docker compose port backend 8000
