# Prompt: Review IAM Policies for Least Privilege

## Context

This project has a hard requirement: no wildcard IAM policies. Every policy must specify exact actions and resource ARNs. Reviewers will check this carefully.

## Task

Review all IAM-related Terraform code in `terraform/modules/iam/` and any other module that defines IAM resources. Check for violations and suggest corrections.

## Checklist

For every `aws_iam_policy_document` or `aws_iam_role_policy`:

1. Actions check:
   - Are all actions explicitly listed? (e.g., `dynamodb:GetItem`, not `dynamodb:*`)
   - Are only the actions the Lambda function actually uses included?
   - Are there any `Action: "*"` statements?

2. Resources check:
   - Are all resources scoped to specific ARNs? (e.g., `aws_dynamodb_table.this.arn`)
   - Are there any `Resource: "*"` statements?
   - If `Resource: "*"` exists, is it genuinely required by the AWS API? (Document why.)

3. Trust policy check:
   - Does the assume role policy scope to `lambda.amazonaws.com` only?
   - Are there any overly broad principals?

4. Managed policy check:
   - Is `AWSLambdaBasicExecutionRole` the only managed policy attached?
   - Are there any other AWS managed policies that grant broader access than needed?

5. Cross-module check:
   - Does the Lambda module or any other module define inline IAM policies?
   - Are those policies also least-privilege?

## Expected DynamoDB Actions

For the service catalog CRUD operations, the Lambda function needs exactly:
- `dynamodb:PutItem` (create)
- `dynamodb:GetItem` (read)
- `dynamodb:Scan` (list)
- `dynamodb:DeleteItem` (delete)

It does not need: `dynamodb:UpdateItem`, `dynamodb:Query`, `dynamodb:BatchWriteItem`, `dynamodb:DescribeTable`, or any other action.

## Expected S3 Actions (if audit writes are implemented)

- `s3:PutObject` (write audit records)

It does not need: `s3:GetObject`, `s3:DeleteObject`, `s3:ListBucket`, or any other action unless explicitly required.

## Output

For each finding:
- State the file and line where the issue exists.
- State what the current policy allows.
- State what it should allow.
- Provide the corrected Terraform code.

If no issues are found, confirm that all policies are least-privilege compliant.
