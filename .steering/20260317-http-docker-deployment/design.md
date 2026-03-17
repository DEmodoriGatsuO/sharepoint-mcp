# Design — HTTP/Docker Deployment Support (Issue #9)

## Implementation Approach

### Transport Selection

FastMCP's `mcp.run(transport=...)` already accepts `"stdio"`, `"sse"`, and
`"streamable-http"`. We expose this via a CLI argument and environment variable so
deployment configuration requires no code changes.

`mcp.settings.host` and `mcp.settings.port` control the bind address for HTTP transports.

### CLI Interface

```
python server.py [--transport {stdio,sse,streamable-http}] [--host HOST] [--port PORT]
```

Priority (highest → lowest): CLI flag → environment variable → built-in default.

| Argument | Env var | Default |
|----------|---------|---------|
| `--transport` | `MCP_TRANSPORT` | `stdio` |
| `--host` | `MCP_HOST` | `0.0.0.0` |
| `--port` | `MCP_PORT` | `8000` |

### Components Changed

| File | Change |
|------|--------|
| `server.py` | Add `argparse` block in `main()` |
| `.env.example` | Document new env vars |
| `requirements.txt` | Add `uvicorn>=0.20.0` |
| `setup.py` | Add `uvicorn>=0.20.0` to `install_requires` |
| `Dockerfile` | New — multi-step slim image |
| `docker-compose.yml` | New — single-service compose file |

### Docker Image Strategy

- Base: `python:3.11-slim` (small, stable)
- No multi-stage build needed (pure Python, no compilation)
- Secrets injected at runtime via `env_file: .env` — never baked into image
- Default transport inside container: `streamable-http`

### Impact Analysis

- `stdio` users: zero impact — default unchanged
- Existing tests: no changes to test files needed; tests mock auth and do not start a server
- Security: container runs as root inside; operators can add `USER` directive if required
