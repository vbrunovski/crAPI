import httpx
from fastmcp import FastMCP, settings
import json
import os
from .config import Config
import logging
import time
from .tool_helpers import (
    get_any_api_key,
    get_chat_history_retriever,
)
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_URL = f"{'https' if Config.TLS_ENABLED else 'http'}://{Config.WEB_SERVICE}"
BASE_IDENTITY_URL = f"{'https' if Config.TLS_ENABLED else 'http'}://{Config.IDENTITY_SERVICE}"
API_KEY = None

def get_api_key():
    global API_KEY
    # Try 5 times to get client auth
    MAX_ATTEMPTS = 5
    for i in range(MAX_ATTEMPTS):
        logger.info(f"Attempt {i+1} to get API key...")
        if API_KEY is None:
            login_body = {"email": Config.API_USER, "password": Config.API_PASSWORD}
            auth_url = f"{BASE_IDENTITY_URL}/identity/management/user/apikey"
            headers = {
                "Content-Type": "application/json",
            }
            with httpx.Client(
                base_url=BASE_URL,
                headers=headers,
            ) as client:
                response = client.post(auth_url, json=login_body)
                if response.status_code != 200:
                    if i == MAX_ATTEMPTS - 1:
                        logger.error(f"Failed to get API key after {i+1} attempts: {response.status_code} {response.text}")
                        raise Exception(f"Failed to get API key after {i+1} attempts: {response.status_code} {response.text}")
                    logger.error(f"Failed to get API key in attempt {i+1}: {response.status_code} {response.text}. Sleeping for {i} seconds...")
                    time.sleep(i)
                response_json = response.json()
                logger.info(f"Response: {response_json}")
                API_KEY = response_json.get("apiKey")
                logger.info(f"MCP Server API Key: {API_KEY}")
                return API_KEY
    return API_KEY

# Async HTTP client for API calls
def get_http_client():
    """Create and configure the HTTP client with appropriate authentication."""
    headers = {
        "Authorization": "ApiKey " + get_api_key(),
    }
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers=headers,
    )

# Load your OpenAPI spec 
with open(Config.OPENAPI_SPEC, "r") as f:
    openapi_spec = json.load(f)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=get_http_client(),
    name="My crAPI MCP Server"
)

@mcp.tool(tags={"history", "search", "summary", "context"},)
async def search_chat_history(question: str) -> str:
    """Answer questions based on user chat history (summarized and semantically indexed). 
    Use this when the user asks about prior chats, what they asked earlier, or wants a summary of past conversations.    
    Answer questions based on the user's prior chat history.

    Use this tool when the user refers to anything mentioned before, asks for a summary of previous messages or sessions, 
    or references phrases like 'what I said earlier', 'things we discussed', 'my earlier question', 'until now', 'till date', 'all my conversations' or 'previously mentioned'.
    The chat history is semantically indexed and summarized using vector search."""

    logger.info(f"search_chat_history called with: {question}")
    api_key=await get_any_api_key()
    if not api_key:
        logger.error("API key is not available. Cannot search chat history.")
        return "OpenAI API key is not available. Cannot search chat history."
    retriever = await get_chat_history_retriever(api_key=api_key)
    response = await retriever.ainvoke({"query": question})
    result = response["result"]
    logger.info(f"RESULT: {result}")
    return result

if __name__ == "__main__":
    mcp_server_port = int(os.environ.get("MCP_SERVER_PORT", 5500))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=mcp_server_port,)
