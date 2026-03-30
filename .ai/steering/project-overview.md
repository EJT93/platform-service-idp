# Project Overview

## What This Service Is

The Platform Service Catalog API is a self-service REST API that allows internal development teams to register and manage metadata about their services and deployment environments. It is the kind of internal developer platform (IDP) capability that a platform engineering team would build to improve visibility, standardization, and operational awareness across an organization.

## Who the Internal User Is

The primary users are development teams and team leads who need to:
- Register a new service with the platform team
- Record which environments a service is deployed to
- Query the catalog to understand what services exist and where they run
- Maintain up-to-date metadata about service ownership, runtime, and dependencies

Secondary users are platform engineers who consume this data for operational dashboards, compliance reporting, or automation triggers.

## What Problem It Solves

In organizations with many teams and services, there is no single source of truth for "what services exist, who owns them, and where are they deployed." Teams use spreadsheets, wikis, or tribal knowledge. This API provides a structured, queryable, API-first catalog that can be integrated into CI/CD pipelines, dashboards, and operational tooling.

## Why This Is a Valid Internal Platform Capability

Service catalogs are a foundational component of internal developer platforms. They appear in Backstage, Cortex, OpsLevel, and similar tools. Building a lightweight version demonstrates:
- Understanding of platform product thinking
- Ability to design APIs for internal consumers
- Practical application of serverless architecture
- Infrastructure-as-code discipline
- Observability awareness

## What the MVP Does

The MVP supports:
- POST /services — Register a new service with metadata (name, owner, description, runtime)
- GET /services — List all registered services
- GET /services/{id} — Get a specific service by ID
- DELETE /services/{id} — Remove a service registration

Each service record includes: `service_id`, `name`, `owner`, `description`, `runtime`, `created_at`, `updated_at`.

Optional for MVP:
- PUT /services/{id} — Update a service registration
- POST /services/{id}/environments — Register an environment for a service
- S3 export of catalog data for audit purposes

## What Is Intentionally Deferred

- Authentication and authorization (API key or IAM auth is sufficient for MVP)
- Environment sub-resources (can be added as a fast follow)
- Search and filtering beyond basic list/get
- Pagination (acceptable to defer if the catalog is small)
- Approval workflows for service registration
- Integration with CI/CD pipelines as a consumer
- UI or dashboard
- Multi-region or multi-account deployment
- Versioning of service metadata
- Event-driven notifications on catalog changes
