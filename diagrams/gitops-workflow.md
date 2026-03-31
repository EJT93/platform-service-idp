# GitOps Workflow — Platform Service IDP

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Developer Workflow                                │
│                                                                          │
│  Developer ──► Feature Branch ──► Push ──► Open PR to main              │
└──────────────────────┬───────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    CI Pipeline (ci.yml)                                   │
│                    Trigger: pull_request → main                          │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────────────┐ │
│  │ python-lint  │  │ python-test │  │ terraform-validate               │ │
│  │              │  │             │  │                                  │ │
│  │ ruff check   │  │ pytest -v   │  │ terraform init -backend=false   │ │
│  │ app/src/     │  │ app/tests/  │  │ terraform validate              │ │
│  │              │  │             │  │ terraform fmt -check -recursive  │ │
│  └──────────────┘  └─────────────┘  └───────────────┬──────────────────┘ │
│                                                     │                    │
│                                              ┌──────▼──────────────────┐ │
│                                              │ terraform-plan          │ │
│                                              │ (needs: validate)       │ │
│                                              │                         │ │
│                                              │ OIDC ──► AWS STS       │ │
│                                              │ terraform init          │ │
│                                              │ terraform plan          │ │
│                                              │   -var-file=dev.tfvars  │ │
│                                              └─────────────────────────┘ │
│                                                                          │
│  Result: PR shows plan output, all checks must pass before merge        │
└──────────────────────────────────────────────────────────────────────────┘
                       │
                       │  Merge PR
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  Deploy Pipeline (deploy.yml)                             │
│                  Trigger: push → main                                    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        deploy job                                │   │
│  │                                                                  │   │
│  │  1. Checkout code                                                │   │
│  │     └── actions/checkout@v4                                      │   │
│  │                                                                  │   │
│  │  2. Setup Python 3.12                                            │   │
│  │     └── actions/setup-python@v5                                  │   │
│  │                                                                  │   │
│  │  3. Authenticate to AWS                                          │   │
│  │     └── OIDC ──► AssumeRoleWithWebIdentity                      │   │
│  │         └── Role: github-actions-deploy                          │   │
│  │             └── Trust: repo:EJT93/platform-service-idp:*         │   │
│  │                                                                  │   │
│  │  4. Package Lambda                                               │   │
│  │     └── scripts/package-lambda.sh --upload <bucket> <key>        │   │
│  │         ├── pip install -r requirements.txt -t build/            │   │
│  │         ├── cp -r src/* build/                                   │   │
│  │         ├── zip -r lambda.zip build/                             │   │
│  │         └── aws s3 cp lambda.zip s3://artifacts/lambda/          │   │
│  │                                                                  │   │
│  │  5. Terraform Apply                                              │   │
│  │     └── terraform init                                           │   │
│  │     └── terraform apply -var-file=dev.tfvars -auto-approve       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Result: Infrastructure updated, Lambda code deployed                   │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                     Security Model                                       │
│                                                                          │
│  ┌─────────────┐     OIDC Token      ┌──────────────────────────┐       │
│  │ GitHub       │ ──────────────────► │ AWS IAM OIDC Provider    │       │
│  │ Actions      │                     │ token.actions.           │       │
│  │ Runner       │ ◄────────────────── │ githubusercontent.com    │       │
│  └─────────────┘   Temporary Creds   └──────────────────────────┘       │
│                     (15 min TTL)                                         │
│                                                                          │
│  No static credentials stored anywhere.                                 │
│  Role trust scoped to specific repo.                                    │
│  Permissions scoped to specific resources (no wildcards).               │
└──────────────────────────────────────────────────────────────────────────┘
```
