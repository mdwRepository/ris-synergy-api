"""
DSpace OrgUnit Data Extraction and Processing Script
====================================================

This script connects to a DSpace REST API to query and process organizational unit (OrgUnit) data. 
The extracted data is processed into a JSON format suitable for further use in organizational charts 
or data pipelines.

Modules Used:
-------------
- `os`: Access environment variables and file paths.
- `json`: Serialize and deserialize JSON data.
- `logging`: Provide logging capabilities for debugging and error reporting.
- `re`: Regular expressions for string parsing.
- `sys`: Exit the program on critical errors.
- `dotenv.load_dotenv`: Load environment variables from a `.env` file.
- `dspace_rest_client.DSpaceClient`: Interface with the DSpace REST API.

Environment Variables:
----------------------
- `DSPACE_API_ENDPOINT`: Base URL for the DSpace API.
- `DSPACE_API_USERNAME`: Username for API authentication.
- `DSPACE_API_PASSWORD`: Password for API authentication.
- `DSPACE_REST_API_URL`: URL for the DSpace REST API.
- `SOLR_ENDPOINT`: URL for the SOLR search endpoint.

Key Components:
---------------
1. **Environment Variable Loading**:
   - Load and validate API credentials from a `.env` file.
   - Terminate if mandatory variables are not set.

2. **Address Parsing**:
   - Extract address components such as `addrline1`, `postCode`, and `cityTown` using regex.

3. **DSpace Client Initialization**:
   - Create a `DSpaceClient` instance for querying SOLR.

4. **Query Parameters**:
   - Construct SOLR query filters, sort order, and fields to retrieve data.

5. **Data Processing**:
   - Parse SOLR query results.
   - Generate a structured JSON object with fields like `id`, `name`, `type`, `acronym`, and `address`.

6. **Output**:
   - Save the processed data into a JSON file named with the format: `organigramm_YYYY-MM-DD.json`.

Functions:
----------
- `parse_address(address)`: Parse a string or list representing an address to extract structured components.

Usage:
------
1. Set up a `.env` file with required environment variables.
2. Run the script to query the DSpace API and generate a JSON file with processed data.

Logging Levels:
---------------
- `INFO`: Connection details and process flow.
- `ERROR`: Missing environment variables or critical issues.
- `DEBUG`: Output JSON structure for validation.

Dependencies:
-------------
Ensure the following Python packages are installed:
- `python-dotenv`
- `dspace-rest-client`

Author:
-------
Stefan Szepe, University of MUsic and Performing Arts Vienna (szepe@mdw.ac.at)

"""

import os
import json
import logging
import re
import sys

from dotenv import load_dotenv
from dspace_rest_client.client import DSpaceClient

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv(override=True)

url = os.getenv("DSPACE_API_ENDPOINT")
username = os.getenv("DSPACE_API_USERNAME")
password = os.getenv("DSPACE_API_PASSWORD")

if not url or not username or not password:
    logging.error(
        "Error: DSPACE_API_ENDPOINT, DSPACE_API_USERNAME, or DSPACE_API_PASSWORD not set in .env file"
    )
    sys.exit(1)
else:
    logging.info(f"Connecting to DSpace API at {url} as {username}")


# Function to process address
def parse_address(address):
    """
    Parses a full address string or list and extracts addrline1, postCode, and cityTown.
    Assumes address format: "Street Address, PostCode City".
    """
    # Handle list input
    if isinstance(address, list):
        address = address[0] if address else ""

    # Ensure it's a string
    if not isinstance(address, str):
        return {"addrline1": [], "postCode": [], "cityTown": []}

    # Regular expression to extract parts of the address
    match = re.match(r"(.+),\s*(\d+)\s*(.+)", address)
    if match:
        addrline1, post_code, city_town = match.groups()
        return {
            "addrline1": [addrline1],
            "postCode": [post_code],
            "cityTown": [city_town],
        }
    else:
        # If address format is unrecognized, return the full address in addrline1
        return {"addrline1": [address], "postCode": [], "cityTown": []}


# Initialize the DSpace client
d = DSpaceClient(
    api_endpoint=os.getenv("DSPACE_REST_API_URL"),
    unauthenticated=True,
    fake_user_agent=True,
    solr_endpoint=os.getenv("SOLR_ENDPOINT") + "/search",
    solr_auth=None,
)

# Query and sort parameters
solr_query = "entityType:OrgUnit AND organization.identifier.mdwonline:[* TO *]"
sort_order = "asc"  # Change to "desc" if needed
solr_sort = f"dc.title_sort {sort_order}"
rows = 200
start = 0  # Start position for querying

# Perform the query
solr_search_results = d.solr_query(
    query=solr_query,
    filters=[],
    fields=[
        "search.resourceid",
        "dc.title",
        "crisou.acronym",
        "dc.title.alternative",
        "mdwrepo.orgunit.hasTopOrgUnit",
        "mdwrepo.orgunit.hasTopOrgUnit_authority",
        "organization.address.addressCountry",
        "organization.address.addressLocality",
        "organization.parentOrganization",
        "organization.parentOrganization_authority",
        "mdwonline.validFrom",
        "risorgunit.level",
        "risorgunit.type",
    ],
    facets=[],
    minfacests=0,
    start=start,
    rows=rows,
    sort=solr_sort,
)

# Process the search results
solr_docs = solr_search_results.docs
output = []

for doc in solr_docs:
    valid_from = doc.get("mdwonline.validFrom", "")  # Get the value of validFrom
    # Check if valid_from is not None and not empty
    if isinstance(valid_from, list):
        valid_from = valid_from[0] if valid_from else ""
    start_date = f"{valid_from}T22:00:00.000+00:00" if valid_from else None
    # Parse the address
    full_address = doc.get("organization.address.addressLocality", "")
    parsed_address = parse_address(full_address)
    # Construct the JSON object
    json_obj = {
        "id": doc.get("search.resourceid"),
        "name": [
            {"lang": "de", "trans": "O", "text": doc.get("dc.title", "")},
            {"lang": "en", "trans": "H", "text": doc.get("dc.title.alternative", "")},
        ],
        "type": doc.get("risorgunit.type", ""),
        "acronym": doc.get("crisou.acronym", ""),
        "electronicAddress": [],
        "identifiers": [],
        "address": {
            "countryCode": doc.get("organization.address.addressCountry", ""),
            **parsed_address,  # Merge parsed address parts
            "stateOfCountry": "Austria",
        },
        "level": doc.get("risorgunit.level", ""),
        "partOf": doc.get("organization.parentOrganization_authority", ""),
        "startDate": start_date,  # Use the validated start_date
    }
    output.append(json_obj)

# Output the results as JSON file with name "organigramm_YYYY-MM-DD.json"
logging.debug(json.dumps(output, indent=4, ensure_ascii=False))
output_file_name = f"organigramm_{start_date[:10]}.json"
with open(output_file_name, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)