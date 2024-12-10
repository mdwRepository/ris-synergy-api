# RIS Synergy Server Routes

This document describes the routes provided by the `ris-synergy` blueprint for serving schemas, organizational data, 
and project-related endpoints.

## Table of Contents
1. [Schema Endpoints](#schema-endpoints)
2. [Data Endpoints](#data-endpoints)
3. [Swagger Documentation](#swagger-documentation)
4. [Utility Notes](#utility-notes)
                   
---
                   
## Schema Endpoints

| **Endpoint**                       | **Method** | **Description**                        |
|------------------------------------|------------|----------------------------------------|
| `/ris-synergy/ris_synergy.json`    | GET        | Serves the RIS Synergy JSON schema.    |
| `/ris-synergy/v1/info/schema`      | GET        | Serves the JSON schema for info.       |
| `/ris-synergy/v1/orgUnits/schema`  | GET        | Serves the JSON schema for org units.  |
| `/ris-synergy/v1/projects/schema`  | GET        | Serves the JSON schema for projects.   |

---

## Data Endpoints

| **Endpoint**                                     | **Method** | **Description**                               |
|--------------------------------------------------|------------|-----------------------------------------------|
| `/ris-synergy/v1/info`                           | GET        | Fetches general information data.             |
| `/ris-synergy/v1/orgUnits/organigram`            | GET        | Serves the full organizational hierarchy.     |
| `/ris-synergy/v1/orgUnits/organigram/<date>`     | GET        | Fetches org hierarchy for a specific date.    |
| `/ris-synergy/v1/orgUnits/<orgunit_id>`          | GET        | Fetches details of a specific organizational unit. |

---

## Swagger Documentation

Swagger UI integration for viewing API specs.

| **Endpoint**                     | **Description**                             |
|----------------------------------|---------------------------------------------|
| `/ris-synergy/apidocs/info`      | Swagger documentation for the info schema.  |
| `/ris-synergy/apidocs/orgunit`   | Swagger documentation for org unit schema.  |
| `/ris-synergy/apidocs/project`   | Swagger documentation for project schema.   |

Access these endpoints to view API specs in the Swagger UI. 
Additionally, the Swagger UI can be accessed at the root URL `/apidocs` too. 
This view provides an integrated API overview. As The OpenAPI spec requires that all 
operationId values must be unique across the entire document, even if they are in different 
paths or resource contexts, we had to rename the operationId values in the Swagger UI for
this view.

findAll turned into findAllProjects, or findAllOrganizations, etc.

---

## Notes

- **Security**: Routes with `@keycloak_protected` require Keycloak authentication.
- **Content-Type**: All routes support `application/json`.
- **Error Handling**: Returns HTTP `500` for internal errors and `404` for missing data.
- **File Replacement**: `{{SERVER_URL}}` placeholders in schemas are dynamically replaced with 
   the `OPEN_API_SERVER_URL` environment variable.
