"""Property-based tests for Validator."""

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.utils.validator import validate_create_service, REQUIRED_FIELDS, LENGTH_LIMITS


# --- Strategies ---

# Non-empty, non-whitespace-only strings within a given max length
def valid_required_field(max_len: int) -> st.SearchStrategy[str]:
    """Generate strings that pass required-field validation: 1..max_len chars, not whitespace-only."""
    return st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=1,
        max_size=max_len,
    ).filter(lambda s: s.strip())


def valid_optional_field(max_len: int) -> st.SearchStrategy[str]:
    """Generate strings within length limit (may be empty)."""
    return st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=0,
        max_size=max_len,
    )


# Strategy for a fully valid input dict
valid_input_strategy = st.fixed_dictionaries(
    {"name": valid_required_field(128), "owner": valid_required_field(128)},
    optional={
        "description": valid_optional_field(1024),
        "runtime": valid_optional_field(64),
    },
)


# Feature: idp-mvp-phase1, Property 1: Valid inputs pass validation
# **Validates: Requirements 5.1, 5.2**
@given(data=valid_input_strategy)
@settings(max_examples=100)
def test_valid_inputs_pass_validation(data):
    """For any dict with valid name, owner, and optional description/runtime within limits,
    the Validator SHALL return an empty error list."""
    errors = validate_create_service(data)
    assert errors == [], f"Expected no errors for valid input {data!r}, got {errors}"


# --- Strategies for invalid inputs ---

# A non-string value
non_string_values = st.one_of(
    st.integers(),
    st.floats(allow_nan=False),
    st.booleans(),
    st.lists(st.integers(), max_size=3),
    st.just(None),
)


def _make_single_violation() -> st.SearchStrategy[tuple[dict, int]]:
    """Generate (dict, expected_min_errors) with exactly one violation type."""
    return st.one_of(
        # Missing required field: name
        st.fixed_dictionaries({"owner": valid_required_field(128)}).map(lambda d: (d, 1)),
        # Missing required field: owner
        st.fixed_dictionaries({"name": valid_required_field(128)}).map(lambda d: (d, 1)),
        # Empty/whitespace-only name
        st.tuples(
            st.text(alphabet=" \t\n\r", min_size=0, max_size=10),
            valid_required_field(128),
        ).map(lambda t: ({"name": t[0], "owner": t[1]}, 1)),
        # Empty/whitespace-only owner
        st.tuples(
            valid_required_field(128),
            st.text(alphabet=" \t\n\r", min_size=0, max_size=10),
        ).map(lambda t: ({"name": t[0], "owner": t[1]}, 1)),
        # Non-string name
        st.tuples(non_string_values, valid_required_field(128)).map(
            lambda t: ({"name": t[0], "owner": t[1]}, 1)
        ),
        # Non-string owner
        st.tuples(valid_required_field(128), non_string_values).map(
            lambda t: ({"name": t[0], "owner": t[1]}, 1)
        ),
        # Name exceeds length limit
        st.tuples(
            st.text(min_size=129, max_size=300),
            valid_required_field(128),
        ).map(lambda t: ({"name": t[0], "owner": t[1]}, 1)),
        # Owner exceeds length limit
        st.tuples(
            valid_required_field(128),
            st.text(min_size=129, max_size=300),
        ).map(lambda t: ({"name": t[0], "owner": t[1]}, 1)),
        # Description exceeds length limit
        st.tuples(
            valid_required_field(128),
            valid_required_field(128),
            st.text(min_size=1025, max_size=1200),
        ).map(lambda t: ({"name": t[0], "owner": t[1], "description": t[2]}, 1)),
        # Runtime exceeds length limit
        st.tuples(
            valid_required_field(128),
            valid_required_field(128),
            st.text(min_size=65, max_size=200),
        ).map(lambda t: ({"name": t[0], "owner": t[1], "runtime": t[2]}, 1)),
    )


# Feature: idp-mvp-phase1, Property 2: Invalid inputs are rejected with correct errors
# **Validates: Requirements 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 5.1, 5.2, 5.4**
@given(pair=_make_single_violation())
@settings(max_examples=100)
def test_invalid_inputs_are_rejected(pair):
    """For any dict that violates at least one validation rule, the Validator SHALL return
    a non-empty error list."""
    data, _expected_min = pair
    errors = validate_create_service(data)
    assert len(errors) >= 1, f"Expected errors for invalid input {data!r}, got none"


# --- Strategies for multi-violation inputs ---

def _make_multi_violation() -> st.SearchStrategy[tuple[dict, int]]:
    """Generate (dict, N) where N >= 2 distinct violations are present."""
    return st.one_of(
        # Missing both name and owner → 2 violations
        st.just(({}, 2)),
        # Missing name + owner exceeds length → 2 violations
        st.text(min_size=129, max_size=300).map(
            lambda owner: ({"owner": owner}, 2)
        ),
        # Missing owner + name exceeds length → 2 violations
        st.text(min_size=129, max_size=300).map(
            lambda name: ({"name": name}, 2)
        ),
        # Both name and owner are non-string → 2 violations
        st.tuples(non_string_values, non_string_values).map(
            lambda t: ({"name": t[0], "owner": t[1]}, 2)
        ),
        # Name empty + owner empty → 2 violations
        st.tuples(
            st.text(alphabet=" \t\n\r", min_size=0, max_size=5),
            st.text(alphabet=" \t\n\r", min_size=0, max_size=5),
        ).map(lambda t: ({"name": t[0], "owner": t[1]}, 2)),
        # Missing name + missing owner + description too long → 3 violations
        st.text(min_size=1025, max_size=1200).map(
            lambda desc: ({"description": desc}, 3)
        ),
        # Name too long + owner too long → 2 violations
        st.tuples(
            st.text(min_size=129, max_size=300),
            st.text(min_size=129, max_size=300),
        ).map(lambda t: ({"name": t[0], "owner": t[1]}, 2)),
    )


# Feature: idp-mvp-phase1, Property 3: Validator reports all errors, not just the first
# **Validates: Requirements 5.3**
@given(pair=_make_multi_violation())
@settings(max_examples=100)
def test_validator_reports_all_errors(pair):
    """For any dict with N >= 2 distinct violations, the Validator SHALL return
    at least N error messages."""
    data, expected_min_errors = pair
    errors = validate_create_service(data)
    assert len(errors) >= expected_min_errors, (
        f"Expected at least {expected_min_errors} errors for {data!r}, got {len(errors)}: {errors}"
    )
