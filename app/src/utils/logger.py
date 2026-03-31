"""Structured logging utility.

Emits single-line JSON log entries with timestamp, level, message,
request_id, and function_name fields for CloudWatch Logs Insights.
"""

import json
import logging
import os
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formatter that outputs single-line JSON log entries."""

    def __init__(self, request_id: str = "", function_name: str = ""):
        super().__init__()
        self.request_id = request_id
        self.function_name = function_name

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": self.request_id,
            "function_name": self.function_name,
        }
        return json.dumps(entry, default=str)


def get_logger(
    name: str, request_id: str = "", function_name: str = ""
) -> logging.Logger:
    """Return a logger that emits structured JSON log entries.

    Each entry contains:
    - timestamp: ISO 8601 UTC
    - level: INFO/WARNING/ERROR
    - message: human-readable description
    - request_id: Lambda context aws_request_id
    - function_name: Lambda context function_name
    """
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)

    # Clear existing handlers so the formatter is always up-to-date
    # with the current request_id / function_name.
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter(request_id=request_id, function_name=function_name))
    logger.addHandler(handler)

    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger
