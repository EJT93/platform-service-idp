"""Unit tests for the service handler."""

import json
import pytest
from unittest.mock import patch, MagicMock

# Patch boto3 before importing handler
with patch("boto3.resource"):
    from src.handlers.service_handler import handler


def _event(method, path, body=None):
    return {
        "httpMethod": method,
        "path": path,
        "body": json.dumps(body) if body else None,
    }


@patch("src.handlers.service_handler.db_service")
def test_get_item_not_found(mock_db):
    mock_db.get_item.return_value = None
    resp = handler(_event("GET", "/items/123"), {})
    assert resp["statusCode"] == 404


@patch("src.handlers.service_handler.db_service")
def test_create_item(mock_db):
    mock_db.put_item.return_value = {"item_id": "1", "name": "test"}
    resp = handler(_event("POST", "/items", {"name": "test"}), {})
    assert resp["statusCode"] == 201


@patch("src.handlers.service_handler.db_service")
def test_create_item_missing_name(mock_db):
    resp = handler(_event("POST", "/items", {}), {})
    assert resp["statusCode"] == 400


def test_invalid_route():
    with patch("boto3.resource"):
        resp = handler(_event("PATCH", "/unknown"), {})
    assert resp["statusCode"] == 404
