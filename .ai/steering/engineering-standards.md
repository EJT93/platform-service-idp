# Engineering Standards

## Code Organization

The service follows a layered architecture within a single Lambda function:

```
handlers/     → Lambda entry points. Parse events, call services, return responses.
models/       → Data models and validation schemas. No business logic.
services/     → Business logic and AWS SDK interactions. Testable in isolation.
utils/        → Shared utilities: logging, validation helpers, constants.
```

Each layer has a single responsibility. Handlers do not call DynamoDB directly. Models do not import boto3. Services do not format HTTP responses.

## Separation of Concerns

- Handlers own HTTP semantics (status codes, headers, request parsing).
- Services own business logic and data access.
- Models own data shape, validation, and serialization.
- Utils own cross-cutting concerns (logging, common validation).

If you find yourself importing boto3 in a handler, you are violating this boundary.

## Naming Conventions

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Terraform resources: `snake_case` with descriptive names
- Terraform modules: `snake_case` directory names
- API paths: `/lowercase-kebab-case`
- DynamoDB attributes: `snake_case`

## Simplicity Requirements

- Prefer standard library over third-party packages.
- Prefer flat structures over deep nesting.
- Prefer explicit code over clever abstractions.
- If a function is longer than 30 lines, consider splitting it.
- If a module has more than 5 imports from the same package, reconsider the dependency.
- Every function should be explainable in one sentence.

## Error Handling

- Never let unhandled exceptions reach the client as raw stack traces.
- Catch specific exceptions, not bare `except:`.
- Return structured JSON error responses with appropriate HTTP status codes.
- Log all errors with stack traces at ERROR level.
- Use 400 for client errors (bad input, missing fields).
- Use 404 for not found.
- Use 500 for unexpected server errors.
- Include a human-readable `error` field in error responses.

## Testing Expectations

- Unit tests for service layer logic using mocked AWS clients.
- Unit tests for input validation.
- Handler tests with mocked service layer.
- Use pytest as the test runner.
- Mock boto3 resources, do not call real AWS services in tests.
- Aim for coverage of happy paths and key error paths.
- Do not write tests for trivial getters/setters or data classes.
- At least one Terraform test (`tftest.hcl`) validating a module.

## Local Development

- Use `pip install -r requirements.txt` for dependency management.
- Use `python -m pytest tests/` to run tests.
- Use environment variables for configuration (table name, log level, etc.).
- Do not require Docker, LocalStack, or SAM CLI for running unit tests.
- Integration testing against real AWS is optional and not required for MVP.

## Dependency Rules

- boto3 is provided by the Lambda runtime. Include it in requirements.txt for local dev/testing only.
- Do not add frameworks (Flask, FastAPI, Chalice) unless they provide clear value over raw Lambda handler.
- If you add a dependency, document why in a code comment or DECISIONS.md.
- Prefer fewer dependencies. Every dependency is a maintenance burden.

## Maintainability

- Code should be readable by someone unfamiliar with the project in under 10 minutes.
- Avoid magic strings. Use constants or enums.
- Avoid deep inheritance hierarchies. Prefer composition.
- Keep the total line count low. This is an MVP, not a framework.

## Anti-Patterns to Avoid

- God handlers that do everything (routing, validation, DB access, response formatting).
- Premature abstraction (don't build a "plugin system" for one service).
- Over-engineering error handling (custom exception hierarchies for 3 endpoints).
- Adding features not in the MVP definition.
- Creating utility functions used only once.
- Wrapping boto3 in unnecessary abstraction layers beyond the service class.
- Using classes where simple functions suffice.
