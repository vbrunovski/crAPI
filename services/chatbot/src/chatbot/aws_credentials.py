"""AWS credentials helper with STS assume role support."""

import logging
import os
import threading
import time
from typing import Optional

import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

from .config import Config

logger = logging.getLogger(__name__)

# Cache for assumed role credentials
_credentials_cache = {
    "credentials": None,
    "expiration": 0,
    "lock": threading.Lock(),
}

# Refresh credentials 5 minutes before expiration
CREDENTIALS_REFRESH_BUFFER_SECONDS = 300


def _get_base_session():
    """Get a boto3 session with base credentials (from env vars or instance profile)."""
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    has_access_key = bool(os.getenv("AWS_ACCESS_KEY_ID"))
    has_secret_key = bool(os.getenv("AWS_SECRET_ACCESS_KEY"))
    has_session_token = bool(os.getenv("AWS_SESSION_TOKEN"))
    logger.info(
        "[BASE_SESSION] Creating boto3 session - region: %s, has_access_key: %s, "
        "has_secret_key: %s, has_session_token: %s, will_use_instance_profile: %s",
        region, has_access_key, has_secret_key, has_session_token,
        not (has_access_key and has_secret_key)
    )
    # Use None for empty strings so boto3 falls back to instance profile/IRSA
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
        aws_session_token=os.getenv("AWS_SESSION_TOKEN") or None,
        region_name=region,
    )
    # Log the credential source boto3 is using
    creds = session.get_credentials()
    if creds:
        logger.info(
            "[BASE_SESSION] Session created - credential_method: %s, access_key_prefix: %s",
            creds.method if hasattr(creds, 'method') else 'unknown',
            creds.access_key[:8] + "..." if creds and creds.access_key else "(none)"
        )
    else:
        logger.warning("[BASE_SESSION] Session created but NO credentials found!")
    return session


def _assume_role() -> dict:
    """Assume the configured IAM role and return temporary credentials."""
    role_arn = Config.AWS_ASSUME_ROLE_ARN
    external_id = Config.AWS_EXTERNAL_ID
    session_name = Config.AWS_ROLE_SESSION_NAME

    logger.info(
        "[ASSUME_ROLE] Starting assume role - role_arn: %s, session_name: %s, has_external_id: %s",
        role_arn, session_name, bool(external_id)
    )

    try:
        base_session = _get_base_session()
        logger.debug("Base session created successfully for assume role")
    except Exception as e:
        logger.error(
            "Failed to create base session for assume role - role_arn: %s, error: %s",
            role_arn, str(e)
        )
        raise

    try:
        sts_client = base_session.client("sts")
        logger.debug("STS client created successfully")
    except Exception as e:
        logger.error(
            "Failed to create STS client for assume role - role_arn: %s, error: %s",
            role_arn, str(e)
        )
        raise

    assume_role_kwargs = {
        "RoleArn": role_arn,
        "RoleSessionName": session_name,
        "DurationSeconds": 3600,  # 1 hour
    }

    if external_id:
        assume_role_kwargs["ExternalId"] = external_id
        logger.debug("External ID configured for assume role")

    logger.debug("Calling STS assume_role with kwargs: %s", {k: v for k, v in assume_role_kwargs.items() if k != "ExternalId"})

    try:
        logger.info("[ASSUME_ROLE] Calling sts:AssumeRole...")
        response = sts_client.assume_role(**assume_role_kwargs)
        credentials = response["Credentials"]

        logger.info(
            "[ASSUME_ROLE] SUCCESS - role_arn: %s, session_name: %s, expires_at: %s, "
            "assumed_role_id: %s, access_key_prefix: %s",
            role_arn,
            session_name,
            credentials["Expiration"],
            response.get("AssumedRoleUser", {}).get("AssumedRoleId", "unknown"),
            credentials["AccessKeyId"][:8] + "..." if credentials.get("AccessKeyId") else "(none)",
        )

        return {
            "access_key": credentials["AccessKeyId"],
            "secret_key": credentials["SecretAccessKey"],
            "token": credentials["SessionToken"],
            "expiry_time": credentials["Expiration"].timestamp(),
        }
    except Exception as e:
        logger.error(
            "[ASSUME_ROLE] FAILED - role_arn: %s, session_name: %s, error_type: %s, error: %s",
            role_arn, session_name, type(e).__name__, str(e)
        )
        raise


def _get_cached_credentials() -> Optional[dict]:
    """Get cached credentials if they're still valid."""
    with _credentials_cache["lock"]:
        if _credentials_cache["credentials"] is None:
            logger.debug("No cached credentials available")
            return None

        # Check if credentials are about to expire
        time_until_expiry = _credentials_cache["expiration"] - time.time()
        if time_until_expiry <= CREDENTIALS_REFRESH_BUFFER_SECONDS:
            logger.info(
                "Cached credentials expiring soon - time_until_expiry: %.0f seconds, refresh_buffer: %d seconds",
                time_until_expiry, CREDENTIALS_REFRESH_BUFFER_SECONDS
            )
            return None

        logger.debug(
            "Using cached credentials - time_until_expiry: %.0f seconds",
            time_until_expiry
        )
        return _credentials_cache["credentials"]


def _set_cached_credentials(credentials: dict) -> None:
    """Cache the credentials."""
    with _credentials_cache["lock"]:
        _credentials_cache["credentials"] = credentials
        _credentials_cache["expiration"] = credentials["expiry_time"]
        logger.debug(
            "Cached new credentials - expires_at: %s",
            credentials["expiry_time"]
        )


