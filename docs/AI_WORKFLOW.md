# AI-Assisted Development Workflow

## Tools Used

- **Kiro (AI IDE)**: Used for all implementation tasks via spec-driven development
- **Formal spec**: A requirements → design → tasks spec was created to drive all implementation work
- **AI steering files** (`.ai/steering/`): Constrained and guided agent behavior to match target architecture
- **AI prompt templates** (`.ai/prompts/`): Used for repeatable scaffolding tasks
- **Hypothesis**: Property-based testing library used to validate 10 correctness properties
- **pytest**: Unit test framework for handler, service layer, model, validator, and logger tests

## Development Phases

### Phase 1: Spec Creation and Steering
AI generated the formal spec (requirements.md, design.md, tasks.md) defining the target architecture. The spec included 11 requirement areas, 10 correctness properties for property-based testing, and a sequenced task list. Human reviewed and refined to ensure alignment with challenge requirements.

### Phase 2: Model, Validator, and Logger Refactoring
AI refactored the core data layer first — renaming `ServiceItem` to `ServiceRecord`, adding `owner`, `runtime`, and `updated_at` fields, then refactoring the validator to support type checking, length limits, and multi-error reporting. The structured logger was converted from plain text to JSON format. Property-based tests were written alongside each component.

### Phase 3: Service Layer and Handler Refactoring
AI refactored the DynamoDB service layer (renamed methods, changed key to `service_id`) and the Lambda handler (v1 → v2 event format, `/items` → `/services` routes, generic 500 error messages). Unit tests and property-based tests were written for both components.

### Phase 4: Infrastructure and CI/CD
AI updated Terraform modules (DynamoDB hash key `item_id` → `service_id`, alarm threshold 5 → 0) and added a pytest step to the CI pipeline. Human verified IAM policies for least-privilege compliance and resource naming patterns.

### Phase 5: Documentation
AI generated the README with architecture overview, deployment steps, and API usage examples. DECISIONS.md was populated with 6 ADRs. This AI_WORKFLOW.md was written to document the full process.

## Tasks Delegated to AI

The following tasks were delegated to Kiro and executed via the formal spec task list:

1. **Refactored ServiceRecord model** — Added `owner`, `runtime`, `updated_at` fields, renamed from `ServiceItem`, implemented `to_dict()` and `from_dict()` with correct defaults
2. **Refactored validator** — Added type checking, length limits (name: 128, owner: 128, description: 1024, runtime: 64), and multi-error reporting
3. **Refactored structured logger** — Converted from plain text format to single-line JSON objects with `timestamp`, `level`, `message`, `request_id`, and `function_name` fields
4. **Refactored DynamoDB service layer** — Renamed methods to `create_service`, `get_service`, `list_services`, `delete_service`; changed key from `item_id` to `service_id`
5. **Refactored Lambda handler** — Switched from API Gateway v1 to v2 event format (`rawPath`, `requestContext.http.method`), changed routes from `/items` to `/services`, added generic 500 error messages
6. **Wrote 10 property-based tests** — Covering model serialization round-trip, schema completeness, validator correctness, service layer CRUD, logger format, error response safety, and route matching
7. **Wrote unit tests for all handler routes** — POST, GET (list and single), DELETE, invalid JSON, missing fields, DynamoDB errors
8. **Updated Terraform modules** — Changed DynamoDB hash key to `service_id`, set alarm threshold to 0
9. **Updated CI pipeline** — Added pytest step to run unit tests on pull requests
10. **Generated README and documentation** — Project description, architecture overview, deployment steps, API examples, ADRs

## What Worked Well

- **Spec-driven development**: The formal spec (requirements → design → tasks) gave AI clear, unambiguous instructions for each implementation step. This eliminated guesswork and kept output consistent.
- **Steering files**: Effectively constrained AI output and prevented over-engineering. The AI stayed within the defined architecture boundaries.
- **Property-based testing with Hypothesis**: Validated 10 correctness properties across hundreds of generated inputs, catching edge cases that unit tests alone would miss.
- **Sequenced task ordering**: Model → validator → logger → service → handler ordering meant each layer was stable before the next was built on top of it.
- **Prompt templates**: Made it easy to regenerate components after corrections without starting from scratch.

## What Required Human Correction

- **Module aliasing for test imports**: The Lambda runtime uses bare module names (e.g., `import models.service_model`), but the test environment needs `sys.path` aliasing to resolve these imports correctly. AI initially generated tests that failed due to import errors; human added the path aliasing setup.
- **DynamoDB table naming pattern**: AI used `platform-service-dev` in some places instead of the correct `platform-services-dev` pattern. Human corrected the naming to follow the `{project}-{purpose}-{env}` convention consistently.
- **Property test generator quality**: Initial property-based tests used overly broad generators that produced inputs outside the valid domain. Human guided AI to write smart generators that constrain to valid input spaces (e.g., generating strings within length limits, using `st.from_regex` for structured fields).

## Lessons Learned

1. **Spec-driven development with formal correctness properties catches edge cases early.** Defining 10 properties upfront meant the AI had clear targets for what "correct" means, and property-based testing surfaced subtle bugs that example-based tests missed.
2. **Property-based testing with Hypothesis is effective for validating universal invariants.** Running 100+ examples per property across model serialization, validation rules, and error handling provided high confidence in correctness without writing hundreds of individual test cases.
3. **Steering files effectively constrain AI output and prevent over-engineering.** Without steering, AI tends to add unnecessary abstractions. The steering files kept the implementation minimal and aligned with the target architecture.
4. **Module aliasing between Lambda runtime and test environments needs careful handling.** Lambda's flat module structure (`from models.service_model import ServiceRecord`) conflicts with standard Python package imports in test environments. This is a recurring friction point that should be addressed in project templates.
5. **Sequenced task execution matters.** Building from the data model outward (model → validator → logger → service → handler) meant each layer was tested and stable before dependent layers were built. This reduced cascading failures during refactoring.

## AI-Generated Artifacts

| Artifact | Path | AI-Generated | Human-Reviewed |
|----------|------|:------------:|:--------------:|
| ServiceRecord model | `app/src/models/service_model.py` | ✅ | ✅ |
| Validator | `app/src/utils/validator.py` | ✅ | ✅ |
| Structured logger | `app/src/utils/logger.py` | ✅ | ✅ |
| DynamoDB service layer | `app/src/services/dynamodb_service.py` | ✅ | ✅ |
| Lambda handler | `app/src/handlers/service_handler.py` | ✅ | ✅ |
| Property-based tests | `app/tests/test_*.py` | ✅ | ✅ |
| Unit tests | `app/tests/test_handler.py` | ✅ | ✅ |
| Terraform modules | `terraform/modules/` | ✅ | ✅ |
| CI pipeline | `.github/workflows/ci.yml` | ✅ | ✅ |
| README | `README.md` | ✅ | ✅ |
| ADRs | `docs/DECISIONS.md` | ✅ | ✅ |
| This document | `docs/AI_WORKFLOW.md` | ✅ | ✅ |
