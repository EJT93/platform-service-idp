# Production Architecture — Platform Service IDP

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AWS Account (us-east-2)                            │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        API Gateway v2 (HTTP API)                         │   │
│  │                    platform-service-dev-api                               │   │
│  │                                                                          │   │
│  │   Routes:                                                                │   │
│  │   ├── $default ──────────────► Service Catalog Lambda                    │   │
│  │   └── GET /platform/audit ──► Audit Lambda                              │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│           │                                    │                                │
│           ▼                                    ▼                                │
│  ┌─────────────────────┐          ┌──────────────────────────┐                 │
│  │  Lambda: Service     │          │  Lambda: Audit            │                 │
│  │  Catalog API         │          │  (Operational Intel)      │                 │
│  │  (Python 3.12)       │          │  (Python 3.12)            │                 │
│  │                      │          │                           │                 │
│  │  POST /services      │          │  GET /platform/audit      │                 │
│  │  GET  /services      │          │  ├── S3 encryption audit  │                 │
│  │  GET  /services/{id} │          │  ├── DynamoDB backup audit│                 │
│  │  DELETE /services/{id}│         │  ├── Lambda config audit  │                 │
│  │                      │          │  └── Log retention audit  │                 │
│  │  IAM Role:           │          │                           │                 │
│  │  platform-service-   │          │  IAM Role:                │                 │
│  │  dev-role            │          │  platform-service-        │                 │
│  │  (DynamoDB + SSM)    │          │  dev-audit-role           │                 │
│  └──────────┬───────────┘          │  (Read-only + S3 write)   │                 │
│             │                      └─────────┬─────────────────┘                │
│             │                                │                                  │
│     ┌───────▼────────┐              ┌────────▼──────────┐                       │
│     │  SSM Parameter  │              │  S3: Artifacts     │                      │
│     │  Store           │              │  Bucket            │                      │
│     │  /platform-      │              │  ├── lambda/       │                      │
│     │  service/dev/    │              │  │   package.zip   │                      │
│     │  dynamodb-table  │              │  └── audit-reports/│                      │
│     └───────┬──────────┘              │      └── *.json    │                      │
│             │                         │                    │                      │
│             │ resolves to             │  Versioned, KMS    │                      │
│             ▼                         │  encrypted, public │                      │
│     ┌────────────────┐               │  access blocked    │                      │
│     │  DynamoDB       │               └────────────────────┘                     │
│     │  platform-      │                                                          │
│     │  services-dev   │                                                          │
│     │                 │                                                          │
│     │  PAY_PER_REQUEST│                                                          │
│     │  PITR enabled   │                                                          │
│     └─────────────────┘                                                          │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │                          Observability Layer                              │   │
│  │                                                                           │   │
│  │  CloudWatch Logs ──► /aws/lambda/platform-service-dev (14-day retention) │   │
│  │                                                                           │   │
│  │  CloudWatch Alarm ──► Lambda Errors > 0 / 5min ──► SNS Topic            │   │
│  │                                                        │                  │   │
│  │                                                        ▼                  │   │
│  │                                                   Email Subscription     │   │
│  │                                                   (alert_emails list)    │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │                          CI/CD Authentication                             │   │
│  │                                                                           │   │
│  │  GitHub OIDC Provider ──► IAM Role: github-actions-deploy                │   │
│  │  (token.actions.          (Scoped permissions, no wildcards)              │   │
│  │   githubusercontent.com)                                                   │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │                          Terraform State                                  │   │
│  │                                                                           │   │
│  │  S3: elijah-terraform-state (encrypted, versioned)                       │   │
│  │  DynamoDB: elijah-terraform-lock-table (state locking)                   │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────┘
```
