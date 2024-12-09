# RIS Synergy API - Flask Implementation


[![Pylint](https://github.com/mdwRepository/ris-synergy-api/actions/workflows/pylint.yml/badge.svg)](https://github.com/mdwRepository/ris-synergy-api/actions/workflows/pylint.yml)
[![Bandit](https://github.com/mdwRepository/ris-synergy-api/actions/workflows/bandit.yml/badge.svg)](https://github.com/mdwRepository/ris-synergy-api/actions/workflows/bandit.yml)


Reference Implementation of the RIS-Synergy OpenAPI Endpoints in Flask.


## What is RIS Synergy?


RIS Synergy is a collaborative initiative to enhance Austria's research infrastructure by standardizing the data exchange of research information systems (CRIS).


RIS Synergy fosters interoperability and transparency among Austrian research institutions, funding agencies, and public administration systems by developing APIs, a centralized Registry, and automated data workflows.


## About the RIS Synergy Portal


This repository contains the source code and implementations for the RIS Synergy Server in Python / Flask. At its heart is the RESTful API designed to facilitate the exchange of research metadata, such as organizational structures, projects, and funding information.


The APIs follow the [OpenAPI specification](https://swagger.io/specification/) and are documented at ["DOKUMENTATION & SUPPORT"](https://documentation.forschungsdaten.at/). They are based on [OpenAIRE Guidelines for CRIS Managers](https://openaire-guidelines-for-cris-managers.readthedocs.io/en/latest/) and extend them according to the metadata requirements defined within the project.


### Key Components


1. The API Endpoints


The following endpoints are available:


- Info Endpoint: Provides metadata about available endpoints and API versions.
- OrgUnit Endpoint: Provides organizational structures and relationships.
- Project Endpoint: Exposes data about research projects, including funding details and project descriptions.
- Funding Endpoint: Shares metadata for funding programs and calls.


The API endpoints follow the OpenAPI specifications.


2. Authentication


Keycloak handles authentication using the OAuth2 Client Credentials Flow. It issues tokens for authorized clients to ensure secure access to all endpoints.


3. Integrations


The project includes automation workflows and integrations, as seen in the scripts and DAGs directories:


- Apache Airflow DAGs manage automated workflows for metadata processing and exchange.
- DSpace Integration: The scripts enable synchronization and ingestion of metadata from DSpace CRIS repositories.


These integrations streamline data exchange and align research outputs across systems.


4. SBOM (Software Bill of Materials)


[GitHub’s Dependency Graph](https://github.com/mdwRepository/ris-synergy-api/dependency-graph/sbom)provides the Software Bill of Materials for transparency and security. 


### Code Quality and Security


The repository implements tools to ensure robust, secure, and high-quality code:


- Pylint: Enforces Python coding standards and identifies code smells.
- Bandit: Scans for security vulnerabilities in Python code.
- Dependabot: Keeps dependencies up to date and addresses vulnerabilities.


The collaborators regularly test the repository with Snyk for security.


## Getting Started


1. Prerequisites


- Python 3.9+
- Keycloak setup for OAuth2 authentication
- Apache Airflow (optional for DAGs)


2. Installation


Clone the repository:


```
git clone https://github.com/mdwRepository/ris-synergy-api.git
cd ris-synergy-api
```


Install dependencies:


```
pip install -r requirements.txt
```


Add environment variables (e.g., via .env file).


Run the server (example for local development):


```
python wsgi.py
```

