"""DynamoDB service layer for CRUD operations."""

import os
import boto3
from utils.logger import get_logger

logger = get_logger(__name__)

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "platform-service-table")


class DynamoDBService:
    """Handles DynamoDB interactions."""

    def __init__(self, table_name=None):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name or TABLE_NAME)

    def get_item(self, item_id):
        resp = self.table.get_item(Key={"item_id": item_id})
        return resp.get("Item")

    def list_items(self):
        resp = self.table.scan()
        return resp.get("Items", [])

    def put_item(self, item):
        self.table.put_item(Item=item)
        logger.info("Created item %s", item.get("item_id"))
        return item

    def delete_item(self, item_id):
        self.table.delete_item(Key={"item_id": item_id})
        logger.info("Deleted item %s", item_id)
