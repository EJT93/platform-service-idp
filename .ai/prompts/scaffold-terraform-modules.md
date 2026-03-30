# Prompt: Scaffold Terraform Modules

## Context

You are building Terraform infrastructure for the Platform Service Catalog API. Read the steering files in `.ai/steering/` before generating any code. Follow the Terraform standards and AWS security standards exactly.

## Task

Generate Terraform modules under `terraform/modules/` and environment composition under `terraform/environments/dev/`.

## Modules to Create

### 1. `terraform/modules/dynamodb/`
- DynamoDB table with `service_id` (S) as hash key.
- PAY_PER_REQUEST billing mode.
- Point-in-time recovery enabled.
- Configurable table name via variable.
- Tags variable.
- Outputs: table_name, table_arn.

### 2. `terraform/modules/s3/`
- S3 bucket for deployment artifacts (and optionally audit data).
- Versioning enabled.
- Server-side encryption (SSE-KMS or SSE-S3).
- Public access fully blocked.
- Configurable bucket name via variable.
- Tags variable.
- Outputs: bucket_name, bucket_arn.

### 3. `terraform/modules/iam/`
- IAM role for Lambda with `lambda.amazonaws.com` trust policy.
- Inline policy for DynamoDB access: GetItem, PutItem, DeleteItem, Scan on specific table ARN.
- Inline policy for S3 access: PutObject on specific bucket ARN (if S3 audit is used).
- Attach `AWSLambdaBasicExecutionRole` managed policy for CloudWatch Logs.
- NO wildcard actions. NO wildcard resources.
- Configurable function name, DynamoDB table ARN, S3 bucket ARN via variables.
- Tags variable.
- Outputs: role_arn, role_name.

### 4. `terraform/modules/lambda_api/`
- Lambda function with Python 3.12 runtime.
- S3-based deployment (s3_bucket and s3_key variables).
- Environment variables: DYNAMODB_TABLE, LOG_LEVEL.
- Configurable timeout and memory.
- API Gateway v2 HTTP API with Lambda proxy integration.
- Lambda permission for API Gateway invocation.
- Tags variable.
- Outputs: function_name, function_arn, api_endpoint.

### 5. `terraform/modules/observability/`
- CloudWatch Log Group for the Lambda function with configurable retention.
- CloudWatch Metric Alarm on Lambda Errors (Sum > threshold in 5 min).
- SNS topic for alarm notifications.
- Tags variable.
- Outputs: log_group_name, sns_topic_arn.

## Environment Composition

### `terraform/environments/dev/main.tf`
- Provider configuration with default_tags.
- Instantiate all five modules.
- Wire cross-module dependencies (DynamoDB ARN → IAM, S3 bucket → IAM and Lambda, etc.).
- Use locals for computed names.

### Also generate:
- `variables.tf` — aws_region, environment, project_name, lambda_s3_key
- `outputs.tf` — api_endpoint, function_name, dynamodb_table, s3_bucket
- `terraform.tfvars.example` — example values
- `backend.tf` — commented-out S3 backend configuration

## Constraints

- Every module has exactly: main.tf, variables.tf, outputs.tf.
- Every variable has a description.
- Every IAM policy uses exact actions and resource ARNs.
- No `Resource: "*"` except where AWS requires it (document exceptions).
- Pin AWS provider to `~> 5.0`.
- Require Terraform `>= 1.5`.
- Follow the Terraform standards in `.ai/steering/terraform-standards.md`.

## Also Generate

- `terraform/tests/basic.tftest.hcl` — at least one test that runs `terraform plan` and asserts outputs are non-empty.
