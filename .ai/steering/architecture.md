# Architecture

## Canonical Architecture

```
Client (curl / internal tool)
    │
    ▼
API Gateway (HTTP API v2)
    │
    ▼
AWS Lambda (Python 3.12)
    │
    ├──▶ DynamoDB (service records)
    ├──▶ S3 (optional audit/export artifacts)
    │
    ▼
CloudWatch Logs (structured JSON)
CloudWatch Alarms → SNS (error alerting)
```

## Service Boundaries

This is a single service with a single Lambda function handling all API routes. There is no need for multiple Lambda functions, microservice decomposition, or event-driven architecture for the MVP.

The Lambda function is the only compute. It handles:
- Request routing (based on HTTP method and path)
- Input validation
- Business logic (CRUD operations)
- Response formatting
- Error handling and logging

## Request Flow

1. Client sends HTTP request to API Gateway endpoint.
2. API Gateway validates the route exists and forwards to Lambda via AWS_PROXY integration.
3. Lambda handler parses the event, routes to the appropriate operation.
4. Service layer performs validation and interacts with DynamoDB (and optionally S3).
5. Lambda returns a structured JSON response with appropriate HTTP status code.
6. API Gateway forwards the response to the client.

## Primary AWS Components

| Component | Purpose | Justification |
|-----------|---------|---------------|
| API Gateway v2 (HTTP API) | Request ingress | Lower latency and cost than REST API. Sufficient for internal APIs. |
| Lambda (Python 3.12) | Compute | No long-running processes. Cold start is acceptable. Minimal ops overhead. |
| DynamoDB | Primary data store | Schemaless, serverless, scales to zero. Perfect for key-value catalog records. |
| S3 | Audit/export artifacts | Optional. Useful for demonstrating multi-store writes and audit capability. |
| CloudWatch Logs | Logging | Default Lambda log destination. Structured JSON for queryability. |
| CloudWatch Alarms | Alerting | Monitor Lambda errors and latency. |
| SNS | Notification delivery | Alarm target for email or webhook notifications. |
| IAM | Access control | Least-privilege roles for Lambda execution. |

## Storage Model

DynamoDB table: `platform-services-{environment}`

Primary key: `service_id` (String, UUID)

Attributes:
- `service_id` (S) — partition key, UUID
- `name` (S) — human-readable service name
- `owner` (S) — team or individual owner
- `description` (S) — brief description
- `runtime` (S) — e.g., "python3.12", "node20", "go1.21"
- `created_at` (S) — ISO 8601 timestamp
- `updated_at` (S) — ISO 8601 timestamp

Billing mode: PAY_PER_REQUEST (on-demand). No capacity planning needed for MVP.

Optional S3 bucket: `platform-services-audit-{environment}`
- Used for periodic exports or write-through audit records
- Not required for core functionality

## Observability Model

- Every Lambda invocation produces structured JSON logs to CloudWatch.
- Log fields: `timestamp`, `level`, `message`, `request_id`, `function_name`, `service_id` (when applicable).
- CloudWatch Alarm on Lambda `Errors` metric (threshold: > 0 in 5 minutes).
- CloudWatch Alarm on Lambda `Duration` metric (threshold: > 10 seconds, optional).
- SNS topic receives alarm notifications.
- Log retention: 14 days for dev environment.

## Deployment Model

- Terraform manages all infrastructure.
- Lambda code is packaged as a zip, uploaded to S3, and referenced by the Lambda resource.
- GitHub Actions CI pipeline: lint → validate → plan on PRs.
- GitHub Actions CD pipeline: package → upload → apply on merge to main.
- Single environment (dev) for the assessment. The module structure supports adding staging/prod later.

## Security Boundaries

- API Gateway is publicly accessible but can be restricted with API keys or IAM auth.
- Lambda runs in the default VPC (no VPC attachment needed for DynamoDB and S3 access).
- DynamoDB and S3 are accessed via IAM role, not access keys.
- No secrets are hardcoded. Environment-specific values come from Terraform variables or SSM.
- S3 bucket has public access blocked, versioning enabled, and KMS encryption.
- DynamoDB has point-in-time recovery enabled.

## Future Extension Points

These are not part of the MVP but the architecture supports them:
- Add `/services/{id}/environments` sub-resource for environment tracking
- Add DynamoDB GSI on `owner` for team-based queries
- Add S3 event notifications for audit pipeline triggers
- Add API key authentication via API Gateway
- Add pagination with DynamoDB `LastEvaluatedKey`
- Add CloudWatch dashboard for operational visibility
- Add EventBridge for catalog change events

## Why Lambda Over ECS

Lambda is preferred for this challenge because:
- The workload is request/response with no long-running processes.
- Cold start latency is acceptable for an internal API.
- Lambda eliminates container management, task definitions, and cluster configuration.
- It reduces the Terraform surface area significantly.
- It demonstrates serverless-first thinking, which is a platform engineering best practice.
- The assessment values simplicity and speed of delivery.

## When ECS Would Be a Valid Future Evolution

ECS would make sense if:
- The service needed long-running background processing.
- Cold start latency became unacceptable (e.g., sub-100ms P99 requirement).
- The service needed to maintain persistent connections (WebSockets, gRPC).
- The deployment artifact exceeded Lambda's 250MB unzipped limit.
- The team had existing ECS infrastructure and operational expertise.

For this assessment, none of these conditions apply.
