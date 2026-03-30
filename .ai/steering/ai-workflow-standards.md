# AI Workflow Standards

## How AI Should Be Used During This Project

AI is a core development tool for this project, not an afterthought. Use it for:
- Scaffolding project structure and boilerplate
- Generating initial implementations of handlers, services, and models
- Writing Terraform modules and environment composition
- Generating unit tests
- Writing documentation drafts
- Reviewing IAM policies for least privilege
- Debugging errors and suggesting fixes
- Refactoring code for clarity

Do not use AI as a black box. Every generated artifact must be reviewed, understood, and potentially corrected by the developer.

## What Kinds of Tasks Are Good for AI Scaffolding

High-value AI tasks (generate and review):
- Initial file structure and boilerplate
- CRUD handler logic
- DynamoDB service layer with boto3 calls
- Terraform module skeletons
- IAM policy documents
- GitHub Actions workflow files
- Unit test scaffolding
- README and documentation drafts
- Input validation logic
- Structured logging setup

Medium-value AI tasks (generate, review carefully):
- Error handling patterns
- CloudWatch alarm configuration
- S3 bucket security configuration
- API Gateway integration setup

Low-value AI tasks (write manually or review very carefully):
- IAM trust policies and permission boundaries
- Security-sensitive configuration
- Complex business logic (if any)
- Terraform backend configuration

## Where Human Review Is Mandatory

Never blindly accept AI output for:
- IAM policies — verify every action and resource ARN
- Security configuration — encryption, public access, network exposure
- Terraform state and backend configuration
- Secrets handling — ensure nothing sensitive is hardcoded
- API response structures — ensure consistency
- Error messages — ensure they do not leak internal details
- CI/CD pipeline steps — ensure correct ordering and credentials handling

## Examples of Likely AI Failure Modes

Be prepared for these common AI mistakes:

1. Over-engineering: AI tends to add features, abstractions, and complexity beyond what was asked. Watch for unnecessary base classes, plugin systems, middleware chains, or configuration frameworks.

2. Wildcard IAM policies: AI frequently generates `Resource: "*"` or `Action: "s3:*"`. Always check and narrow.

3. Inconsistent naming: AI may use different naming conventions across files (camelCase in one, snake_case in another). Enforce consistency.

4. Hallucinated AWS API parameters: AI may use boto3 parameters that do not exist or are deprecated. Verify against AWS documentation.

5. Missing error handling: AI often generates happy-path code and forgets edge cases. Add error handling explicitly.

6. Outdated patterns: AI may use Python 2 patterns, old Terraform syntax, or deprecated AWS features. Verify currency.

7. Incomplete Terraform: AI may generate resources without required attributes or with incorrect type constraints. Run `terraform validate` immediately.

8. Test mocking errors: AI frequently mocks at the wrong level (mocking the function under test instead of its dependencies). Review test logic carefully.

9. Verbose implementations: AI tends to write more code than necessary. Actively trim and simplify.

10. Copy-paste documentation: AI may generate generic documentation that does not match the actual implementation. Ensure docs reflect reality.

## How to Document AI-Assisted Work

Maintain `docs/AI_WORKFLOW.md` with:
- Which AI tools were used (Kiro, Claude, Copilot, etc.)
- What tasks were delegated to AI
- What required human correction
- What worked well
- What would be done differently next time

In commit messages, note when AI generated the initial version:
- "feat: scaffold service handler (AI-generated, reviewed)"
- "fix: narrow IAM policy to specific actions (corrected from AI draft)"

In PR descriptions, include a brief note on AI usage for that PR.

## Expectations for the Open PR

The challenge requires at least one open PR showing AI-assisted iteration. This PR should demonstrate:
- AI-generated initial implementation
- Human review comments or commit messages showing corrections
- Iterative improvement (not just a single AI dump)
- Clear commit history showing the progression

Good PR narrative: "AI scaffolded the handler and tests. I corrected the IAM policy, fixed the error response format, and added missing validation for the owner field."

Bad PR narrative: "AI wrote everything and it worked."

## How to Discuss Course-Correction in the Interview

Be prepared to explain:
- "The AI generated wildcard IAM policies. I narrowed them to specific actions and resource ARNs."
- "The AI over-engineered the error handling with a custom exception hierarchy. I simplified it to basic try/except with structured logging."
- "The AI missed input validation for the runtime field. I added it manually."
- "The Terraform module AI generated was missing the S3 public access block. I added it."

Frame corrections as evidence of engineering judgment, not AI failure.

## How to Avoid Blindly Accepting Generated Code

1. Read every line before committing. If you cannot explain it, do not commit it.
2. Run `terraform validate` and `terraform plan` immediately after generating Terraform.
3. Run `pytest` immediately after generating tests.
4. Check IAM policies against the least-privilege checklist.
5. Verify that generated code matches the steering file standards.
6. Ask yourself: "Is this simpler than it needs to be?" If not, simplify.
7. Ask yourself: "Would I be comfortable explaining this in an interview?" If not, rewrite.
