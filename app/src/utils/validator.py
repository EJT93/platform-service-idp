"""Request validation utilities."""

REQUIRED_FIELDS = ("name", "owner")

LENGTH_LIMITS = {
    "name": 128,
    "owner": 128,
    "description": 1024,
    "runtime": 64,
}

KNOWN_FIELDS = set(LENGTH_LIMITS.keys())


def validate_create_service(data: dict) -> list[str]:
    """Validate a POST /services request body.

    Checks:
    - Required fields: name, owner
    - All field values must be strings
    - Length limits: name (128), owner (128), description (1024), runtime (64)
    - Non-empty after stripping whitespace for required fields

    Returns list of all validation errors (empty list = valid).
    """
    errors: list[str] = []

    # Check required fields are present
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate each known field that is present
    for field in KNOWN_FIELDS:
        if field not in data:
            continue

        value = data[field]

        # Type check
        if not isinstance(value, str):
            errors.append(f"Field '{field}' must be a string")
            continue

        # Non-empty / whitespace-only check for required fields
        if field in REQUIRED_FIELDS and not value.strip():
            errors.append(f"Field '{field}' must not be empty")
            continue

        # Length limit check
        limit = LENGTH_LIMITS[field]
        if len(value) > limit:
            errors.append(
                f"Field '{field}' exceeds maximum length of {limit} characters"
            )

    return errors
