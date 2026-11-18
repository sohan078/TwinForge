# TwinForge

Digital twin dashboard with a React/Vite frontend, FastAPI backend, SQLite
telemetry storage, and an MQTT broker.

## Run with Docker

Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/)
(macOS/Windows/Linux), or install Docker Engine with the Compose v2 plugin on
Linux. Use a current Compose version supporting `up --wait` and BuildKit.
Docker is the only host prerequisite: Python, Node.js, npm, and an MQTT broker
are provided by the containers.

From this directory:

```sh
sh scripts/start.sh
```

The script checks Docker and Compose, reports missing prerequisites, then runs:

```sh
docker compose up --build --detach --wait
```

Open:

- Dashboard: <http://localhost:5173>
- Backend API docs: <http://localhost:8000/docs>
- Backend health: <http://localhost:8000/health>
- API through the frontend proxy: <http://localhost:5173/api/health>

The first build requires internet access and downloads the container images,
Python requirements, and npm packages. Later builds reuse Docker's cached
dependency layers when [requirements.txt](backend/requirements.txt) and the
frontend [package.json](frontend/frontend/package.json) /
[package-lock.json](frontend/frontend/package-lock.json) have not changed.
If a dependency file changes, the relevant install step runs again, with pip/npm
download caches available to reuse packages. Packages installed on the host are
not used inside containers. Clearing Docker's build cache requires downloading
dependencies again.

The backend requires `models/rul_random_forest.joblib`. When it is absent from
the backend build context, the image build runs the existing
[training/evaluation script](backend/demos/evaluate_final_rul_model.py) using the
checked-in dataset. A supplied model is kept; otherwise the generated model is
cached in the image and is not retrained on container restart. This is the demo
model trained from the repository dataset.

## Services and storage

[compose.yaml](compose.yaml) starts:

- `frontend`: builds the actual app in [frontend/frontend](frontend/frontend)
  and serves it with Nginx. `/api/` and `/ws/` proxy to the backend, keeping HTTP
  and WebSocket connections on the dashboard's origin.
- `backend`: runs one Uvicorn worker, which owns the simulation. SQLite data is
  kept in the `backend-data` named volume across restarts and image rebuilds.
- `mqtt`: runs Mosquitto on the internal Compose network. No broker installation
  is needed on the host. The local demo broker allows anonymous connections and
  is not published to a host port.

Startup waits for broker and backend health checks before starting their
dependents. Host ports bind to localhost. Existing local SQLite files are not
copied into the image; Docker starts with its own persistent database.

To change the host ports, create a `.env` file beside [compose.yaml](compose.yaml):

```dotenv
FRONTEND_PORT=5174
BACKEND_PORT=8001
```

Then rerun the startup command and use the new ports. The frontend proxy does
not need changing. Backend settings `MQTT_HOST`, `MQTT_PORT`, and `DATABASE_PATH`
are set by Compose; non-Docker execution retains localhost and `twinforge.db`
defaults. A custom database directory must already exist and be writable.

## Everyday commands

```sh
# Status and logs
docker compose ps
docker compose logs -f

# Stop and remove containers; retain the SQLite volume and built images
docker compose down

# Start existing images without building or pulling anything
docker compose up --detach --wait --no-build --pull never

# Rebuild after changing source code or dependency files
docker compose up --build --detach --wait
```

The Docker frontend is a compiled build. Source edits require rebuilding; it
does not use hot reload. For local Vite development, the existing `npm run dev`
command proxies API and WebSocket requests to a backend on port 8000.
After restarting the backend, refresh an already-open dashboard to reconnect
its WebSocket.

`docker compose down --volumes` deletes the Docker database volume and its
telemetry history. Use it only when you intentionally want a fresh database.

If startup fails, inspect `docker compose logs backend frontend mqtt`. Check
that Docker Desktop is running, the selected ports are free, and the package
registries are reachable during the initial build.
