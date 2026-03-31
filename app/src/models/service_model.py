"""Data model for the platform service."""

import uuid
from datetime import datetime, timezone


class ServiceRecord:
    """Represents a service record stored in DynamoDB."""

    def __init__(self, service_id=None, name="", owner="", description="", runtime="", created_at=None, updated_at=None):
        self.service_id = service_id or str(uuid.uuid4())
        self.name = name
        self.owner = owner
        self.description = description
        self.runtime = runtime
        now = datetime.now(timezone.utc).isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or self.created_at

    def to_dict(self):
        return {
            "service_id": self.service_id,
            "name": self.name,
            "owner": self.owner,
            "description": self.description,
            "runtime": self.runtime,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            service_id=data.get("service_id"),
            name=data.get("name", ""),
            owner=data.get("owner", ""),
            description=data.get("description", ""),
            runtime=data.get("runtime", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
