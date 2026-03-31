"""Property-based tests for the service handler."""

import json
import sys

# Module aliasing: the handler imports from bare module names (e.g.
# ``from models.service_model import ServiceRecord``) which resolve when
# ``app/src`` is on ``sys.path`` (Lambda runtime).  Under test with
# ``PYTHONPATH=app`` we alias the bare names to their ``src.*`` counterparts.
#
# The aliases for ``utils`` must be registered BEFORE importing modules that
# depend on them (e.g. ``dynamodb_service`` does ``from utils.logger …``).
import src.utils
import src.utils.logger
import src.utils.validator

sys.modules.setdefault("utils", src.utils)
sys.modules.setdefault("utils.logger", src.utils.logger)
sys.modules.setdefault("utils.validator", src.utils.validator)

import src.models
import src.models.service_model

sys.modules.setdefault("models", src.models)
sys.modules.setdefault("models.service_model", src.models.service_model)

import src.services
import src.services.dynamodb_service

sys.modules.setdefault("services", src.services)
sys.modules.setdefault("services.dynamodb_service", src.services.dynamodb_service)

from unittest.mock import patch, MagicMock

# Patch boto3 before importing handler so DynamoDBService.__init__ doesn't
# attempt a real AWS connection.
with patch("boto3.resource"):
    from src.handlers.service_handler import handler

from hypothesis import given, settings, assume
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeContext:
    """Minimal Lambda context stub."""
    aws_request_id = "test-request-id"
    function_name = "test-function"


def _v2_event(method, path, body=None, path_params=None):
    """Build an API Gateway HTTP API v2 proxy event."""
    return {
        "requestContext": {"http": {"method": method}},
        "rawPath": path,
        "pathParameters": path_params,
        "body": json.dumps(body) if body else None,
    }


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Exception types that could plausibly occur during request processing.
_exception_types = st.sampled_from([RuntimeError, ValueError, TypeError, KeyError, OSError])

# Random exception messages — we later assert these do NOT leak into the response.
_exception_messages = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=1,
    max_size=200,
)

# Valid routes that exercise each handler branch (POST, GET list, GET single, DELETE).
_valid_routes = st.sampled_from([
    ("POST", "/services", {"name": "svc", "owner": "team"}, None),
    ("GET", "/services", None, None),
    ("GET", "/services/abc-123", None, {"service_id": "abc-123"}),
    ("DELETE", "/services/abc-123", None, {"service_id": "abc-123"}),
])

# HTTP methods that are NOT used by any defined route.
_unknown_methods = st.sampled_from(["PATCH", "PUT", "OPTIONS", "HEAD"])

# Paths that definitely don't match /services or /services/{id}.
_unknown_paths = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=0,
    max_size=200,
).filter(lambda p: not p.startswith("/services"))


# ---------------------------------------------------------------------------
# Property 9: Error responses are well-formed JSON with no leaked internals
# Feature: idp-mvp-phase1, Property 9: Error responses are well-formed JSON with no leaked internals
# **Validates: Requirements 6.6, 7.2**
# ---------------------------------------------------------------------------

@given(
    route=_valid_routes,
    exc_type=_exception_types,
    exc_msg=_exception_messages,
)
@settings(max_examples=100)
def test_error_responses_well_formed_no_leaked_internals(route, exc_type, exc_msg):
    """For any exception raised during request processing, the resulting HTTP
    response SHALL have a JSON body containing an ``error`` field, and the
    response body SHALL NOT contain the raw exception message or stack trace."""
    method, path, body, path_params = route
    event = _v2_event(method, path, body=body, path_params=path_params)

    # Force an exception from every db_service method so that regardless of
    # which route is exercised the handler hits the except branch.
    mock_db = MagicMock()
    side_effect = exc_type(exc_msg)
    mock_db.create_service.side_effect = side_effect
    mock_db.list_services.side_effect = side_effect
    mock_db.get_service.side_effect = side_effect
    mock_db.delete_service.side_effect = side_effect

    with patch("src.handlers.service_handler.db_service", mock_db):
        resp = handler(event, FakeContext())

    # Response must be a valid JSON body with an "error" key.
    assert resp["statusCode"] >= 400, f"Expected error status, got {resp['statusCode']}"
    resp_body = json.loads(resp["body"])
    assert "error" in resp_body, f"Response body missing 'error' key: {resp_body}"

    # The raw exception message must NOT appear in the response body.
    # Only check when the message is long enough to be meaningful — very short
    # strings (e.g. single characters like "{", "e") can coincidentally appear
    # inside the fixed JSON envelope and would cause false positives.
    if len(exc_msg.strip()) > 5:
        assert exc_msg not in resp["body"], (
            f"Raw exception message leaked into response: {exc_msg!r}"
        )

    # Stack trace markers must not appear in the response body.
    assert "Traceback" not in resp["body"]
    assert "File " not in resp["body"]