def get_aws_credentials() -> Optional[dict]:
    """
    Get AWS credentials, using assume role if configured.

    Returns:
        dict with 'access_key', 'secret_key', 'token' (optional), and 'region',
        or None if no credentials are configured/needed.
    """
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    logger.info(
        "[AWS_CREDS] get_aws_credentials called - region: %s, AWS_ASSUME_ROLE_ARN: %s, "
        "has_static_access_key: %s, has_static_secret_key: %s, has_bearer_token: %s",
        region,
        Config.AWS_ASSUME_ROLE_ARN or "(not set)",
        bool(os.getenv("AWS_ACCESS_KEY_ID")),
        bool(os.getenv("AWS_SECRET_ACCESS_KEY")),
        bool(Config.AWS_BEARER_TOKEN_BEDROCK)
    )

    # If assume role is configured, use it
    if Config.AWS_ASSUME_ROLE_ARN:
        logger.info(
            "[AWS_CREDS] Assume role path - role_arn: %s",
            Config.AWS_ASSUME_ROLE_ARN
        )
        # Try to use cached credentials
        cached = _get_cached_credentials()
        if cached:
            logger.info(
                "[AWS_CREDS] Using CACHED assume role credentials - access_key_prefix: %s",
                cached["access_key"][:8] + "..." if cached.get("access_key") else "(none)"
            )
            return {
                "access_key": cached["access_key"],
                "secret_key": cached["secret_key"],
                "token": cached["token"],
                "region": region,
            }

        # Assume role and cache credentials
        logger.info("[AWS_CREDS] No cached credentials, will call assume role now")
        try:
            credentials = _assume_role()
            _set_cached_credentials(credentials)
            logger.info(
                "[AWS_CREDS] Assume role succeeded - access_key_prefix: %s",
                credentials["access_key"][:8] + "..." if credentials.get("access_key") else "(none)"
            )
            return {
                "access_key": credentials["access_key"],
                "secret_key": credentials["secret_key"],
                "token": credentials["token"],
                "region": region,
            }
        except Exception as e:
            logger.error(
                "[AWS_CREDS] Assume role FAILED - role_arn: %s, error_type: %s, error: %s",
                Config.AWS_ASSUME_ROLE_ARN, type(e).__name__, str(e)
            )
            raise

    # If static credentials are provided via environment variables
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")

    if access_key and secret_key:
        logger.info(
            "[AWS_CREDS] Using STATIC credentials from env - access_key_prefix: %s, has_session_token: %s",
            access_key[:8] + "..." if access_key else "(none)",
            bool(session_token)
        )
        result = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
        }
        if session_token:
            result["token"] = session_token
        return result

    # Return None to use default credential chain (instance profile, etc.)
    logger.info("[AWS_CREDS] No credentials found, returning None (will use default chain)")
    return None


def get_boto3_session() -> boto3.Session:
    """
    Get a boto3 session with the appropriate credentials.

    This handles assume role if configured, otherwise uses the default credential chain.
    """
    logger.debug("Creating boto3 session")
    credentials = get_aws_credentials()

    if credentials:
        logger.debug(
            "Creating boto3 session with explicit credentials - region: %s, has_token: %s",
            credentials.get("region"), bool(credentials.get("token"))
        )
        return boto3.Session(
            aws_access_key_id=credentials["access_key"],
            aws_secret_access_key=credentials["secret_key"],
            aws_session_token=credentials.get("token"),
            region_name=credentials.get("region"),
        )

    # Use default credential chain
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    logger.debug("Creating boto3 session with default credential chain - region: %s", region)
    return boto3.Session(region_name=region)


def get_bedrock_credentials_kwargs() -> dict:
    """
    Get kwargs to pass to ChatBedrock or BedrockEmbeddings for credentials.

    Returns a dict that can be unpacked into the constructor.
    """
    logger.info("[BEDROCK_KWARGS] get_bedrock_credentials_kwargs called")
    credentials = get_aws_credentials()
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")

    kwargs = {}

    if region:
        kwargs["region_name"] = region

    if credentials:
        kwargs["credentials_profile_name"] = None  # Disable profile lookup
        kwargs["aws_access_key_id"] = credentials["access_key"]
        kwargs["aws_secret_access_key"] = credentials["secret_key"]
        if credentials.get("token"):
            kwargs["aws_session_token"] = credentials["token"]
        logger.info(
            "[BEDROCK_KWARGS] Explicit credentials obtained - region: %s, has_session_token: %s, "
            "credential_source: %s, access_key_prefix: %s",
            region,
            bool(credentials.get("token")),
            "assume_role" if Config.AWS_ASSUME_ROLE_ARN else "static_or_default",
            credentials["access_key"][:8] + "..." if credentials.get("access_key") else "(none)"
        )
    else:
        logger.info(
            "[BEDROCK_KWARGS] No explicit credentials, will use default chain - region: %s",
            region
        )

    # Log final kwargs (without secrets)
    safe_kwargs = {k: v for k, v in kwargs.items() if "secret" not in k.lower()}
    if "aws_access_key_id" in kwargs:
        safe_kwargs["aws_access_key_id"] = kwargs["aws_access_key_id"][:8] + "..."
    if "aws_session_token" in kwargs:
        safe_kwargs["aws_session_token"] = "(set)"
    logger.info("[BEDROCK_KWARGS] Returning kwargs: %s", safe_kwargs)

    return kwargs
