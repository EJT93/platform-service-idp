# Python Service Standards

## Python Version

Target Python 3.12. Use features available in 3.12 (f-strings, walrus operator, match statements if they improve clarity). Do not use features from 3.13+.

## Package and Module Layout

```
app/
├── src/
│   ├── handlers/
│   │   └── service_handler.py    # Single handler for all routes
│   ├── models/
│   │   └── service_model.py      # ServiceRecord data model
│   ├── services/
│   │   └── dynamodb_service.py   # DynamoDB CRUD operations
│   │   └── s3_service.py         # S3 audit writes (optional)
│   └── utils/
│       ├── logger.py             # Structured JSON logger
│       └── validator.py          # Input validation helpers
├── tests/
│   ├── test_handler.py
│   ├── test_service.py
│   └── test_validator.py
├── requirements.txt
└── Dockerfile                    # Optional
```

Do not add `__init__.py` files unless needed for import resolution. Keep the structure flat.

## Handler / Service / Model / Utils Separation

Handlers:
- Accept Lambda event and context.
- Extract HTTP method, path, body, and path parameters.
- Call the appropriate service method.
- Return a dict with `statusCode`, `headers`, and `body`.
- Do not contain business logic or direct AWS SDK calls.

Services:
- Contain all business logic and AWS SDK interactions.
- Accept and return plain Python dicts or model instances.
- Are stateless — instantiate clients at module level for Lambda reuse.
- Are independently testable with mocked AWS clients.

Models:
- Define the shape of data (fields, types, defaults).
- Handle serialization to/from dict.
- Handle ID generation (UUID) and timestamp defaults.
- Do not import boto3 or any AWS SDK.

Utils:
- Cross-cutting concerns only.
- Logger configuration.
- Generic validation functions (required fields, type checks).
- Do not contain business logic.

## Input Validation

- Validate all incoming request bodies before processing.
- Check for required fields and reject with 400 if missing.
- Check field types where practical (e.g., `name` must be a non-empty string).
- Do not trust any input from the client.
- Return a list of validation errors, not just the first one.
- Validation logic lives in `utils/validator.py` or in the model layer.

## Response Structure

All responses must be JSON with consistent structure.

Success responses:
```json
{
  "statusCode": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"service_id\": \"...\", \"name\": \"...\"}"
}
```

Error responses:
```json
{
  "statusCode": 400,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"error\": \"Missing required field: name\"}"
}
```

The `body` field is always a JSON string (API Gateway requirement). Use `json.dumps()`.

## Exception Handling

- Catch `json.JSONDecodeError` for malformed request bodies → 400.
- Catch `KeyError` / `ValueError` for missing or invalid data → 400.
- Catch `botocore.exceptions.ClientError` for AWS errors → log and return 500.
- Catch `Exception` as a final fallback → log with traceback and return 500.
- Never return raw exception messages to the client in production. Use generic messages for 500 errors.
- Always log the full exception with `logger.exception()` for debugging.

## Structured Logging

- Use Python's `logging` module configured to output JSON.
- Every log entry must include: `timestamp`, `level`, `message`, `request_id`.
- Include `function_name` from the Lambda context.
- Include `service_id` or other entity identifiers when processing specific records.
- Log at INFO level for successful operations.
- Log at WARNING level for client errors (bad input).
- Log at ERROR level for server errors with full stack traces.
- Configure log level via `LOG_LEVEL` environment variable.

## Test Organization

- One test file per source module (e.g., `test_handler.py`, `test_service.py`).
- Use `unittest.mock.patch` to mock boto3 resources and service dependencies.
- Test happy paths: successful create, read, list, delete.
- Test error paths: missing fields, not found, invalid JSON.
- Do not test boto3 itself. Mock it and verify your code calls it correctly.
- Use `pytest` fixtures for common test setup.

## Requirements Management

- `requirements.txt` for simplicity. No poetry, pipenv, or pyproject.toml unless justified.
- Pin major versions (e.g., `boto3>=1.28.0`).
- Keep the list short. For MVP, you likely need only `boto3` and `pytest`.
- Add `ruff` for linting if CI includes a lint step.

## Type Hints

- Use type hints for function signatures.
- Do not obsess over typing every internal variable.
- Use `dict`, `list`, `str`, `int`, `bool`, `None` — not `Dict`, `List` from `typing` (Python 3.12 supports built-in generics).
- Type hints are documentation, not enforcement. Keep them practical.

## Serialization

- Use `json.dumps()` and `json.loads()` from the standard library.
- Model classes should have `to_dict()` and `from_dict()` class methods.
- DynamoDB items are dicts. Convert between model instances and dicts at the service layer boundary.
- Use ISO 8601 format for all timestamps (`datetime.now(timezone.utc).isoformat()`).

## Idempotency and Duplicate Handling

- Use client-generated UUIDs for `service_id` if provided, otherwise generate server-side.
- DynamoDB `PutItem` is naturally idempotent (same key overwrites).
- For the MVP, do not implement conditional writes or optimistic locking.
- If duplicate detection becomes important, add a GSI on `name` + `owner` later.
- Document this as a known limitation in DECISIONS.md if relevant.
