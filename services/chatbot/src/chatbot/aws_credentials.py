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
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"),
    )


def _assume_role() -> dict:
    """Assume the configured IAM role and return temporary credentials."""
    role_arn = Config.AWS_ASSUME_ROLE_ARN
    external_id = Config.AWS_EXTERNAL_ID
    session_name = Config.AWS_ROLE_SESSION_NAME

    logger.info("Assuming IAM role: %s", role_arn)

    base_session = _get_base_session()
    sts_client = base_session.client("sts")

    assume_role_kwargs = {
        "RoleArn": role_arn,
        "RoleSessionName": session_name,
        "DurationSeconds": 3600,  # 1 hour
    }

    if external_id:
        assume_role_kwargs["ExternalId"] = external_id

    response = sts_client.assume_role(**assume_role_kwargs)
    credentials = response["Credentials"]

    logger.info(
        "Successfully assumed role %s, expires at %s",
        role_arn,
        credentials["Expiration"],
    )

    return {
        "access_key": credentials["AccessKeyId"],
        "secret_key": credentials["SecretAccessKey"],
        "token": credentials["SessionToken"],
        "expiry_time": credentials["Expiration"].timestamp(),
    }


def _get_cached_credentials() -> Optional[dict]:
    """Get cached credentials if they're still valid."""
    with _credentials_cache["lock"]:
        if _credentials_cache["credentials"] is None:
            return None

        # Check if credentials are about to expire
        if time.time() >= _credentials_cache["expiration"] - CREDENTIALS_REFRESH_BUFFER_SECONDS:
            return None

        return _credentials_cache["credentials"]


def _set_cached_credentials(credentials: dict) -> None:
    """Cache the credentials."""
    with _credentials_cache["lock"]:
        _credentials_cache["credentials"] = credentials
        _credentials_cache["expiration"] = credentials["expiry_time"]


def get_aws_credentials() -> Optional[dict]:
    """
    Get AWS credentials, using assume role if configured.

    Returns:
        dict with 'access_key', 'secret_key', 'token' (optional), and 'region',
        or None if no credentials are configured/needed.
    """
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")

    # If assume role is configured, use it
    if Config.AWS_ASSUME_ROLE_ARN:
        # Try to use cached credentials
        cached = _get_cached_credentials()
        if cached:
            return {
                "access_key": cached["access_key"],
                "secret_key": cached["secret_key"],
                "token": cached["token"],
                "region": region,
            }

        # Assume role and cache credentials
        try:
            credentials = _assume_role()
            _set_cached_credentials(credentials)
            return {
                "access_key": credentials["access_key"],
                "secret_key": credentials["secret_key"],
                "token": credentials["token"],
                "region": region,
            }
        except Exception as e:
            logger.error("Failed to assume role %s: %s", Config.AWS_ASSUME_ROLE_ARN, e)
            raise

    # If static credentials are provided via environment variables
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")

    if access_key and secret_key:
        result = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
        }
        if session_token:
            result["token"] = session_token
        return result

    # Return None to use default credential chain (instance profile, etc.)
    return None


def get_boto3_session() -> boto3.Session:
    """
    Get a boto3 session with the appropriate credentials.

    This handles assume role if configured, otherwise uses the default credential chain.
    """
    credentials = get_aws_credentials()

    if credentials:
        return boto3.Session(
            aws_access_key_id=credentials["access_key"],
            aws_secret_access_key=credentials["secret_key"],
            aws_session_token=credentials.get("token"),
            region_name=credentials.get("region"),
        )

    # Use default credential chain
    return boto3.Session(
        region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    )


def get_bedrock_credentials_kwargs() -> dict:
    """
    Get kwargs to pass to ChatBedrock or BedrockEmbeddings for credentials.

    Returns a dict that can be unpacked into the constructor.
    """
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

    return kwargs
