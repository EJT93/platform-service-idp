# Definition of Done

## What Counts as MVP Complete

The MVP is complete when all four categories below are satisfied. Nothing more is required.

## Infrastructure Complete Criteria

- [ ] DynamoDB table created via Terraform module with PITR enabled
- [ ] S3 bucket created via Terraform module with encryption, versioning, and public access blocked
- [ ] IAM role created via Terraform module with least-privilege policies (no wildcards)
- [ ] Lambda function created via Terraform module, deployed from S3 package
- [ ] API Gateway HTTP API created via Terraform module, integrated with Lambda
- [ ] CloudWatch Log Group created with 14-day retention
- [ ] CloudWatch Alarm on Lambda errors with SNS notification target
- [ ] SNS topic created for alarm notifications
- [ ] All resources tagged with Environment, Project, ManagedBy
- [ ] `terraform plan` runs cleanly with no errors
- [ ] `terraform validate` passes
- [ ] `terraform fmt -check` passes
- [ ] At least one `tftest.hcl` test exists and passes
- [ ] Environment composition in `terraform/environments/dev/` stitches all modules together

## Service Complete Criteria

- [ ] POST /services — creates a service record in DynamoDB, returns 201
- [ ] GET /services — lists all service records, returns 200
- [ ] GET /services/{id} — returns a specific service record, returns 200 or 404
- [ ] DELETE /services/{id} — deletes a service record, returns 204
- [ ] Input validation rejects requests missing required fields with 400
- [ ] Invalid JSON returns 400
- [ ] Unknown routes return 404
- [ ] Unhandled errors return 500 with generic message (no stack trace to client)
- [ ] All errors logged with structured JSON including stack traces
- [ ] All successful operations logged at INFO level
- [ ] Handler/service/model separation is clean
- [ ] Unit tests exist for handler, service, and validation logic
- [ ] `pytest` passes with no failures

## Documentation Complete Criteria

- [ ] README.md includes: description, architecture overview, prerequisites, deployment steps, API usage examples, design rationale, repo structure
- [ ] DECISIONS.md includes at least 4 architectural decisions with context and tradeoffs
- [ ] AI_WORKFLOW.md documents AI tool usage, what worked, what was corrected
- [ ] Architecture diagram exists in `diagrams/` showing the full request flow
- [ ] KIRO.md and steering files are present and accurate

## AI Workflow Complete Criteria

- [ ] AI agent configuration exists in repo (KIRO.md, .ai/ directory)
- [ ] At least one PR is open showing AI-assisted iteration
- [ ] PR shows evidence of human review and correction
- [ ] AI_WORKFLOW.md documents the development process
- [ ] Developer can explain AI usage, corrections, and lessons learned

## What Can Be Deferred

These are explicitly not required for MVP and should not be built:
- PUT /services/{id} (update endpoint)
- Environment sub-resources (/services/{id}/environments)
- S3 audit writes (nice-to-have, not required)
- Pagination on list endpoint
- Authentication (API key or IAM auth)
- CloudWatch dashboard
- X-Ray tracing
- Custom CloudWatch metrics
- Multi-environment deployment (staging, prod)
- Remote Terraform state backend
- Integration tests against real AWS
- Docker containerization of Lambda
- Any frontend or UI

If time permits, add one or two of these as polish. Prioritize in this order:
1. S3 audit writes (demonstrates multi-store pattern)
2. PUT endpoint (completes CRUD)
3. API key authentication (demonstrates security awareness)

## Pre-Demo Checklist

Run through this before submitting or presenting:

- [ ] `terraform plan` shows no errors and expected resources
- [ ] `terraform apply` succeeds (or has succeeded at least once)
- [ ] API Gateway endpoint is reachable
- [ ] POST a service record and GET it back successfully
- [ ] Check CloudWatch Logs for structured JSON entries
- [ ] Verify the CloudWatch Alarm exists in the console
- [ ] `pytest` passes locally
- [ ] CI pipeline passes on the latest commit
- [ ] README deployment steps are accurate and copy-pasteable
- [ ] No secrets are committed anywhere in the repo
- [ ] IAM policies have no wildcards (grep for `"*"` in Terraform)
- [ ] At least one PR is open with AI-assisted iteration visible
- [ ] Architecture diagram is present and accurate
- [ ] You can explain every file in the repo in 30 seconds or less
