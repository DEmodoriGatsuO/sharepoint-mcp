"""Main implementation of the SharePoint MCP Server."""
import os
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from auth.sharepoint_auth import SharePointContext, get_auth_context
from config.settings import APP_NAME, DEBUG

logging_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    level=logging_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sharepoint_mcp")

@asynccontextmanager
async def sharepoint_lifespan(server: FastMCP) -> AsyncIterator[SharePointContext]:
    logger.info("Initializing SharePoint connection...")
    try:
        context = await get_auth_context()
        logger.info(f"Authentication successful. Token expiry: {context.token_expiry}")
        yield context
    except Exception as e:
        logger.error(f"Error during SharePoint authentication: {e}")
        error_context = SharePointContext(
            access_token="error",
            token_expiry=datetime.now() + timedelta(seconds=10),
            graph_url="https://graph.microsoft.com/v1.0",
        )
        logger.warning("Using error context due to authentication failure")
        yield error_context
    finally:
        logger.info("Ending SharePoint connection...")

mcp = FastMCP(APP_NAME, lifespan=sharepoint_lifespan)

from tools.site_tools import register_site_tools
register_site_tools(mcp)

app = mcp.streamable_http_app()

# Patch transport security to allow Railway host
from mcp.server import transport_security
transport_security.ALLOWED_HOSTS = None

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
