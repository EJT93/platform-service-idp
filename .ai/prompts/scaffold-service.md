# Prompt: Scaffold the Platform Service Catalog API

## Context

You are building a self-service Platform Service Catalog API. Read the steering files in `.ai/steering/` before generating any code. Follow the architecture, engineering standards, and Python service standards exactly.

## Task

Generate the Python Lambda service under `app/src/` with the following structure:

```
app/src/
├── handlers/service_handler.py
├── models/service_model.py
├── services/dynamodb_service.py
├── utils/logger.py
└── utils/validator.py
```

## Requirements

### Handler (`handlers/service_handler.py`)
- Single Lambda handler function that routes based on HTTP method and path.
- Supported routes: POST /services, GET /services, GET /services/{id}, DELETE /services/{id}.
- Delegates all business logic to the service layer.
- Returns structured JSON responses with appropriate status codes.
- Catches and handles all exceptions. Never returns raw stack traces.

### Model (`models/service_model.py`)
- `ServiceRecord` class with fields: service_id (UUID), name, owner, description, runtime, created_at, updated_at.
- `to_dict()` and `from_dict()` methods.
- Server-side UUID generation if service_id not provided.
- ISO 8601 timestamps.

### Service (`services/dynamodb_service.py`)
- `DynamoDBService` class with methods: put_item, get_item, list_items, delete_item.
- Table name from `DYNAMODB_TABLE` environment variable.
- boto3 DynamoDB resource client initialized at module level.
- Structured logging for all operations.

### Logger (`utils/logger.py`)
- Configurable structured JSON logger.
- Log level from `LOG_LEVEL` environment variable.
- Outputs JSON with: timestamp, level, message, and any extra fields passed.

### Validator (`utils/validator.py`)
- `validate_create_service(data)` function.
- Checks required fields: name, owner.
- Returns list of error strings. Empty list means valid.

## Constraints

- Do not add Flask, FastAPI, or any web framework.
- Do not add pydantic unless it meaningfully simplifies validation.
- Do not create more files than listed above.
- Do not add features beyond the four endpoints listed.
- Follow the Python service standards in `.ai/steering/python-service-standards.md`.

## Also Generate

- `app/tests/test_handler.py` — unit tests for the handler with mocked service layer.
- `app/tests/test_service.py` — unit tests for the DynamoDB service with mocked boto3.
- `app/tests/test_validator.py` — unit tests for input validation.
- `app/requirements.txt` — minimal dependencies.
