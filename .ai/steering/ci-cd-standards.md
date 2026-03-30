# CI/CD Standards

## GitHub Actions as Default

All CI/CD runs on GitHub Actions. No Jenkins, CircleCI, CodePipeline, or other CI systems.

## PR Validation Workflow (`ci.yml`)

Triggered on: `pull_request` to `main`

Steps:
1. Python lint (ruff or flake8)
2. Python unit tests (pytest)
3. Terraform fmt check (`terraform fmt -check -recursive`)
4. Terraform validate (`terraform validate`)
5. Terraform plan (`terraform plan` — output for review, no apply)

All steps must pass before merge. The plan output helps reviewers understand infrastructure changes.

## Main Branch Deployment Workflow (`deploy.yml`)

Triggered on: `push` to `main`

Steps:
1. Package Lambda code (zip the `app/src/` directory with dependencies)
2. Upload package to S3
3. Terraform init
4. Terraform apply (`-auto-approve` is acceptable for dev environment)

This workflow requires AWS credentials configured via GitHub Actions OIDC (preferred) or access key secrets.

## Required Terraform Pipeline Steps

Every Terraform change must go through:
1. `terraform init` — initialize providers and modules
2. `terraform fmt -check` — enforce formatting
3. `terraform validate` — catch syntax and configuration errors
4. `terraform plan` — preview changes (on PR)
5. `terraform apply` — execute changes (on merge to main)

Do not skip `validate` or `fmt -check`. They catch real errors.

## Required Application Checks

On every PR:
- Lint Python code (catch style issues and common bugs)
- Run unit tests (catch regressions)
- Verify the Lambda package can be built (zip step succeeds)

On merge:
- Build and upload the Lambda package
- Deploy via Terraform

## Branch and Commit Hygiene

- `main` is the deployment branch. It should always be deployable.
- Feature work happens on short-lived branches.
- Branch naming: `feature/description`, `fix/description`, `chore/description`
- Commit messages should be descriptive but concise.
- Squash merges are preferred for clean history.
- Leave at least one PR open showing AI-assisted iteration (challenge requirement).

## When Automatic Apply Is Too Risky

For this assessment, auto-apply on merge to dev is acceptable. In a real environment:
- Require manual approval for staging and production.
- Use Terraform plan output as a PR comment for review.
- Consider using Atlantis or Terraform Cloud for plan/apply workflows.
- Never auto-apply destructive changes (table deletions, security group modifications).

Document this as a known simplification in DECISIONS.md.

## Artifact and Package Handling

Lambda deployment package:
1. Install dependencies into a `package/` directory: `pip install -r requirements.txt -t package/`
2. Copy `app/src/*` into `package/`
3. Zip the `package/` directory
4. Upload to S3 with a versioned key or consistent key that Terraform references

Do not commit zip files to git. Do not use Lambda inline code. The S3-based deployment pattern is clean and scalable.

## Keeping CI/CD Simple

- Two workflow files maximum: `ci.yml` and `deploy.yml`.
- Do not create reusable workflow templates for a single project.
- Do not add matrix builds for multiple Python versions or environments.
- Do not add caching unless builds are genuinely slow.
- Do not add Slack notifications, PR comments, or status badges for MVP.
- Do not add integration tests in CI. Unit tests and Terraform validate are sufficient.

The goal is a working pipeline that demonstrates competence, not a production-grade CI/CD platform.

## AWS Credentials in CI/CD

Preferred: OIDC federation with GitHub Actions
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: us-east-1
```

Acceptable for MVP: IAM access key/secret in GitHub Actions secrets
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

Never hardcode credentials in workflow files.
