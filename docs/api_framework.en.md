# RIS Synergy API framework


The RIS Synergy API framework facilitates seamless data exchange among Austrian research institutions, funding agencies, and public administration. Its architecture encompasses several key components:


## Network Architecture


The RIS Synergy network operates on a decentralized model, connecting universities, funding bodies, and a centrally managed instance called "RIS Apps." Each participant maintains its own systems and coordinates data through a central registry. This registry contains entries for all network members detailing their authentication and information endpoints. The current registry is accessible at [registry.json](https://forschungsdaten.at/registry/registry.json).


## Registry


The central registry is a curated resource listing all RIS Synergy network participants. Each entry includes:


- id: A unique identifier for the institution or organization.
- acronym: An abbreviation representing the institution.
- name: The full name of the institution.
- contact: An email address for inquiries related to the institution.
- oauth2: The URL endpoint for OAuth2 authorization requests.
- info: The URL endpoint to the institution's local information resource.


This structured approach ensures efficient discovery and interaction among network members.


## APIs


RIS Synergy offers several APIs to facilitate data exchange:


- Info Endpoint: Provides metadata about available systems, including a list of resource endpoints and their versions.
   
- OrgUnit Endpoint: Allows retrieval of organizational structures, such as organigrams, from research institutions.


- Funding Endpoint: Enables access to metadata regarding current funding programs and calls for research project financing.
 
- Project Endpoint: Facilitates the exchange of application and project data, providing metadata on proposals and externally funded projects.


## Authentication


Security within the RIS Synergy network is managed through OAuth2, specifically employing the Client Credentials Flow. Each node is required to operate an OAuth2 server that is responsible for issuing access tokens. The authentication process involves:


- The client sends an authentication request to the OAuth2 token endpoint using client credentials.
- Upon successful validation, the OAuth2 server issues an access token to the client.
- The client uses this access token to access the desired API on the resource server.


Client credentials (Client ID and Client Secret) must be exchanged bilaterally between network members to ensure secure data transmission.


## OpenAIRE Guidelines for CRIS Managers


The RIS Synergy APIs are built upon the OpenAIRE Guidelines for CRIS Managers, specifically leveraging version 1.2.0. These guidelines provide a standard for exchanging metadata about research information, ensuring interoperability across systems like CRIS (Current Research Information Systems). The RIS Synergy APIs adopt these principles to facilitate seamless data sharing within the Austrian research ecosystem.


### Introduction to OpenAIRE Guidelines


The OpenAIRE Guidelines for CRIS Managers are designed to standardize research information system outputs, enabling integration into the wider European Open Science landscape. OpenAIRE focuses on metadata interoperability by aligning with the CERIF (Common European Research Information Format) data model. These guidelines ensure that CRIS systems can expose metadata for various entities—projects, organizational units, outputs, funding, and more—using standardized endpoints.


The guidelines facilitate the creation of FAIR-compliant (Findable, Accessible, Interoperable, and Reusable) research data by defining data models, formats, and protocols. This supports open science goals by enabling machine-readable and standardized metadata across platforms.


### CERIF and FAIR Impact


The CERIF model, developed by euroCRIS, underpins the OpenAIRE guidelines by offering a structured and semantic representation of research information. CERIF models data through entities (like projects, funding, publications, and organizations) and the relationships between them. By using CERIF as a foundation, the OpenAIRE guidelines ensure that research information adheres to FAIR principles:


- Findable: Data is enriched with unique identifiers and standardized metadata.
- Accessible: Open endpoints and APIs allow consistent access.
- Interoperable: Data is exposed in machine-readable, CERIF-compatible formats.
- Reusable: Standardized structures allow data to be reused across platforms.


### OpenAPI vs OAI-PMH


OpenAPI: OpenAPI is a modern, REST-based standard for creating, documenting, and consuming web APIs. It supports real-time access to structured JSON data.


*Advantages*: Lightweight, developer-friendly, supports diverse clients (web, mobile), and provides real-time data access.
    Use in RIS Synergy: RIS endpoints (Info, OrgUnit, Funding, etc.) utilize RESTful OpenAPI for efficient metadata exchange.


OAI-PMH (Open Archives Initiative Protocol for Metadata Harvesting): OAI-PMH is an older protocol for batch harvesting metadata in XML format. It works well for static repositories but lacks the flexibility provided by REST APIs.


*Advantages*: Simple, ideal for batch metadata harvesting.
*Limitations*: Limited support for complex queries, less interactive.


[OpenAIRE PROVIDE](https://provide.openaire.eu/home)uses OAI-PMH for data harvesting.


**Key Differences and Authentication**


1. Data Exchange Protocols


    OpenAPI:
        A REST-based standard that provides real-time access to structured data in JSON format.
        Supports fine-grained queries and modern API tools (e.g., Swagger).
        Ideal for scalable, interactive applications like RIS Synergy APIs.


    OAI-PMH:
        A legacy protocol for batch harvesting of metadata in XML format.
        Lacks the flexibility of real-time interaction.


2. Authentication


    OpenAPI:
        Utilizes OAuth2 authentication for secure access.
        In RIS Synergy, clients authenticate via the Client Credentials Flow to retrieve an access token.
        Tokens provide secure, authorized access to endpoints while allowing fine control over permissions.


    OAI-PMH:
        Generally, it does not support robust authentication methods like OAuth2.
        Access is often open or, at best, relies on basic authentication, making it less suitable for secure, modern systems.


3. Use in RIS Synergy


    RIS Synergy APIs favor OpenAPI because of its modern features:
        - Real-time, dynamic data access.
        - Enhanced security with OAuth2, which enables the exchange of sensitive non-public data.
    Publication data is still provided via the OAI-PMH endpoint.


For more information, see [RIS Synergy Dokumentation & Support](https://documentation.forschungsdaten.at/)

