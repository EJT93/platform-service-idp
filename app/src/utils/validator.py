"""Request validation utilities."""


def validate_request(data, required_fields=None):
    """Validate that required fields are present in the request data."""
    errors = []
    for field in required_fields or []:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    return errors
