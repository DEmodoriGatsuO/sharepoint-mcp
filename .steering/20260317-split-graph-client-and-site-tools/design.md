# Design: Split graph_client.py and site_tools.py

---

## Issue 1 — GraphClient Mixin Split

### Constraint: Method Interdependencies

Methods inside `GraphClient` call each other via `self.*`. For example:

```
create_advanced_document_library
  → self.post()               (HTTP layer)
  → self.get()                (HTTP layer)
  → self.add_column_to_list() (list domain)
  → self.create_folder_in_library() (drive domain)
```

A naive split into independent classes would break these calls. The solution is **Python mixins**: each domain module defines a mixin class with its methods, and `GraphClient` inherits all of them. At runtime, every `self.*` call resolves correctly through Python's MRO because `self` is always a `GraphClient` instance that owns all methods.

### Import Dependency Rule

No mixin imports another mixin. Cross-domain `self.*` calls resolve at runtime — no static import is needed. This prevents all circular import risks.

```
_graph_constants.py  ←── _graph_http.py, _graph_drive_ops.py
_graph_http.py       ←── (no internal imports)
_graph_site_ops.py   ←── (no internal imports)
_graph_list_ops.py   ←── (no internal imports)
_graph_page_ops.py   ←── (no internal imports)
_graph_drive_ops.py  ←── _graph_constants.py
graph_client.py      ←── all five mixins + _graph_constants (for re-export)
```

### Constants Module

`LARGE_FILE_THRESHOLD` and `UPLOAD_CHUNK_SIZE` are used by both `_GraphHttpMixin` (`_upload_in_chunks`) and `_GraphDriveOpsMixin` (`upload_document`). Defining them in either mixin would require the other to import it — creating exactly the kind of cross-mixin dependency to avoid. Instead they live in a dedicated `utils/_graph_constants.py` (a pure-data file with no imports), and `utils/graph_client.py` re-exports them so that existing callers (`tests/test_graph_client.py`) need no changes.

### File Layout

```
utils/
  _graph_constants.py    # LARGE_FILE_THRESHOLD, UPLOAD_CHUNK_SIZE
  _graph_http.py         # _GraphHttpMixin
                         #   get, post, patch, delete, upload_file, _upload_in_chunks
  _graph_site_ops.py     # _GraphSiteOpsMixin
                         #   get_site_info, list_document_libraries, create_site
  _graph_list_ops.py     # _GraphListOpsMixin
                         #   create_list, create_list_item, update_list_item,
                         #   delete_list_item, add_column_to_list,
                         #   create_intelligent_list, _get_intelligent_schema_for_purpose
  _graph_page_ops.py     # _GraphPageOpsMixin
                         #   create_page, create_modern_page, create_news_post,
                         #   add_section_to_page, add_web_part_to_section,
                         #   update_page, publish_page
  _graph_drive_ops.py    # _GraphDriveOpsMixin
                         #   get_document_content, upload_document,
                         #   create_folder_in_library, create_advanced_document_library,
                         #   _get_document_metadata_schema,
                         #   _get_folder_structure_for_document_type,
                         #   list_folder_contents, get_document_content_by_path,
                         #   get_item_metadata_by_path
  graph_client.py        # GraphClient(all mixins) — thin facade, re-exports constants
```

The `_` prefix on mixin files signals they are internal implementation details and should not be imported directly by code outside `utils/`.

### Resulting `graph_client.py`

```python
from utils._graph_constants import LARGE_FILE_THRESHOLD, UPLOAD_CHUNK_SIZE  # re-export
from utils._graph_http import _GraphHttpMixin
from utils._graph_site_ops import _GraphSiteOpsMixin
from utils._graph_list_ops import _GraphListOpsMixin
from utils._graph_page_ops import _GraphPageOpsMixin
from utils._graph_drive_ops import _GraphDriveOpsMixin

class GraphClient(
    _GraphSiteOpsMixin,
    _GraphListOpsMixin,
    _GraphPageOpsMixin,
    _GraphDriveOpsMixin,
    _GraphHttpMixin,
):
    def __init__(self, context: SharePointContext):
        self.context = context
        self.base_url = context.graph_url
```

MRO order is chosen so that higher-level domain mixins appear before `_GraphHttpMixin`. Since no two mixins define the same method name, the order has no practical effect on resolution — but the convention reads naturally as a dependency stack.

---

## Issue 2 — site_tools.py Domain Split

### Shared Helper

`_check_auth(sp_ctx)` is called at the start of every tool function. Rather than duplicating it or keeping it in the thinned `site_tools.py`, it lives in `tools/_tool_helpers.py`. All three new domain modules import it from there.

### Tool Classification

| Tool | Category |
|------|----------|
| `get_site_info` | Read |
| `list_document_libraries` | Read |
| `search_sharepoint` | Read |
| `get_document_content` | Read |
| `list_folder_contents` | Read |
| `get_document_by_path` | Read |
| `get_item_metadata` | Read |
| `upload_document` | Write |
| `create_list_item` | Write |
| `update_list_item` | Write |
| `create_sharepoint_site` | Provisioning |
| `create_intelligent_list` | Provisioning |
| `create_advanced_document_library` | Provisioning |
| `create_modern_page` | Provisioning |
| `create_news_post` | Provisioning |

### File Layout

```
tools/
  _tool_helpers.py       # _check_auth (shared by all three modules)
  read_tools.py          # register_read_tools(mcp) — 7 read tools
  write_tools.py         # register_write_tools(mcp) — 3 write tools
  provisioning_tools.py  # register_provisioning_tools(mcp) — 5 provisioning tools
  site_tools.py          # register_site_tools(mcp) — delegates to the three above
```

### Resulting `site_tools.py`

```python
from tools.read_tools import register_read_tools
from tools.write_tools import register_write_tools
from tools.provisioning_tools import register_provisioning_tools

def register_site_tools(mcp: FastMCP):
    register_read_tools(mcp)
    register_write_tools(mcp)
    register_provisioning_tools(mcp)
```

`server.py` calls `register_site_tools(mcp)` and requires no changes.

### Import Reduction per Module

| Module | Imports removed vs original |
|--------|----------------------------|
| `read_tools.py` | No `ContentGenerator` |
| `write_tools.py` | No `ContentGenerator`, no `SHAREPOINT_CONFIG` |
| `provisioning_tools.py` | No `DocumentProcessor`, no `SHAREPOINT_CONFIG` |

Each module now imports only what it actually uses.

---

## Backward Compatibility Summary

| Consumer | Before | After | Change needed |
|----------|--------|-------|---------------|
| `server.py` | `from tools.site_tools import register_site_tools` | same | None |
| `tests/test_graph_client.py` | `from utils.graph_client import GraphClient, LARGE_FILE_THRESHOLD, UPLOAD_CHUNK_SIZE` | same | None |
| `resources/site.py` | `from utils.graph_client import GraphClient` | same | None |
| Any file importing `GraphClient` | `from utils.graph_client import GraphClient` | same | None |