# ---------------------------------------------------------------------------
# Property 10: Unknown routes return 404
# Feature: idp-mvp-phase1, Property 10: Unknown routes return 404
# **Validates: Requirements 7.1**
# ---------------------------------------------------------------------------

@given(
    method=_unknown_methods,
    path=_unknown_paths,
)
@settings(max_examples=100)
def test_unknown_routes_return_404_unknown_methods(method, path):
    """For any HTTP method not used by the API and any path that does not start
    with /services, the Handler SHALL return a 404 status code."""
    event = _v2_event(method, path)

    with patch("src.handlers.service_handler.db_service"):
        resp = handler(event, FakeContext())

    assert resp["statusCode"] == 404, (
        f"Expected 404 for {method} {path!r}, got {resp['statusCode']}"
    )


@given(
    method=st.sampled_from(["PATCH", "PUT", "OPTIONS", "HEAD"]),
    service_id=st.text(min_size=1, max_size=50),
)
@settings(max_examples=100)
def test_unknown_routes_return_404_wrong_method_valid_path(method, service_id):
    """For any HTTP method that is not GET or DELETE on /services/{id}, or not
    POST/GET on /services, the Handler SHALL return a 404 status code."""
    # Test against /services (only POST and GET are valid)
    event_base = _v2_event(method, "/services")
    with patch("src.handlers.service_handler.db_service"):
        resp = handler(event_base, FakeContext())
    assert resp["statusCode"] == 404, (
        f"Expected 404 for {method} /services, got {resp['statusCode']}"
    )

    # Test against /services/{id} (only GET and DELETE are valid)
    event_id = _v2_event(method, f"/services/{service_id}", path_params={"service_id": service_id})
    with patch("src.handlers.service_handler.db_service"):
        resp = handler(event_id, FakeContext())
    assert resp["statusCode"] == 404, (
        f"Expected 404 for {method} /services/{service_id}, got {resp['statusCode']}"
    )


# ---------------------------------------------------------------------------
# Unit Tests for Handler (Task 4.3)
# Requirements: 1.1, 1.4, 1.10, 2.1, 2.2, 2.3, 3.1, 7.1, 7.3
# ---------------------------------------------------------------------------

import botocore.exceptions
import pytest


class TestPostServices:
    """Tests for POST /services."""

    def test_post_valid_input_returns_201(self):
        """WHEN a valid POST is sent to /services, THEN 201 is returned with the created record.
        Validates: Requirements 1.1"""
        event = _v2_event("POST", "/services", body={"name": "my-svc", "owner": "team-a"})
        mock_db = MagicMock()
        mock_db.create_service.return_value = {
            "service_id": "abc-123",
            "name": "my-svc",
            "owner": "team-a",
            "description": "",
            "runtime": "",
            "created_at": "2025-01-01T00:00:00+00:00",
            "updated_at": "2025-01-01T00:00:00+00:00",
        }

        with patch("src.handlers.service_handler.db_service", mock_db):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 201
        body = json.loads(resp["body"])
        assert body["name"] == "my-svc"
        assert body["owner"] == "team-a"
        assert body["service_id"] == "abc-123"
        mock_db.create_service.assert_called_once()

    def test_invalid_json_returns_400(self):
        """WHEN the POST body is not valid JSON, THEN 400 is returned.
        Validates: Requirements 1.10"""
        event = _v2_event("POST", "/services")
        event["body"] = "not-json{{"

        with patch("src.handlers.service_handler.db_service"):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert "error" in body
        assert "Invalid JSON" in body["error"]

    def test_missing_required_fields_returns_400(self):
        """WHEN required fields are missing, THEN 400 is returned with errors list.
        Validates: Requirements 1.4"""
        event = _v2_event("POST", "/services", body={"description": "no name or owner"})

        with patch("src.handlers.service_handler.db_service"):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert "errors" in body
        assert len(body["errors"]) >= 2  # at least name and owner missing


