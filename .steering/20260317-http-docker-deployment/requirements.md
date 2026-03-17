# Requirements — HTTP/Docker Deployment Support (Issue #9)

## Feature Description

Enable the SharePoint MCP server to be deployed as a web service or Docker container,
allowing Copilot agents and other HTTP-based clients to connect via SSE or streamable-HTTP
transport — in addition to the existing stdio transport for local use.

## User Stories

- As a developer deploying to a cloud VM, I want to run the MCP server as an HTTP service
  so that multiple Copilot agents can connect to it simultaneously.
- As a DevOps engineer, I want a ready-to-use Dockerfile and docker-compose.yml so that I
  can deploy the server with minimal configuration.
- As a local user, I want the existing `stdio` mode to remain the default so that my current
  setup is not broken.

## Acceptance Criteria

1. `python server.py` (no flags) starts in `stdio` mode — existing behaviour preserved.
2. `python server.py --transport sse` starts an SSE HTTP server on the configured host/port.
3. `python server.py --transport streamable-http` starts a streamable-HTTP server.
4. `--host` and `--port` flags (and `MCP_HOST` / `MCP_PORT` env vars) control the bind address.
5. A `Dockerfile` builds a production image that defaults to `streamable-http` on port 8000.
6. A `docker-compose.yml` brings up the service, loading credentials from `.env`.
7. All existing pytest tests continue to pass.
8. `black` and `ruff` report no violations.

## Constraints

- Python 3.10+ (unchanged).
- MCP SDK ≥ 1.26.0 already supports `stdio`, `sse`, and `streamable-http` transports.
- `uvicorn` is already installed but must be added to `requirements.txt` and `setup.py`.
- `.env` must never be committed; secrets are passed via env_file in docker-compose.
