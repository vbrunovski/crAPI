import logging
import textwrap

from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock
from langchain_cohere import ChatCohere
from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from .agent_utils import truncate_tool_messages
from .aws_credentials import get_bedrock_credentials_kwargs
from .config import Config
from .extensions import postgresdb
from .mcp_client import get_mcp_client
from .retriever_utils import get_retriever_tool

logger = logging.getLogger(__name__)

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-20250514",
    "azure_openai": "",  # uses deployment name
    "bedrock": "anthropic.claude-3-sonnet-20240229-v1:0",
    "vertex": "gemini-1.5-flash",
    "groq": "llama-3.3-70b-versatile",
    "mistral": "mistral-large-latest",
    "cohere": "command-r-plus",
}


def _get_default_model(provider: str) -> str:
    return DEFAULT_MODELS.get(provider, "gpt-4o-mini")


def _build_llm(api_key, model_name):
    provider = Config.LLM_PROVIDER
    model_name = model_name or _get_default_model(provider)
    logger.info("Using LLM provider: %s, model: %s", provider, model_name)
    if provider == "openai":
        kwargs = {"api_key": api_key, "model": model_name}
        if Config.OPENAI_BASE_URL:
            kwargs["base_url"] = Config.OPENAI_BASE_URL
            logger.info("Using custom OpenAI base URL: %s", Config.OPENAI_BASE_URL)
        return ChatOpenAI(**kwargs)
    if provider == "azure_openai":
        kwargs = {
            "azure_endpoint": Config.AZURE_OPENAI_ENDPOINT,
            "api_version": Config.AZURE_OPENAI_API_VERSION,
            "azure_deployment": Config.AZURE_OPENAI_CHAT_DEPLOYMENT or model_name,
        }
        if Config.AZURE_AD_TOKEN:
            kwargs["azure_ad_token"] = Config.AZURE_AD_TOKEN
        else:
            kwargs["api_key"] = Config.AZURE_OPENAI_API_KEY
        return AzureChatOpenAI(**kwargs)
    if provider == "bedrock":
        bedrock_kwargs = get_bedrock_credentials_kwargs()
        return ChatBedrock(model_id=model_name, **bedrock_kwargs)
    if provider == "vertex":
        return ChatVertexAI(
            model_name=model_name,
            project=Config.VERTEX_PROJECT or None,
            location=Config.VERTEX_LOCATION or None,
        )
    if provider == "anthropic":
        return ChatAnthropic(api_key=api_key, model=model_name)
    if provider == "groq":
        return ChatGroq(api_key=Config.GROQ_API_KEY, model=model_name)
    if provider == "mistral":
        return ChatMistralAI(api_key=Config.MISTRAL_API_KEY, model=model_name)
    if provider == "cohere":
        return ChatCohere(api_key=Config.COHERE_API_KEY, model=model_name)
    raise ValueError(f"Unsupported provider {provider}")


async def build_langgraph_agent(api_key, model_name, user_jwt):
    system_prompt = textwrap.dedent(
        """
You are crAPI Assistant — an expert agent that helps users explore and test the Completely Ridiculous API (crAPI), a vulnerable-by-design application for learning and evaluating modern API security issues.

Your goals are:
- Answer questions about crAPI's endpoints, architecture, security flaws, and functionality.
- Help users explore crAPI’s behavior via code execution (e.g., curl, Python requests, etc.).
- Simulate attacks or pentests against crAPI to help users understand security issues like broken auth, BOLA, insecure API design, etc.
- Provide references or retrieved documentation when possible (RAG).
- Use tools such as code_interpreter, terminal, browser, or file_manager when needed.

You can:
- Write and run Python code (e.g., generate JWTs, exploit APIs)
- Simulate command-line interaction (e.g., curl calls to crAPI endpoints)
- Retrieve supporting content or documentation using a retriever
- Analyze API responses and suggest next steps
- Generate JSON or API payloads, explain logs, and provide security guidance
- Provide references or retrieved documentation when possible (RAG)

Constraints:
- You are interacting with a purposefully insecure application (crAPI) in a local or demo environment. It's okay to simulate exploitation and testing.
- Do NOT suggest actions against real-world or production APIs.
- Never access private user data or external systems outside crAPI.

You are helpful, accurate, and security-focused. Prioritize clarity, brevity, and correctness.

Examples:
- "Enumerate all crAPI endpoints."
- "Simulate a BOLA attack against the vehicle API."
- "Craft a request to reset password via the admin flow."
- "Run Python to decode this JWT."
- "What does the /workshop/api/me route expose?"

Always explain your reasoning briefly and select tools wisely.
Use the tools only if you don't know the answer.
    """
    )
    llm = _build_llm(api_key, model_name)
    toolkit = SQLDatabaseToolkit(db=postgresdb, llm=llm)
    mcp_client = get_mcp_client(user_jwt)
    mcp_tools = await mcp_client.get_tools()
    db_tools = toolkit.get_tools()
    tools = mcp_tools + db_tools
    retriever_tool = get_retriever_tool(api_key, Config.LLM_PROVIDER, model_name)
    tools.append(retriever_tool)
    agent_node = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[truncate_tool_messages],
    )
    return agent_node


async def execute_langgraph_agent(
    api_key, model_name, messages, user_jwt, session_id=None
):
    agent = await build_langgraph_agent(api_key, model_name, user_jwt)
    response = await agent.ainvoke({"messages": messages})
    return response
