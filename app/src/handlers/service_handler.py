"""Lambda API handler for the platform service."""

import json
import logging
from models.service_model import ServiceItem
from services.dynamodb_service import DynamoDBService
from utils.logger import get_logger
from utils.validator import validate_request

logger = get_logger(__name__)
db_service = DynamoDBService()


def handler(event, context):
    """Main Lambda handler for API Gateway events."""
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    body = event.get("body")

    logger.info("Received %s %s", http_method, path)

    try:
        if http_method == "GET" and path.startswith("/items/"):
            item_id = path.split("/")[-1]
            item = db_service.get_item(item_id)
            if not item:
                return _response(404, {"error": "Item not found"})
            return _response(200, item)

        elif http_method == "GET" and path == "/items":
            items = db_service.list_items()
            return _response(200, items)

        elif http_method == "POST" and path == "/items":
            data = json.loads(body) if body else {}
            errors = validate_request(data, required_fields=["name"])
            if errors:
                return _response(400, {"errors": errors})
            item = ServiceItem.from_dict(data)
            created = db_service.put_item(item.to_dict())
            return _response(201, created)

        elif http_method == "DELETE" and path.startswith("/items/"):
            item_id = path.split("/")[-1]
            db_service.delete_item(item_id)
            return _response(204, None)

        else:
            return _response(404, {"error": "Route not found"})

    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON"})
    except Exception as e:
        logger.exception("Unhandled error")
        return _response(500, {"error": str(e)})


def _response(status_code, body):
    """Build an API Gateway compatible response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body else "",
    }
