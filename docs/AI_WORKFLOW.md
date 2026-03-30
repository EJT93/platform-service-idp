# AI-Assisted Development Workflow

## Tools Used

- Kiro (AI IDE) for code generation, review, and iteration
- AI steering files (`.ai/steering/`) to constrain and guide agent behavior
- AI prompt templates (`.ai/prompts/`) for repeatable scaffolding tasks

## Development Phases

### Phase 1: Steering and Guidance
AI generated the initial steering files, project standards, and prompt templates. Human reviewed and refined to ensure they matched the challenge requirements and architectural preferences.

### Phase 2: Infrastructure Scaffolding
AI scaffolded Terraform modules using the `scaffold-terraform-modules.md` prompt. Human reviewed IAM policies for least-privilege compliance and corrected resource naming.

### Phase 3: Service Implementation
AI scaffolded the Python Lambda service using the `scaffold-service.md` prompt. Human reviewed error handling, input validation, and response structure for consistency.

### Phase 4: CI/CD and Documentation
AI generated GitHub Actions workflows and documentation drafts. Human verified pipeline steps and ensured README deployment instructions were accurate.

## What Worked Well

- Steering files effectively constrained AI output and prevented over-engineering.
- Terraform module scaffolding was fast and structurally correct.
- Prompt templates made it easy to regenerate components after corrections.

## What Required Human Correction

(To be filled in during implementation)

- IAM policy scope:
- Error handling patterns:
- Naming consistency:
- Test mocking approach:

## What Would Improve Next Time

(To be filled in after implementation)

- Steering refinements:
- Prompt improvements:
- Workflow changes:

## Open PR

(Link to the PR demonstrating AI-assisted iteration)

PR #___: [Title]
- What AI generated
- What was corrected
- Key commits showing iteration
