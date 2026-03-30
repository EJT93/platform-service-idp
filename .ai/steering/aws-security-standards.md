# AWS Security Standards

## No Hardcoded Secrets

This is non-negotiable. No AWS access keys, secret keys, database passwords, API tokens, or any sensitive value may appear in:
- Source code
- Terraform files (including variable defaults)
- Committed tfvars files
- GitHub Actions workflow files
- Docker images
- README or documentation

Use environment variables, SSM Parameter Store, or Secrets Manager for all sensitive values.

## IAM Roles and Least Privilege

- Every Lambda function has its own dedicated IAM role.
- Roles use `sts:AssumeRole` trust policies scoped to the `lambda.amazonaws.com` service principal.
- Policies grant only the specific actions the function needs.
- Policies scope resources to specific ARNs, not wildcards.
- Use `data "aws_iam_policy_document"` in Terraform for policy construction.
- Prefer inline policies or customer-managed policies over AWS managed policies (except `AWSLambdaBasicExecutionRole`).

## Avoiding Wildcard Policies

This is a challenge requirement. Violations will be noticed by reviewers.

Never use:
- `Action: "*"`
- `Action: "dynamodb:*"` or `Action: "s3:*"`
- `Resource: "*"` (unless the AWS API genuinely requires it)

Always specify:
- Exact action names: `dynamodb:GetItem`, `dynamodb:PutItem`, `s3:PutObject`
- Exact resource ARNs: `arn:aws:dynamodb:us-east-1:123456789012:table/my-table`
- Use Terraform resource references for ARNs: `aws_dynamodb_table.this.arn`

Document any exception where `Resource: "*"` is unavoidable (e.g., `logs:CreateLogGroup`).

## Acceptable Secret Stores

For this project:
- SSM Parameter Store (preferred for simple key-value config)
- Secrets Manager (if rotation or structured secrets are needed)
- GitHub Actions secrets (for CI/CD pipeline values)
- Environment variables set by Terraform on Lambda configuration

Do not use:
- `.env` files committed to the repo
- Hardcoded values in Lambda code
- Terraform variable defaults for sensitive values

## Encryption Expectations

- S3 buckets: server-side encryption enabled (SSE-S3 or SSE-KMS).
- DynamoDB: encryption at rest is enabled by default (AWS managed key is acceptable for MVP).
- CloudWatch Logs: default encryption is acceptable for MVP.
- No data in transit without TLS (API Gateway enforces HTTPS by default).

## Logging and Security Visibility

- All API requests are logged with structured JSON.
- Failed requests (4xx, 5xx) are logged at WARNING or ERROR level.
- Authentication failures (if auth is implemented) are logged at WARNING level.
- No sensitive data (passwords, tokens, PII) appears in logs.
- CloudWatch Log Groups have defined retention periods (not infinite).

## API Exposure Considerations

- API Gateway is the only public-facing endpoint.
- Lambda functions are not directly invocable from outside AWS (no function URL needed).
- S3 buckets have public access blocked.
- DynamoDB is not directly accessible from outside the AWS account.
- For MVP, API Gateway can be open (no auth) or use a simple API key. Document the choice.
- If adding auth, prefer API Gateway's built-in API key mechanism or IAM authorization over custom authorizers.

## Input Trust Boundaries

- All data from API Gateway is untrusted.
- Validate every field in the request body.
- Do not use client-provided data in AWS API calls without sanitization.
- Do not use client-provided data in log messages without ensuring it cannot inject malicious content.
- Treat path parameters as untrusted (validate format, e.g., UUID pattern for service_id).

## Validation Requirements

- Required fields must be present and non-empty.
- String fields should have reasonable length limits.
- ID fields should match expected formats (UUID).
- Reject unexpected fields silently (do not store arbitrary client data).
- Return clear error messages for validation failures.

## Security Decision Documentation

Document the following in DECISIONS.md:
- Why a particular auth mechanism was chosen (or why auth was deferred).
- Any IAM policy that uses `Resource: "*"` and why.
- Encryption choices (default vs KMS).
- Network exposure decisions (public API Gateway, no VPC).
- Any security tradeoff made for MVP simplicity.
