import uuid

from quart import after_this_request, request

from .config import Config
from .extensions import db

SESSION_COOKIE_NAME = "chat_session_id"


async def get_or_create_session_id():
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        session_id = str(uuid.uuid4())

        @after_this_request
        def after_index(response):
            response.set_cookie(
                SESSION_COOKIE_NAME, session_id, httponly=True, secure=True
            )
            return response

    return session_id


def _get_api_key_field(provider: str) -> str | None:
    if provider == "openai":
        return "openai_api_key"
    if provider == "anthropic":
        return "anthropic_api_key"
    return None


async def store_api_key(session_id, api_key, provider: str):
    key_field = _get_api_key_field(provider)
    if not key_field:
        return
    await db.sessions.update_one(
        {"session_id": session_id}, {"$set": {key_field: api_key}}, upsert=True
    )


async def get_api_key(session_id):
    provider = Config.LLM_PROVIDER
    key_field = _get_api_key_field(provider)
    if provider == "openai" and Config.OPENAI_API_KEY:
        return Config.OPENAI_API_KEY
    if provider == "anthropic" and Config.ANTHROPIC_API_KEY:
        return Config.ANTHROPIC_API_KEY
    if not key_field:
        return None
    doc = await db.sessions.find_one({"session_id": session_id})
    if not doc:
        return None
    if key_field not in doc:
        return None
    return doc[key_field]


async def delete_api_key(session_id):
    updates = {}
    for key_field in ("openai_api_key", "anthropic_api_key"):
        updates[key_field] = ""
    await db.sessions.update_one(
        {"session_id": session_id}, {"$unset": updates}
    )


async def store_model_name(session_id, model_name):
    await db.sessions.update_one(
        {"session_id": session_id}, {"$set": {"model_name": model_name}}, upsert=True
    )


async def get_model_name(session_id):
    doc = await db.sessions.find_one({"session_id": session_id})
    if not doc:
        return Config.LLM_MODEL_NAME
    if "model_name" not in doc:
        return Config.LLM_MODEL_NAME
    return doc["model_name"]


async def get_user_jwt() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.replace("Bearer ", "")
    return None
