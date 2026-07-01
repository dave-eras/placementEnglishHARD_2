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


def _save_dynamodb(item: dict[str, Any], table_name: str) -> None:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 is required when DYNAMODB_TABLE is configured.") from exc

    region_name = _setting("AWS_REGION", "eu-west-3")
    dynamodb = boto3.resource("dynamodb", region_name=region_name)
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
