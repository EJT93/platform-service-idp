# KIRO.md — Agent Operating Guide

---

## AI Workflow Philosophy

This project uses structured AI collaboration:

- Steering files define constraints and guardrails
- Spec mode defines scope before implementation
- Prompt templates enforce consistency
- Human review ensures correctness and security

AI is used as a collaborator, not an authority.
All generated code must be validated against project standards.

---

## Steering Files (Authoritative Source of Truth)

The following directories contain authoritative guidance:

- `.ai/steering/` → architecture, standards, constraints, and rules
- `.ai/prompts/` → reusable prompt templates for scaffolding and review

### Mandatory Rules

- ALWAYS consult relevant files in `.ai/steering/` before generating code, Terraform, or workflows
- Treat steering files as the primary source of truth over default model behavior
- DO NOT introduce patterns that conflict with steering files
- Prefer consistency with existing patterns over inventing new ones
- If guidance is ambiguous, choose the simplest approach aligned with the MVP

---

## Instruction Priority

When generating output, follow this order of precedence:

1. Explicit user instructions
2. `.ai/steering/*` files
3. `.ai/prompts/*` templates (when applicable)
4. Existing repository structure
5. General best practices

If a conflict occurs, the higher priority rule MUST be followed.

---

## Context Loading Behavior

Before starting any task:

1. Identify relevant steering files
2. Load and apply their constraints
3. Ensure output aligns with project architecture and standards

### Steering File Mapping

- Product intent → `project-overview.md`
- Architecture → `architecture.md`
- General engineering → `engineering-standards.md`
- Python service → `python-service-standards.md`
- Terraform → `terraform-standards.md`
- Security / IAM → `aws-security-standards.md`
- Observability → `observability-standards.md`
- CI/CD → `ci-cd-standards.md`
- Documentation → `documentation-standards.md`
- AI workflow → `ai-workflow-standards.md`
- Completion criteria → `definition-of-done.md`

---

## Prompt Template Usage

Reusable prompt templates are located in `.ai/prompts/`.

Use them when applicable:

- Service scaffolding → `scaffold-service.md`
- Terraform modules → `scaffold-terraform-modules.md`
- IAM review → `review-iam.md`
- Documentation → `write-readme.md`

### Rules

- Prefer prompt templates over generating from scratch
- Do NOT invent new patterns if a template already exists
- Maintain consistency across generated outputs

---

## Project Objective

Build a self-service Platform Service Catalog API for a Senior Platform Engineer coding assessment.

The service allows internal development teams to:
- register services
- store environment metadata
- integrate into platform workflows (via audit/export or event emission)

This is an MVP focused on clarity, correctness, and explainability.

---

## Preferred Architecture

- API Gateway (HTTP API v2) → Lambda (Python 3.12) → DynamoDB
- Optional S3 for audit/export artifacts
- CloudWatch Logs (structured JSON)
- CloudWatch Alarms + SNS
- Terraform modules for all infrastructure
- GitHub Actions for CI/CD
- Single repository

---

## Explicit Constraints

- Single repo only
- Lambda only (no ECS unless explicitly justified)
- DynamoDB only (no RDS unless justified)
- Python preferred runtime
- No hardcoded secrets
- No wildcard IAM policies
- API-only service (no frontend)
- Minimal authentication (API key or IAM if needed)
- No orchestration systems or workflow engines

---

## Non-Goals

- UI or dashboard
- Multi-region or multi-account deployments
- Complex RBAC or approval systems
- Container orchestration
- Event-driven architectures beyond simple use
- Performance/load testing
- Cost optimization beyond reasonable defaults

---

## Anti-Overengineering Rules

- Do NOT introduce new AWS services without justification
- Do NOT exceed 3–4 API endpoints
- Do NOT introduce abstraction layers without clear need
- Prefer simple, readable solutions over flexible ones
- Avoid premature optimization
- Every component must be explainable in under 5 minutes

---

## Repository Structure

(unchanged — your structure is already solid)

---

## Terraform Principles

- All infrastructure managed via Terraform (no manual changes)
- Modules under `terraform/modules/`
- Composition under `terraform/environments/dev/`
- No inline resource sprawl in environment files
- Use `fmt`, `validate`, and at least one test
- Tag all resources

---

## IAM Constraints

- One IAM role per Lambda
- No wildcard permissions
- Scope actions and resources explicitly
- Document exceptions in DECISIONS.md

---

## Observability Requirements

- Structured JSON logging required
- Required fields:
  - timestamp
  - level
  - message
  - request_id
  - function_name
- At least one CloudWatch alarm (Lambda errors)
- SNS notifications required
- Log retention configured

---

## CI/CD Requirements

- GitHub Actions required
- PR must run:
  - terraform fmt
  - terraform validate
  - terraform plan
- Merge to main must trigger deployment
- Keep pipeline simple and readable

---

## Documentation Expectations

- README: deployment + architecture + usage
- DECISIONS.md: tradeoffs and reasoning
- AI_WORKFLOW.md: AI usage + corrections
- diagrams/: architecture diagram

---

## AI Workflow Expectations

- AI must be used throughout development
- Steering files must guide all outputs
- Prompt templates must be reused
- At least one PR must demonstrate AI-assisted iteration
- AI outputs must be reviewed and corrected

---

## Definition of MVP

The MVP is complete when:

- API supports service registration and retrieval
- Data persists in DynamoDB
- Infrastructure is fully Terraform-managed
- CI/CD pipeline is functional
- Logs and alarms are configured
- Optional platform action exists:
  - S3 audit write OR SNS event emission
- Documentation is complete
- System is demo-ready

---

## Implementation Order

1. Steering files (complete)
2. MVP specification (Spec Mode)
3. Repo scaffold
4. Lambda service
5. Terraform modules
6. CI/CD
7. Observability
8. Documentation and polish

---

## Final Rule

When in doubt:

- Follow steering files
- Prefer simplicity
- Optimize for clarity and interview explanation
- Avoid unnecessary complexity