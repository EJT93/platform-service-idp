# Observability Standards

## Structured Logging Format

All Lambda functions must emit structured JSON logs. Do not use plain text log messages.

Each log entry must be a single JSON object on one line:

```json
{
  "timestamp": "2026-03-30T12:00:00.000Z",
  "level": "INFO",
  "message": "Service registered successfully",
  "request_id": "abc-123-def",
  "function_name": "platform-services-dev",
  "service_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Required Fields in Every Log Entry

| Field | Source | Required |
|-------|--------|----------|
| `timestamp` | `datetime.now(timezone.utc).isoformat()` | Yes |
| `level` | Logging level (INFO, WARNING, ERROR) | Yes |
| `message` | Human-readable description | Yes |
| `request_id` | `context.aws_request_id` | Yes |
| `function_name` | `context.function_name` or env var | Yes |

## Contextual Fields (Include When Available)

| Field | When |
|-------|------|
| `service_id` | When processing a specific service record |
| `http_method` | On request entry |
| `path` | On request entry |
| `status_code` | On response |
| `error_type` | On error |
| `duration_ms` | On response (optional for MVP) |

## Error Logging Standards

- All caught exceptions must be logged at ERROR level.
- Include the full stack trace using `logger.exception()` or equivalent.
- Include the error type and message as structured fields.
- Do not log sensitive data (request bodies containing secrets, auth tokens).
- Log client errors (400s) at WARNING level, not ERROR.
- Log server errors (500s) at ERROR level.

Example error log:
```json
{
  "timestamp": "2026-03-30T12:00:00.000Z",
  "level": "ERROR",
  "message": "Failed to write to DynamoDB",
  "request_id": "abc-123-def",
  "function_name": "platform-services-dev",
  "error_type": "ClientError",
  "error_message": "ProvisionedThroughputExceededException",
  "traceback": "..."
}
```

## Alarm Expectations

Minimum alarms for MVP:

1. Lambda Errors alarm:
   - Metric: `AWS/Lambda` → `Errors`
   - Threshold: Sum > 0 in 5-minute period
   - Action: SNS notification
   - This catches any unhandled exception in the Lambda function.

2. Optional but recommended:
   - Lambda Duration alarm (P99 > 10 seconds)
   - Lambda Throttles alarm (Sum > 0)
   - API Gateway 5xx alarm

Do not create alarms for metrics you will not act on. One meaningful alarm is better than ten ignored ones.

## Dashboard Expectations

For MVP, a CloudWatch dashboard is optional. If created, include:
- Lambda invocation count
- Lambda error count
- Lambda duration (P50, P99)
- DynamoDB consumed read/write capacity
- API Gateway request count by status code

A dashboard is a nice-to-have for the interview demo but not required for the submission.

## Operational Metrics to Track

These metrics are available by default and should be monitored:

Lambda:
- `Invocations` — request volume
- `Errors` — unhandled exceptions
- `Duration` — execution time
- `Throttles` — concurrency limits hit
- `ConcurrentExecutions` — current load

API Gateway:
- `Count` — total requests
- `4XXError` — client errors
- `5XXError` — server errors
- `Latency` — end-to-end response time

DynamoDB:
- `ConsumedReadCapacityUnits`
- `ConsumedWriteCapacityUnits`
- `ThrottledRequests`

## CloudWatch Usage

- One Log Group per Lambda function: `/aws/lambda/{function_name}`
- Log retention: 14 days for dev (configurable via Terraform variable)
- Use CloudWatch Logs Insights for ad-hoc queries during development
- Do not create custom metrics for MVP. Built-in metrics are sufficient.

## SNS Notification Guidance

- One SNS topic for all alarms in the environment: `{project}-alerts-{environment}`
- Subscribe an email address for dev (manual step, not automated in Terraform for MVP)
- Do not create complex notification routing or fan-out patterns
- SNS is the alarm target, not a messaging backbone

## What "Good Enough" Observability Means for This MVP

Good enough means:
- You can tell if the service is working by looking at CloudWatch metrics.
- You can debug a failed request by searching CloudWatch Logs for the request ID.
- You get notified (via SNS) if the Lambda function starts throwing errors.
- You can explain to an interviewer what you would monitor and alert on in production.

Good enough does not mean:
- Distributed tracing (X-Ray)
- Custom metrics and dimensions
- Automated runbooks
- PagerDuty or OpsGenie integration
- Log aggregation to a third-party service
- SLO/SLI dashboards

These are all valid production concerns. Mention them in the interview as future improvements. Do not build them for the MVP.
