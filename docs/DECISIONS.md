# Architecture Decision Records

## ADR-001: Lambda over ECS

Status: Accepted

Context: The challenge requires a compute platform for an API service. Both Lambda and ECS Fargate are viable options. The service handles simple CRUD operations with no long-running processes, persistent connections, or large deployment artifacts.

Decision: Use Lambda. It eliminates container management overhead, reduces Terraform surface area, and aligns with the challenge's emphasis on simplicity and speed of delivery. Cold start latency is acceptable for an internal API.

Consequences: Limited to 15-minute execution time and 250MB deployment size. Cannot maintain persistent connections. These constraints are irrelevant for this use case. If the service evolved to need background processing or sub-100ms P99 latency, ECS would be reconsidered.

---

## ADR-002: DynamoDB over RDS Aurora Postgres

Status: Accepted

Context: The service stores service catalog records — simple key-value data with a UUID primary key. Access patterns are: create, read by ID, list all, delete by ID. No joins, aggregations, or complex queries are needed.

Decision: Use DynamoDB with on-demand billing. The data model is a natural fit for a key-value store. DynamoDB requires zero capacity planning, scales to zero cost when idle, and needs no connection management or VPC configuration.

Consequences: Limited query flexibility. If the service needed full-text search, complex filtering, or relational joins, RDS would be the better choice. For the current access patterns, DynamoDB is simpler and cheaper.

---

## ADR-003: Single Repository

Status: Accepted

Context: The project includes application code, Terraform infrastructure, CI/CD pipelines, and documentation. A multi-repo approach would separate concerns but add coordination overhead.

Decision: Use a single repository. The project is small enough that separation provides no benefit. A single repo simplifies CI/CD, makes cross-cutting changes atomic, and is easier to review as a cohesive submission.

Consequences: If the project grew to include multiple services, a mono-repo or multi-repo strategy would need to be evaluated. For a single-service MVP, one repo is the right choice.

---

## ADR-004: GitHub Actions with Auto-Apply on Dev

Status: Accepted

Context: The challenge requires CI/CD deployment. The pipeline needs to validate Terraform and deploy on merge.

Decision: Use GitHub Actions with two workflows: CI (lint, validate, plan on PR) and Deploy (package, upload, apply on merge to main). Auto-apply is enabled for the dev environment to simplify the workflow.

Consequences: Auto-apply is not appropriate for staging or production environments. In a real deployment, manual approval or plan review would gate applies. This is documented as a known simplification.

---

## ADR-005: Observability Scope — CloudWatch + SNS Only

Status: Accepted

Context: The challenge requires demonstrating observability. Options range from basic CloudWatch logging to full distributed tracing with X-Ray, custom metrics, and third-party integrations.

Decision: Use structured JSON logging to CloudWatch, a Lambda errors alarm, and SNS for notifications. This is sufficient to demonstrate observability awareness without over-investing in monitoring infrastructure.

Consequences: No distributed tracing, custom metrics, or dashboards in the MVP. These would be added for production. The current setup allows debugging via CloudWatch Logs Insights and alerting on errors.

---

## ADR-006: Authentication Deferred

Status: Accepted

Context: The API is intended for internal use. The challenge does not explicitly require authentication, but security awareness is expected.

Decision: Defer authentication for the MVP. The API Gateway endpoint is publicly accessible. API key authentication or IAM authorization can be added as a fast follow.

Consequences: The API is open to anyone who knows the endpoint URL. This is acceptable for a dev environment demonstration. Document this as a known limitation and mention the planned auth approach in the README.
