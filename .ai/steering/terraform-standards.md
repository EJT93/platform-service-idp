# Terraform Standards

## Module Structure

Every module lives in `terraform/modules/<module_name>/` and contains exactly three files:

```
terraform/modules/<module_name>/
├── main.tf          # Resource definitions
├── variables.tf     # Input variables with descriptions and defaults
└── outputs.tf       # Output values
```

Do not add `providers.tf` inside modules. Provider configuration belongs in the environment composition layer.

Do not add `locals.tf` as a separate file in modules. Use a `locals` block in `main.tf` if needed.

## Environment Layering

Environment-specific composition lives in `terraform/environments/<env>/`:

```
terraform/environments/dev/
├── main.tf                    # Provider config + module calls
├── variables.tf               # Environment-level variables
├── outputs.tf                 # Environment-level outputs
├── terraform.tfvars.example   # Example variable values (committed)
├── terraform.tfvars           # Actual values (gitignored)
└── backend.tf                 # Remote state configuration
```

The environment layer stitches modules together. It does not define resources directly. If you find yourself writing `resource` blocks in the environment layer, move them into a module.

## Resource Naming

All resources follow the pattern: `{project}-{resource_purpose}-{environment}`

Examples:
- DynamoDB table: `platform-services-dev`
- S3 bucket: `platform-services-audit-dev`
- Lambda function: `platform-services-dev`
- IAM role: `platform-services-dev-role`
- CloudWatch log group: `/aws/lambda/platform-services-dev`

Use variables to construct names. Do not hardcode environment or project names in modules.

## Tagging Conventions

Every taggable resource must include these tags:

```hcl
tags = {
  Environment = var.environment    # e.g., "dev", "staging", "prod"
  Project     = var.project_name   # e.g., "platform-services"
  ManagedBy   = "terraform"
}
```

Use `default_tags` in the provider block for environment-wide defaults. Pass a `tags` variable to modules for resource-specific tags.

## Variables and Outputs

Variables:
- Every variable must have a `description`.
- Use `type` constraints (`string`, `number`, `bool`, `map(string)`, `list(string)`).
- Provide sensible `default` values where appropriate.
- Do not default sensitive values. Force them to be provided.
- Use `sensitive = true` for secrets.

Outputs:
- Output values that other modules or the environment layer need.
- Output ARNs, names, and endpoints — not entire resource objects.
- Every output must have a `description` or at minimum a clear name.

## Remote State

For the MVP, local state is acceptable. If using remote state:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "platform-services/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

Do not commit `terraform.tfstate` files. Add them to `.gitignore`.

## Reuse Guidance

Modules should be reusable across environments without modification. Achieve this by:
- Parameterizing all environment-specific values (names, tags, sizes).
- Using variables with defaults for optional configuration.
- Not hardcoding AWS account IDs, regions, or environment names.

Do not over-abstract. A module used in only one environment does not need to support every possible configuration. Build for the current need with reasonable extension points.

## Least Privilege IAM

This is a hard requirement. Every IAM policy must:
- Specify exact actions (e.g., `dynamodb:GetItem`, `dynamodb:PutItem`). Never `dynamodb:*`.
- Specify exact resource ARNs. Never `Resource: "*"` unless the AWS API requires it.
- Use `data "aws_iam_policy_document"` for policy construction (type-safe, readable).
- Attach only the permissions the Lambda function actually needs.

Acceptable exceptions (document in DECISIONS.md):
- `logs:CreateLogGroup` may require `Resource: "*"` depending on the pattern.
- `AWSLambdaBasicExecutionRole` managed policy is acceptable for CloudWatch Logs access.

## No Wildcard IAM Rule

This deserves its own section because it is a challenge requirement.

Bad:
```hcl
actions   = ["dynamodb:*"]
resources = ["*"]
```

Good:
```hcl
actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem", "dynamodb:Scan"]
resources = [aws_dynamodb_table.this.arn]
```

## Secret Handling

- No secrets in Terraform code, variable defaults, or tfvars committed to git.
- Use `terraform.tfvars` (gitignored) for sensitive values locally.
- Use SSM Parameter Store or Secrets Manager for runtime secrets.
- Use `sensitive = true` on variables and outputs that contain secrets.
- In CI/CD, pass secrets via GitHub Actions secrets and environment variables.

## Formatting, Linting, and Testing

- Run `terraform fmt -recursive` before every commit.
- Run `terraform validate` in CI.
- Write at least one `tftest.hcl` test that validates a plan.
- Use `terraform fmt -check -recursive` in CI to enforce formatting.

## Plan/Apply Workflow

- PRs trigger `terraform plan`. The plan output should be reviewable.
- Merges to main trigger `terraform apply -auto-approve` (acceptable for dev environment).
- Never run `terraform apply` without a preceding `terraform plan` in CI.
- Never run `terraform destroy` in CI without explicit confirmation.

## What Belongs in a Module vs Environment Composition

In a module:
- Resource definitions
- IAM policies specific to those resources
- Default configuration values
- Internal wiring between resources in the module

In environment composition:
- Provider configuration
- Module instantiation with environment-specific values
- Cross-module wiring (e.g., passing DynamoDB ARN from dynamodb module to IAM module)
- Backend configuration

## Anti-Patterns to Avoid

- Defining resources directly in the environment layer.
- Creating a "shared" module that contains unrelated resources.
- Using `count` or `for_each` for complexity that does not exist yet.
- Over-parameterizing modules with variables that have only one possible value.
- Nesting modules (module calling another module).
- Using `terraform_remote_state` data source for cross-module communication (use outputs and variables instead).
- Creating separate modules for trivially small resources (e.g., a single SSM parameter).