class TestGetServices:
    """Tests for GET /services and GET /services/{id}."""

    def test_get_services_returns_200_with_list(self):
        """WHEN GET /services is called, THEN 200 is returned with a list.
        Validates: Requirements 2.1"""
        event = _v2_event("GET", "/services")
        mock_db = MagicMock()
        mock_db.list_services.return_value = [
            {"service_id": "id-1", "name": "svc-1", "owner": "team-a"},
            {"service_id": "id-2", "name": "svc-2", "owner": "team-b"},
        ]

        with patch("src.handlers.service_handler.db_service", mock_db):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert isinstance(body, list)
        assert len(body) == 2
        mock_db.list_services.assert_called_once()

    def test_get_service_by_id_returns_200(self):
        """WHEN GET /services/{id} is called with an existing id, THEN 200 is returned.
        Validates: Requirements 2.2"""
        event = _v2_event("GET", "/services/abc-123", path_params={"service_id": "abc-123"})
        mock_db = MagicMock()
        mock_db.get_service.return_value = {
            "service_id": "abc-123",
            "name": "my-svc",
            "owner": "team-a",
        }

        with patch("src.handlers.service_handler.db_service", mock_db):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["service_id"] == "abc-123"
        mock_db.get_service.assert_called_once_with("abc-123")

    def test_get_service_not_found_returns_404(self):
        """WHEN GET /services/{id} is called with a non-existent id, THEN 404 is returned.
        Validates: Requirements 2.3"""
        event = _v2_event("GET", "/services/no-such-id", path_params={"service_id": "no-such-id"})
        mock_db = MagicMock()
        mock_db.get_service.return_value = None

        with patch("src.handlers.service_handler.db_service", mock_db):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 404
        body = json.loads(resp["body"])
        assert "error" in body
        assert "not found" in body["error"].lower()


class TestDeleteService:
    """Tests for DELETE /services/{id}."""

    def test_delete_service_returns_204(self):
        """WHEN DELETE /services/{id} is called, THEN 204 is returned with empty body.
        Validates: Requirements 3.1"""
        event = _v2_event("DELETE", "/services/abc-123", path_params={"service_id": "abc-123"})
        mock_db = MagicMock()

        with patch("src.handlers.service_handler.db_service", mock_db):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 204
        assert resp["body"] == ""
        mock_db.delete_service.assert_called_once_with("abc-123")


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_dynamodb_error_returns_500_with_generic_message(self):
        """WHEN a DynamoDB operation fails, THEN 500 is returned with a generic message.
        Validates: Requirements 7.3"""
        event = _v2_event("GET", "/services")
        mock_db = MagicMock()
        mock_db.list_services.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "InternalServerError", "Message": "DynamoDB is down"}},
            "Scan",
        )

        with patch("src.handlers.service_handler.db_service", mock_db):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 500
        body = json.loads(resp["body"])
        assert body["error"] == "Internal server error"
        # Must NOT leak the actual DynamoDB error message
        assert "DynamoDB is down" not in resp["body"]

    def test_unknown_route_returns_404(self):
        """WHEN an unknown route is requested, THEN 404 is returned.
        Validates: Requirements 7.1"""
        event = _v2_event("PATCH", "/services")

        with patch("src.handlers.service_handler.db_service"):
            resp = handler(event, FakeContext())

        assert resp["statusCode"] == 404
        body = json.loads(resp["body"])
        assert "error" in body
