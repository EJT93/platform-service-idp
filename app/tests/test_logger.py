"""Property-based tests for structured logger."""

import json
import logging

from hypothesis import given, settings
from hypothesis import strategies as st

from src.utils.logger import get_logger, JSONFormatter


# --- Strategies ---

# Strategy for log levels the handler uses
log_levels = st.sampled_from(["INFO", "WARNING", "ERROR"])

# Strategy for arbitrary message, request_id, and function_name strings
arbitrary_text = st.text(min_size=0, max_size=200)


# Feature: idp-mvp-phase1, Property 8: Structured log output format
# **Validates: Requirements 6.1**
@given(
    message=arbitrary_text,
    request_id=arbitrary_text,
    function_name=arbitrary_text,
    level=log_levels,
)
@settings(max_examples=100)
def test_structured_log_output_format(message, request_id, function_name, level):
    """For any log message emitted by the Structured_Logger, the output SHALL be
    a valid JSON string containing the keys timestamp, level, message, request_id,
    and function_name."""
    # Create a formatter with the given request_id and function_name
    formatter = JSONFormatter(request_id=request_id, function_name=function_name)

    # Build a LogRecord at the chosen level
    numeric_level = getattr(logging, level)
    record = logging.LogRecord(
        name="test",
        level=numeric_level,
        pathname="",
        lineno=0,
        msg=message,
        args=None,
        exc_info=None,
    )

    # Format the record
    output = formatter.format(record)

    # Output must be valid single-line JSON
    assert "\n" not in output, "Log output must be single-line"
    parsed = json.loads(output)

    # Must contain all 5 required keys
    required_keys = {"timestamp", "level", "message", "request_id", "function_name"}
    assert required_keys.issubset(parsed.keys()), (
        f"Missing keys: {required_keys - parsed.keys()}"
    )

    # Verify values match what was provided
    assert parsed["level"] == level
    assert parsed["message"] == message
    assert parsed["request_id"] == request_id
    assert parsed["function_name"] == function_name
