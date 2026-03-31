"""Property-based tests for ServiceRecord model."""

import uuid
from datetime import datetime, timezone

from hypothesis import given, settings
from hypothesis import strategies as st

from src.models.service_model import ServiceRecord


# --- Strategies ---

# Strategy for ISO 8601 timestamps (valid datetime strings)
iso8601_timestamps = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2099, 12, 31),
    timezones=st.just(timezone.utc),
).map(lambda dt: dt.isoformat())

# Strategy for valid UUID v4 strings
uuid4_strings = st.uuids(version=4).map(str)

# Strategy for arbitrary text fields (non-null strings)
text_fields = st.text(min_size=0, max_size=200)

# Strategy for a fully-specified ServiceRecord
service_record_strategy = st.builds(
    ServiceRecord,
    service_id=uuid4_strings,
    name=text_fields,
    owner=text_fields,
    description=text_fields,
    runtime=text_fields,
    created_at=iso8601_timestamps,
    updated_at=iso8601_timestamps,
)

# Strategy for non-empty strings (used for required fields in Property 5)
non_empty_text = st.text(min_size=1, max_size=200)


# Feature: idp-mvp-phase1, Property 4: ServiceRecord serialization round-trip
# **Validates: Requirements 4.2**
@given(record=service_record_strategy)
@settings(max_examples=100)
def test_service_record_serialization_round_trip(record):
    """For any valid ServiceRecord, to_dict() followed by from_dict() produces an equivalent record."""
    serialized = record.to_dict()
    restored = ServiceRecord.from_dict(serialized)

    assert restored.service_id == record.service_id
    assert restored.name == record.name
    assert restored.owner == record.owner
    assert restored.description == record.description
    assert restored.runtime == record.runtime
    assert restored.created_at == record.created_at
    assert restored.updated_at == record.updated_at


# Feature: idp-mvp-phase1, Property 5: ServiceRecord schema completeness and defaults
# **Validates: Requirements 4.1, 4.3, 1.2**
@given(name=non_empty_text, owner=non_empty_text)
@settings(max_examples=100)
def test_service_record_schema_completeness_and_defaults(name, owner):
    """For any ServiceRecord created with only name and owner, defaults are correctly applied."""
    record = ServiceRecord(name=name, owner=owner)

    # service_id must be a valid UUID v4
    parsed_uuid = uuid.UUID(record.service_id, version=4)
    assert str(parsed_uuid) == record.service_id
    assert parsed_uuid.version == 4

    # created_at and updated_at must be non-empty ISO 8601 timestamps
    assert record.created_at != ""
    assert record.updated_at != ""
    datetime.fromisoformat(record.created_at)
    datetime.fromisoformat(record.updated_at)

    # description and runtime default to empty strings
    assert record.description == ""
    assert record.runtime == ""
