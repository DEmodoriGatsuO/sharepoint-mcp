# Development Guidelines

> This document defines coding conventions, naming rules, testing standards, and Git conventions for the SharePoint MCP Server.

---

## Code Style

### Formatter: black

All Python code must be formatted with `black` before committing.

```bash
black .
```

- Line length: black default (88 characters)
- No manual overrides; let black handle all formatting decisions

### Linter: ruff

All Python code must pass `ruff` with zero errors.

```bash
ruff check .
```

Auto-fix safe issues:

```bash
ruff check --fix .
```

Common rules enforced:

| Rule | Description |
|------|-------------|
| `F401` | Remove unused imports |
| `F841` | Remove unused local variables |
| `E402` | Module-level imports must be at the top of the file |
| `E712` | Avoid `== True` / `== False`; use truthiness directly |

Use `# noqa: FXXX` only when the violation is intentional and documented (e.g., availability-check imports inside `try/except`).

---

## Naming Conventions

### Python

| Element | Convention | Example |
|---------|-----------|---------|
| Module | `snake_case` | `graph_client.py` |
| Class | `PascalCase` | `SharePointContext`, `GraphClient` |
| Function / Method | `snake_case` | `get_site_info()`, `refresh_token_if_needed()` |
| Variable | `snake_case` | `site_name`, `access_token` |
| Constant | `UPPER_SNAKE_CASE` | `APP_NAME`, `GRAPH_BASE_URL` |
| MCP tool name | `snake_case` (auto-derived from function name) | `get_site_info`, `create_list_item` |
| Private helper | `_snake_case` | `_check_auth()`, `_process_csv()` |

### Files and Directories

| Element | Convention | Example |
|---------|-----------|---------|
| Python files | `snake_case.py` | `site_tools.py` |
| Test files | `test_{module}.py` | `test_auth.py` |
| Markdown docs | `kebab-case.md` | `development-guidelines.md` |
| Steering dirs | `YYYYMMDD-kebab-case` | `20260225-initial-implementation` |
| Branch names | `fix/issue-{number}-{summary}` | `fix/issue-42-token-refresh` |

---

## Testing Standards

### Framework

- `pytest` with `pytest-asyncio` (`asyncio_mode = auto` in `pytest.ini`)
- Test files in `tests/`, named `test_*.py`

### Running Tests

```bash
pytest
```

### Writing Tests

- Use `unittest.mock.patch` and `MagicMock` to mock external calls (Graph API, requests)
- Do not make real HTTP calls in unit tests
- Use fixtures (`@pytest.fixture`) for shared setup (e.g., `mock_context`, `graph_client`)
- Async tests are automatically handled by `pytest-asyncio` — no `@pytest.mark.asyncio` decorator needed

```python
# Good
async def test_get(graph_client):
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"value": "data"}
        result = await graph_client.get("endpoint/test")
        assert result == {"value": "data"}

# Avoid
assert context.is_token_valid() == True   # ruff E712
assert context.is_token_valid() == False  # ruff E712

# Correct
assert context.is_token_valid()
assert not context.is_token_valid()
```

### Coverage Targets

- Authentication logic (`auth/`) — required
- Graph client HTTP methods (`utils/graph_client.py`) — required
- Tool functions (`tools/`) — recommended for new tools

---

## Quality Check Procedure

Run all three checks before every commit and PR:

```bash
# 1. Format
black .

# 2. Lint
ruff check .

# 3. Test
pytest
```

All checks must pass with zero errors/failures.

---

## Git Conventions

### Branch Naming

```
fix/issue-{number}-{summary}
```

Examples:
```
fix/issue-12-token-refresh-failure
fix/issue-34-search-returns-empty
```

For features (non-issue-tracked):
```
feat/{summary}
```

### Commit Message Format

```
fix: #[issue-number] - brief description of the change
```

Examples:
```
fix: #12 - refresh token before expiry on every tool call
fix: #34 - handle empty search results from Graph API
```

For non-issue changes:
```
feat: add create_news_post tool
chore: update requirements.txt versions
docs: add glossary.md
```

### Pull Requests

- Title: `fix: #[number] - brief description` (≤ 70 characters)
- Body must reference the issue: `Closes #[number]`
- All quality checks must pass before merge

---

## Adding a New MCP Tool

1. Add the tool function inside `register_site_tools()` in `tools/site_tools.py`
   - Or create a new `tools/{feature}_tools.py` with a `register_{feature}_tools()` function
2. If using a new Graph API endpoint, add the method to `utils/graph_client.py`
3. Register the new tool file in `server.py` if a new file was created
4. Write tests in `tests/test_{feature}.py`
5. Run quality checks

### Tool Function Template

```python
@mcp.tool()
async def my_new_tool(ctx: Context, param: str) -> str:
    """One-line description shown to the LLM.

    Args:
        param: Description of the parameter
    """
    logger.info(f"Tool called: my_new_tool with param: {param}")
    try:
        sp_ctx = ctx.request_context.lifespan_context
        _check_auth(sp_ctx)
        await refresh_token_if_needed(sp_ctx)
        graph_client = GraphClient(sp_ctx)
        result = await graph_client.some_method(param)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in my_new_tool: {str(e)}")
        raise
```

---

## Security Guidelines

- Never commit `.env` or any file containing real credentials
- Never log access tokens or client secrets
- Validate all inputs that are passed to Graph API URLs (avoid path traversal)
- Use `# noqa` sparingly and only with a comment explaining the reason
- Keep `CLIENT_SECRET` rotation documented in `docs/auth_guide.md`
