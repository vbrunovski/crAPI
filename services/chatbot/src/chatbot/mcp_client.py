import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient(
    {
        "crapi": {
            "transport": "streamable_http",
            "url": "http://localhost:5500/mcp/",
            "headers": {},
        },
    }
)
