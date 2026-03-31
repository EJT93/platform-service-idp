"""Property-based tests for DynamoDB service layer."""

import sys
from unittest.mock import MagicMock

# The dynamodb_service module imports `from utils.logger import get_logger`
# which resolves when app/src is on sys.path (Lambda runtime). Under test
# with PYTHONPATH=app, we alias `utils` → `src.utils` so the import succeeds.
import src.utils.logger
sys.modules.setdefault("utils", src.utils)
sys.modules.setdefault("utils.logger", src.utils.logger)

from hypothesis import given, settings
from hypothesis import strategies as st

from src.models.service_model import ServiceRecord
from src.services.dynamodb_service import DynamoDBService


# --- In-memory DynamoDB table mock ---


class FakeTable:
    """Simulates DynamoDB table operations using an in-memory dict."""

    def __init__(self):
        self.store: dict[str, dict] = {}

    def put_item(self, *, Item: dict):
        key = Item["service_id"]
        self.store[key] = dict(Item)

    def get_item(self, *, Key: dict) -> dict:
        item = self.store.get(Key["service_id"])
        if item is not None:
            return {"Item": dict(item)}
        return {}

    def delete_item(self, *, Key: dict):
        self.store.pop(Key["service_id"], None)

    def scan(self) -> dict:
        return {"Items": list(self.store.values())}


def _make_service(fake_table: FakeTable) -> DynamoDBService:
    """Create a DynamoDBService wired to a FakeTable."""
    svc = DynamoDBService.__new__(DynamoDBService)
    svc.table = fake_table
    return svc


# --- Strategies ---

# Non-empty strings for required fields (name, owner)
non_empty_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=1,
    max_size=128,
).filter(lambda s: s.strip())

# Optional text fields
optional_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=0,
    max_size=200,
)

# Strategy for valid ServiceRecord creation inputs
service_input_strategy = st.fixed_dictionaries(
    {"name": non_empty_text, "owner": non_empty_text},
    optional={"description": optional_text, "runtime": optional_text},
)


# Feature: idp-mvp-phase1, Property 6: Create-then-get round-trip
# **Validates: Requirements 1.1, 1.3, 2.2**
@given(data=service_input_strategy)
@settings(max_examples=100)
def test_create_then_get_round_trip(data):
    """For any valid service creation input, creating a ServiceRecord via the
    Service_Layer and then retrieving it by service_id SHALL return a record
    with matching name, owner, description, and runtime fields."""
    fake_table = FakeTable()
    svc = _make_service(fake_table)

    record = ServiceRecord(
        name=data["name"],
        owner=data["owner"],
        description=data.get("description", ""),
        runtime=data.get("runtime", ""),
    )
    item = record.to_dict()

    svc.create_service(item)
    retrieved = svc.get_service(record.service_id)

    assert retrieved is not None, "get_service returned None after create"
    assert retrieved["name"] == data["name"]
    assert retrieved["owner"] == data["owner"]
    assert retrieved["description"] == data.get("description", "")
    assert retrieved["runtime"] == data.get("runtime", "")
    assert retrieved["service_id"] == record.service_id


# Feature: idp-mvp-phase1, Property 7: Delete removes record
# **Validates: Requirements 3.1**
@given(data=service_input_strategy)
@settings(max_examples=100)
def test_delete_removes_record(data):
    """For any ServiceRecord that exists in DynamoDB, deleting it by service_id
    via the Service_Layer and then attempting to retrieve it SHALL return None."""
    fake_table = FakeTable()
    svc = _make_service(fake_table)

    record = ServiceRecord(
        name=data["name"],
        owner=data["owner"],
        description=data.get("description", ""),
        runtime=data.get("runtime", ""),
    )
    item = record.to_dict()

    svc.create_service(item)
    # Confirm it exists first
    assert svc.get_service(record.service_id) is not None

    svc.delete_service(record.service_id)
    retrieved = svc.get_service(record.service_id)

    assert retrieved is None, f"Expected None after delete, got {retrieved}"
