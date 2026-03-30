# Platform Service IDP

A serverless platform service built with AWS Lambda, API Gateway, and DynamoDB, managed with Terraform.

## Structure

```
app/          — Python Lambda service (handler, models, services, utils)
terraform/    — Infrastructure as Code (modular Terraform)
.github/      — CI/CD workflows
.ai/          — AI steering files and prompt templates
docs/         — Architecture decisions and workflow docs
diagrams/     — Architecture diagrams
```

## Quick Start

### Prerequisites

- Python 3.12+
- Terraform >= 1.5
- AWS CLI configured

### Local Development

```bash
cd app
pip install -r requirements.txt
python -m pytest tests/
```

### Infrastructure

```bash
cd terraform/environments/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## CI/CD

- PRs trigger lint, validate, and plan
- Merges to `main` trigger deploy
