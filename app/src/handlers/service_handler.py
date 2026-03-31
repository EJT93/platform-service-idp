"""Lambda API handler for the platform service catalog."""

import json

import botocore.exceptions
from models.service_model import ServiceRecord
from services.dynamodb_service import DynamoDBService
from utils.logger import get_logger
from utils.validator import validate_create_service

db_service = DynamoDBService()


def handler(event: dict, context) -> dict:
    """Main Lambda handler for API Gateway HTTP API v2 events."""
    http_method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")
    path_params = event.get("pathParameters") or {}
    body = event.get("body")

    request_id = getattr(context, "aws_request_id", "unknown")
    function_name = getattr(context, "function_name", "unknown")
    logger = get_logger(__name__, request_id=request_id, function_name=function_name)

    logger.info("Received %s %s", http_method, path)

    try:
        if http_method == "POST" and path == "/services":
            data = json.loads(body) if body else {}
            errors = validate_create_service(data)
            if errors:
                logger.warning("Validation failed: %s", errors)
                return _response(400, {"errors": errors})
            record = ServiceRecord.from_dict(data)
            created = db_service.create_service(record.to_dict())
            logger.info("Created service %s", created.get("service_id"))
            return _response(201, created)

        elif http_method == "GET" and path == "/services":
            services = db_service.list_services()
            logger.info("Listed %d services", len(services))
            return _response(200, services)

        elif http_method == "GET" and path.startswith("/services/"):
            service_id = path_params.get("service_id") or path.split("/services/")[-1]
            if not service_id:
                return _response(400, {"error": "Missing service_id"})
            service = db_service.get_service(service_id)
            if not service:
                logger.warning("Service not found: %s", service_id)
                return _response(404, {"error": "Service not found"})
            logger.info("Retrieved service %s", service_id)
            return _response(200, service)

        elif http_method == "DELETE" and path.startswith("/services/"):
            service_id = path_params.get("service_id") or path.split("/services/")[-1]
            if not service_id:
                return _response(400, {"error": "Missing service_id"})
            db_service.delete_service(service_id)
            logger.info("Deleted service %s", service_id)
            return _response(204, None)

        else:
            logger.warning("Route not found: %s %s", http_method, path)
            return _response(404, {"error": "Route not found"})

    except json.JSONDecodeError:
        logger.warning("Invalid JSON in request body")
        return _response(400, {"error": "Invalid JSON"})
    except botocore.exceptions.ClientError:
        logger.exception("DynamoDB error")
        return _response(500, {"error": "Internal server error"})
    except Exception:
        logger.exception("Unhandled error")
        return _response(500, {"error": "Internal server error"})


def _response(status_code: int, body) -> dict:
    """Build an API Gateway compatible response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body else "",
    }
