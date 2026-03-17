# Task List — HTTP/Docker Deployment Support (Issue #9)

## Tasks

- [x] Create `.steering/20260317-http-docker-deployment/requirements.md`
- [x] Create `.steering/20260317-http-docker-deployment/design.md`
- [x] Create `.steering/20260317-http-docker-deployment/tasklist.md`
- [x] Modify `server.py` — add `--transport`, `--host`, `--port` CLI args
- [x] Modify `.env.example` — add `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`
- [x] Modify `requirements.txt` — add `uvicorn>=0.20.0`
- [x] Modify `setup.py` — add `uvicorn>=0.20.0` to `install_requires`
- [x] Create `Dockerfile`
- [x] Create `docker-compose.yml`
- [x] Run `black .` — no violations
- [x] Run `ruff check .` — no violations
- [x] Run `pytest` — all tests pass

## Completion Criteria

All tasks checked, quality checks clean, PR created referencing Issue #9.
