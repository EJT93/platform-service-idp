# Platform Service Catalog API

A self-service REST API for internal teams to register and manage service metadata. Built on a serverless architecture using API Gateway v2, Lambda (Python 3.12), and DynamoDB — all managed by Terraform.

## Architecture Overview

```
Client (curl / internal tool)
    │
    ▼
API Gateway v2 (HTTP API)
    │  AWS_PROXY integration, payload format v2.0
    ▼
Lambda (Python 3.12)
    │  Routes: POST/GET/DELETE /services
    ▼
DynamoDB (platform-services-dev)
    │  PAY_PER_REQUEST, PITR enabled
    │
    ├── CloudWatch Logs (structured JSON, 14-day retention)
    │       └── CloudWatch Alarm (Lambda Errors, Sum > 0 / 5 min)
    │               └── SNS Topic (alerts)
    │
    └── S3 (artifacts bucket, versioned, KMS-encrypted)
```

**Request flow**: Client sends an HTTP request → API Gateway forwards it to Lambda via proxy integration → Lambda handler parses the v2 event (`rawPath`, `requestContext.http.method`, `pathParameters`), validates input, delegates to the DynamoDB service layer, and returns a JSON response. All operations emit structured JSON logs to CloudWatch.

## Prerequisites

- Python 3.12+
- Terraform >= 1.5
- AWS CLI configured with appropriate credentials
- GitHub Actions for CI/CD (runs automatically on PRs and merges)

## Getting Started

### Local Development

```bash
cd app
pip install -r requirements.txt
PYTHONPATH=app python -m pytest app/tests/ -v
```

### Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan -var-file=tfvars-env/dev/dev.tfvars
terraform apply -var-file=tfvars-env/dev/dev.tfvars
```

## API Usage

Replace `$API_URL` with your API Gateway endpoint (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com`).

### Create a Service

```bash
curl -X POST "$API_URL/services" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "auth-service",
    "owner": "platform-team",
    "description": "Handles authentication and authorization",
    "runtime": "python3.12"
  }'
```

Response (201):
```json
{
  "service_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "auth-service",
  "owner": "platform-team",
  "description": "Handles authentication and authorization",
  "runtime": "python3.12",
  "created_at": "2025-01-15T10:30:00+00:00",
  "updated_at": "2025-01-15T10:30:00+00:00"
}
```

### List All Services

```bash
curl "$API_URL/services"
```

Response (200):
```json
[
  {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "auth-service",
    "owner": "platform-team",
    "description": "Handles authentication and authorization",
    "runtime": "python3.12",
    "created_at": "2025-01-15T10:30:00+00:00",
    "updated_at": "2025-01-15T10:30:00+00:00"
  }
]
```

### Get a Service

```bash
curl "$API_URL/services/{service_id}"
```

Response (200): Single service record JSON object.

Response (404):
```json
{
  "error": "Service not found"
}
```

### Delete a Service

```bash
curl -X DELETE "$API_URL/services/{service_id}"
```

Response (204): Empty body.

## Design Rationale

| Decision | Rationale |
|----------|-----------|
| **Lambda** | No long-running processes. Scales to zero with minimal ops overhead. Cold start is acceptable for an internal API. |
| **DynamoDB** | Schemaless, serverless, key-value access pattern fits the data model. PAY_PER_REQUEST means no capacity planning. |
| **API Gateway v2 (HTTP API)** | Lower latency and cost than REST API (v1). Proxy integration simplifies routing. Sufficient for internal use. |
| **Single Lambda function** | All 4 routes handled by one function. No need for per-route functions at this scale. |
| **Structured JSON logging** | Enables querying and debugging via CloudWatch Logs Insights. Each log entry includes `request_id` and `function_name` for traceability. |
| **Terraform modules** | Reproducible, auditable infrastructure. Modular design (DynamoDB, IAM, Lambda, Observability, S3) for reuse and separation of concerns. |

## Repository Structure

```
platform-service-idp/
├── app/
│   ├── src/
│   │   ├── handlers/
│   │   │   └── service_handler.py    # Lambda entry point, HTTP routing
│   │   ├── models/
│   │   │   └── service_model.py      # ServiceRecord dataclass
│   │   ├── services/
│   │   │   └── dynamodb_service.py   # DynamoDB CRUD operations
│   │   └── utils/
│   │       ├── logger.py             # Structured JSON logger
│   │       └── validator.py          # Input validation
│   ├── tests/
│   │   ├── test_handler.py           # Handler unit + property tests
│   │   ├── test_logger.py            # Logger property tests
│   │   ├── test_model.py             # Model property tests
│   │   ├── test_service.py           # Service layer property tests
│   │   └── test_validator.py         # Validator property tests
│   ├── Dockerfile
│   └── requirements.txt
├── terraform/
│   ├── main.tf                       # Module composition
│   ├── variables.tf
│   ├── outputs.tf
│   ├── backend.tf
│   ├── provider.tf
│   ├── locals.tf
│   ├── tfvars-env/
│   │   └── dev/
│   │       └── dev.tfvars
│   ├── modules/
│   │   ├── dynamodb/                 # DynamoDB table (service_id key, PITR)
│   │   ├── github_oidc/             # GitHub Actions OIDC provider + IAM role
│   │   ├── iam/                      # Lambda execution role (least-privilege)
│   │   ├── lambda_api/               # Lambda + API Gateway v2
│   │   ├── notifications/            # SNS email subscriptions
│   │   ├── observability/            # CloudWatch Logs, Alarm, SNS
│   │   └── s3/                       # Artifacts bucket (versioned, KMS)
│   └── tests/
│       └── basic.tftest.hcl
├── .github/
│   └── workflows/
│       ├── ci.yml                    # PR: lint + test + fmt + validate + plan
│       └── deploy.yml                # Merge to main: package + upload + apply
├── diagrams/
│   ├── architecture.drawio
│   └── architecture.png
├── docs/
│   ├── DECISIONS.md                  # Architectural Decision Records
│   └── AI_WORKFLOW.md                # AI tool usage documentation
├── .ai/                              # AI steering files and prompts
└── README.md
```

## CI/CD

- **Pull Requests** trigger the CI pipeline (`ci.yml`): ruff lint, pytest, `terraform fmt -check`, `terraform validate`, and `terraform plan`.
- **Merges to main** trigger the deploy pipeline (`deploy.yml`): Lambda code packaging, S3 upload, and `terraform apply`.

## Known Limitations

- **Authentication**: Deferred to a future phase. The API is currently unauthenticated.
- **Pagination**: The `GET /services` endpoint returns all records via a DynamoDB Scan with no pagination.
- **Environment**: Only a `dev` environment is configured. Production and staging environments are not yet set up.
