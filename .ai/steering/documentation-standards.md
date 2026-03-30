# Documentation Standards

## README Minimum Required Sections

The README.md must include:

1. Project title and one-sentence description
2. Architecture overview (brief prose + reference to diagram)
3. Prerequisites (tools, versions, AWS access)
4. Quick start / deployment steps (copy-pasteable commands)
5. API usage examples (curl commands for each endpoint)
6. Design rationale (2-3 paragraphs on why this architecture)
7. What would change in production (brief list of improvements)
8. Repository structure (tree view with one-line descriptions)

Do not include:
- Lengthy tutorials on how Terraform or Lambda work
- Copy-pasted AWS documentation
- Sections with no content ("TODO" placeholders)
- Badges or shields unless they add real value

## DECISIONS.md Content Expectations

Each decision should follow this format:

```
## ADR-NNN: Title

Status: Accepted | Superseded | Deprecated

Context: What situation or requirement prompted this decision.

Decision: What was decided and why.

Consequences: What tradeoffs result. What becomes easier or harder.
```

Minimum decisions to document:
- Lambda vs ECS
- DynamoDB vs RDS
- Single repo vs multi-repo
- CI/CD approach (GitHub Actions, auto-apply)
- Auth approach (deferred, API key, IAM)
- Observability scope (what is included, what is deferred)

Keep each ADR to 5-10 sentences. Reviewers want to see that you thought about tradeoffs, not that you can write essays.

## Architecture Diagram Expectations

- Include at least one diagram in `diagrams/`.
- The diagram should show: client → API Gateway → Lambda → DynamoDB/S3, plus CloudWatch/SNS.
- Use draw.io, Lucidchart, Mermaid, or any tool that produces a clear PNG/SVG.
- Include the source file (`.drawio`, `.mmd`) alongside the rendered image.
- The diagram should be understandable in 10 seconds. Label every component.
- Do not include AWS account boundaries, VPC details, or networking unless relevant.

## How to Explain Tradeoffs

When documenting a tradeoff:
- State what you chose and what you rejected.
- Give one concrete reason for the choice.
- Acknowledge one downside of the choice.
- Mention when you would reconsider.

Example: "We chose DynamoDB over RDS because the data model is simple key-value lookups and DynamoDB requires zero capacity management. The tradeoff is limited query flexibility — if we needed complex joins or full-text search, RDS would be the better choice."

## How Much Detail Is Appropriate

- README: enough for someone to deploy and use the service in 10 minutes.
- DECISIONS.md: enough for a reviewer to understand your reasoning in 5 minutes.
- AI_WORKFLOW.md: enough for an interviewer to understand your AI usage in 3 minutes.
- Code comments: explain why, not what. The code should explain what.
- Terraform comments: explain non-obvious configuration choices.

More is not better. Concise, accurate documentation beats comprehensive, unread documentation.

## What Reviewers Are Likely Looking For

Experienced platform engineering reviewers will evaluate:
- Can I understand the architecture in under 2 minutes?
- Can I deploy this by following the README?
- Are the Terraform modules well-structured and reusable?
- Are IAM policies least-privilege?
- Is the code clean, simple, and well-organized?
- Is there evidence of thoughtful decision-making?
- Is observability present and practical?
- Does the CI/CD pipeline work?
- Was AI used effectively and transparently?

They are not looking for:
- Feature completeness
- Production-grade hardening
- Complex architectures
- Extensive test coverage
- Beautiful formatting

Optimize documentation for the first list, not the second.
