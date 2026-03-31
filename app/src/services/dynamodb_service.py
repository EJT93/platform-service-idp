"""DynamoDB service layer for CRUD operations."""

import os
import boto3
from utils.logger import get_logger

logger = get_logger(__name__)

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "platform-service-table")


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
