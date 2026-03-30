# Prompt: Write the README

## Context

You are writing the README.md for the Platform Service Catalog API. This is a coding assessment submission for a Senior Platform Engineer role. The README is one of the first things reviewers will read. It must be clear, concise, and demonstrate platform engineering competence.

## Task

Write `README.md` with the following sections. Do not add sections beyond these.

## Required Sections

### 1. Title and Description
- Project name: Platform Service Catalog API
- One-sentence description of what it does and who it is for.

### 2. Architecture
- 2-3 sentences describing the architecture.
- Reference the diagram in `diagrams/`.
- List the AWS services used and their purpose (brief table or list).

### 3. Prerequisites
- AWS account with appropriate permissions
- Terraform >= 1.5
- Python 3.12+
- AWS CLI configured
- GitHub repository with Actions enabled

### 4. Deployment
- Step-by-step commands to deploy from scratch.
- Include: clone, configure tfvars, terraform init/plan/apply.
- Include: how to find the API endpoint after deployment.
- Commands must be copy-pasteable.

### 5. API Usage
- curl examples for each endpoint:
  - POST /services (create)
  - GET /services (list)
  - GET /services/{id} (get)
  - DELETE /services/{id} (delete)
- Show example request bodies and expected responses.

### 6. Local Development
- How to install dependencies
- How to run tests
- How to lint

### 7. Design Rationale
- 2-3 paragraphs explaining:
  - Why this service (platform self-service catalog)
  - Why this architecture (Lambda + DynamoDB + API Gateway)
  - What tradeoffs were made for MVP scope
- Reference DECISIONS.md for detailed ADRs.

### 8. What Would Change in Production
- Brief list (5-7 items) of what you would add for production readiness.
- Examples: auth, pagination, multi-environment, monitoring dashboard, CI/CD approval gates.

### 9. Repository Structure
- Tree view of the repo with one-line descriptions for each directory.

### 10. AI-Assisted Development
- 2-3 sentences noting that AI tools were used.
- Reference AI_WORKFLOW.md for details.
- Reference the open PR for iteration examples.

## Constraints

- Total length: 150-250 lines of markdown.
- No filler content or placeholder sections.
- No badges or shields.
- No lengthy explanations of how AWS services work.
- Write for an audience of experienced platform engineers.
- Every command must actually work with the deployed infrastructure.
