from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import json
import logging
import os
from dspace_rest_client.client import DSpaceClient

# Please note:
# This DAG requires this dspace-rest-client fork to be installed:
# https://github.com/sszepe/dspace-rest-python

# Define default arguments
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 10, 1),
    "retries": 1,
}


# Define a function to process and generate the organigram JSON
def generate_organigram():
    # Fetch Airflow variables
    organigram_folder = Variable.get("organigram_results_folder", default_var="/tmp")
    dspace_api = Variable.get("dspace_api")
    dspace_solr = Variable.get("dspace_solr")

    # Initialize the DSpace client
    d = DSpaceClient(
        api_endpoint=dspace_api,
        unauthenticated=True,
        fake_user_agent=True,
        solr_endpoint=dspace_solr + "/search",
        solr_auth=None,
    )

    # Solr query and sort parameters
    solr_query = "entityType:OrgUnit AND organization.identifier.mdwonline:[* TO *]"
    solr_sort = "dc.title_sort asc"
    rows = 200
    start = 0

    # Perform the query
    solr_search_results = d.solr_query(
        query=solr_query,
        filters=[],
        fields=[
            "search.resourceid",
            "dc.title",
            "dc.title.de",
            "dc.title.en",
            "crisou.acronym",
            "dc.title.alternative",
            "dc.title.alternative.en",
            "dc.title.alternative.de",
            "dc.title.alternative.fr",
            "dc.title.alternative.sl",
            "mdwrepo.orgunit.hasTopOrgUnit",
            "mdwrepo.orgunit.hasTopOrgUnit_authority",
            "organization.address.addressCountry",
            "organization.address.addressLocality",
            "risorgunit.postAddress.addrline1",
            "risorgunit.postAddress.postCode",
            "risorgunit.electronicAddress.telephone",
            "risorgunit.electronicAddress.fax",
            "risorgunit.electronicAddress.email",
            "oairecerif.identifier.url",
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

    top_unit_id = "37ddc68f-9cd7-4b80-b6dc-1d15a65eb34b"

    def calculate_levels(docs, top_unit_id):
        levels = {}
        children_map = {}

        for doc in docs:
            doc_id = doc.get("search.resourceid")
            parent_ids = doc.get("organization.parentOrganization_authority", [])

            if not doc_id:
                logging.warning(f"Document missing ID: {doc}")
                continue

            if isinstance(parent_ids, list):
                for parent_id in parent_ids:
                    if parent_id:
                        children_map.setdefault(parent_id, []).append(doc_id)
            elif parent_ids:
                children_map.setdefault(parent_ids, []).append(doc_id)

        levels[top_unit_id] = 1

        def assign_levels(parent_id, current_level):
            children = children_map.get(parent_id, [])
            for child_id in children:
                if child_id in levels:
                    continue
                levels[child_id] = current_level + 1
                assign_levels(child_id, current_level + 1)

        assign_levels(top_unit_id, 1)
        return levels

    level_mapping = calculate_levels(solr_docs, top_unit_id)

    for doc in solr_docs:
        valid_from = doc.get("mdwonline.validFrom", "")
        if isinstance(valid_from, list):
            valid_from = valid_from[0] if valid_from else ""
        start_date = f"{valid_from}T22:00:00.000+00:00" if valid_from else None

        json_obj = {
            "id": doc.get("search.resourceid"),
            "name": [{"trans": "O", "text": doc.get("dc.title", "")}],
            "type": doc.get("risorgunit.type", ""),
            "acronym": doc.get("crisou.acronym", ""),
            "identifiers": [],
            "address": {
                "countryCode": doc.get("organization.address.addressCountry", ""),
                "addrline1": doc.get("risorgunit.postAddress.addrline1", ""),
                "postCode": doc.get("risorgunit.postAddress.postCode", ""),
                "cityTown": doc.get("organization.address.addressLocality", ""),
                "stateOfCountry": "Austria",
            },
            "electronicAddress": [],
            "website": doc.get("oairecerif.identifier.url", ""),
            "level": "LEVEL_"
            + str(level_mapping.get(doc.get("search.resourceid"), "")),
            "partOf": doc.get("organization.parentOrganization_authority", ""),
            "startDate": start_date,
        }
        output.append(json_obj)

    today = datetime.now().isoformat()
    output_file_name = f"{organigram_folder}/organigramm_{today[:10]}.json"

    with open(output_file_name, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)


# Define the DAG
with DAG(
    "dspace_generate_organigram",
    default_args=default_args,
    description="A DAG to generate a daily organigram from DSpace CRIS.",
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 12, 6),
    catchup=False,
) as dag:

    start_task = DummyOperator(task_id="start_task")

    generate_organigram_task = PythonOperator(
        task_id="generate_organigram",
        python_callable=generate_organigram,
    )

    end_task = DummyOperator(task_id="end_task")

    start_task >> generate_organigram_task >> end_task
