import httpx
from fastmcp import FastMCP, settings
import json
import os
import logging
import time
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

WEB_SERVICE = os.environ.get("WEB_SERVICE", "crapi-web")
IDENTITY_SERVICE = os.environ.get("IDENTITY_SERVICE", "crapi-identity:8080")
TLS_ENABLED = os.environ.get("TLS_ENABLED", "false").lower() in ("true", "1", "yes")
BASE_URL = f"{'https' if TLS_ENABLED else 'http'}://{WEB_SERVICE}"
BASE_IDENTITY_URL = f"{'https' if TLS_ENABLED else 'http'}://{IDENTITY_SERVICE}"

API_USER = os.environ.get("API_USER", "admin@example.com")
API_PASSWORD = os.environ.get("API_PASSWORD", "Admin!123")
API_URL = f"{'https' if TLS_ENABLED else 'http'}://{WEB_SERVICE}"

API_KEY = None
API_AUTH_TYPE = "ApiKey"

def get_api_key():
    global API_KEY
    # Try 5 times to get API key
    MAX_ATTEMPTS = 5
    for i in range(MAX_ATTEMPTS):
        logger.info(f"Attempt {i+1} to get API key...")
        if API_KEY is None:
            login_body = {"email": API_USER, "password": API_PASSWORD}
            apikey_url = f"{BASE_IDENTITY_URL}/identity/management/user/apikey"
            headers = {
                "Content-Type": "application/json",
            }
            with httpx.Client(
                base_url=API_URL,
                headers=headers,
            ) as client:
                response = client.post(apikey_url, json=login_body)
                if response.status_code != 200:
                    if i == MAX_ATTEMPTS - 1:
                        logger.error(f"Failed to get API key after {i+1} attempts: {response.status_code} {response.text}")
                        raise Exception(f"Failed to get API key after {i+1} attempts: {response.status_code} {response.text}")
                    logger.error(f"Failed to get API key in attempt {i+1}: {response.status_code} {response.text}. Sleeping for {i} seconds...")
                    time.sleep(i)
                response_json = response.json()
                logger.info(f"Response: {response_json}")
                API_KEY = response_json.get("apiKey")
                logger.info(f"Chatbot API Key: {API_KEY}")
                return API_KEY
    return API_KEY


# Async HTTP client for API calls
def get_http_client():
    """Create and configure the HTTP client with appropriate authentication."""
    headers = {
        "Authorization": "ApiKey " + get_api_key(),
    }
    return httpx.AsyncClient(
        base_url=API_URL,
        headers=headers,
    )

# Load your OpenAPI spec 
with open("/app/resources/crapi-openapi-spec.json", "r") as f:
    openapi_spec = json.load(f)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=get_http_client(),
    name="My crAPI MCP Server"
)

if __name__ == "__main__":
    mcp_server_port = int(os.environ.get("MCP_SERVER_PORT", 5500))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=mcp_server_port,)
