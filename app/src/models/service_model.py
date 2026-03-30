"""Data model for the platform service."""

import uuid
from datetime import datetime, timezone


class ServiceItem:
    """Represents a service item stored in DynamoDB."""

    def __init__(self, item_id=None, name="", description="", created_at=None):
        self.item_id = item_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            item_id=data.get("item_id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at"),
        )
