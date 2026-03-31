"""DynamoDB service layer for CRUD operations."""

import os
import boto3
from utils.logger import get_logger

logger = get_logger(__name__)

ssm = boto3.client("ssm")


def _resolve_table_name() -> str:
    """Resolve table name from SSM parameter or fall back to env var."""
    ssm_param = os.environ.get("DYNAMODB_TABLE_SSM")
    if ssm_param:
        try:
            resp = ssm.get_parameter(Name=ssm_param)
            return resp["Parameter"]["Value"]
        except Exception:
            logger.warning("Failed to read SSM param %s, falling back", ssm_param)
    return os.environ.get("DYNAMODB_TABLE", "platform-service-table")


TABLE_NAME = _resolve_table_name()


class DynamoDBService:
    """Handles DynamoDB interactions for service records."""

    def __init__(self, table_name: str | None = None):
        self.table = boto3.resource("dynamodb").Table(table_name or TABLE_NAME)

    def create_service(self, item: dict) -> dict:
        """Put a service record into DynamoDB. Returns the item."""
        self.table.put_item(Item=item)
        logger.info("Created service %s", item.get("service_id"))
        return item

    def get_service(self, service_id: str) -> dict | None:
        """Get a service record by service_id. Returns None if not found."""
        resp = self.table.get_item(Key={"service_id": service_id})
        return resp.get("Item")

    def list_services(self) -> list[dict]:
        """Scan and return all service records."""
        resp = self.table.scan()
        return resp.get("Items", [])

    def delete_service(self, service_id: str) -> None:
        """Delete a service record by service_id."""
        self.table.delete_item(Key={"service_id": service_id})
        logger.info("Deleted service %s", service_id)
