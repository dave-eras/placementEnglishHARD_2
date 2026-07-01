import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import streamlit as st

LOCAL_RESPONSES_PATH = Path(__file__).resolve().parent.parent / "local_responses.jsonl"


def _setting(name: str, default: str = "") -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass

    return os.environ.get(name, default)


def _payload(**kwargs: Any) -> dict[str, Any]:
    response = kwargs.get("response", "")
    correct = kwargs.get("correct", "")
    return {
        **kwargs,
        "is_correct": response == correct,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _save_local(item: dict[str, Any]) -> None:
    with LOCAL_RESPONSES_PATH.open("a", encoding="utf-8") as response_file:
        response_file.write(json.dumps(item, ensure_ascii=False) + "\n")


def _boto3_kwargs() -> dict[str, str]:
    kwargs: dict[str, str] = {"region_name": _setting("AWS_REGION", "eu-west-3")}

    access_key_id = _setting("AWS_ACCESS_KEY_ID")
    secret_access_key = _setting("AWS_SECRET_ACCESS_KEY")
    if access_key_id and secret_access_key:
        kwargs["aws_access_key_id"] = access_key_id
        kwargs["aws_secret_access_key"] = secret_access_key

    session_token = _setting("AWS_SESSION_TOKEN")
    if session_token:
        kwargs["aws_session_token"] = session_token

    return kwargs


def _save_dynamodb(item: dict[str, Any], table_name: str) -> None:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 is required when DYNAMODB_TABLE is configured.") from exc

    boto3_kwargs = _boto3_kwargs()
    if "aws_access_key_id" not in boto3_kwargs:
        raise RuntimeError(
            "DYNAMODB_TABLE is set but AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are missing."
        )

    dynamodb = boto3.resource("dynamodb", **boto3_kwargs)
    table = dynamodb.Table(table_name)

    dynamo_item = {
        key: Decimal(str(value)) if isinstance(value, float) else value
        for key, value in item.items()
    }
    table.put_item(Item=dynamo_item)


def save_response(**kwargs: Any) -> None:
    item = _payload(**kwargs)
    table_name = _setting("DYNAMODB_TABLE")

    if table_name:
        _save_dynamodb(item, table_name)
        return

    _save_local(item)
