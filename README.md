# Solar Panel CAD Bridge – Full Stack

Generate custom solar panel STL files via a web interface, with full telemetry.

## Quick Start

1. Clone this repo.
2. Run `./setup.sh` to create the `gh-pages` branch.
3. The frontend will be available at GitHub Pages (after the first deploy).
4. For backend:
   - Locally: `docker-compose up --build`
   - Production: build and push the Docker image, deploy to any cloud provider (Render, Fly.io, AWS, etc.)

## API

- `POST /api/generate` – JSON payload with generation parameters, returns STL as base64 and telemetry logs.

## Telemetry

Every generation logs timestamps and step-by-step status, visible in the frontend.

## Deploying Backend

To enable the backend in GitHub Actions, set `if: false` to `true` in `.github/workflows/deploy.yml` and add Docker credentials as secrets.
