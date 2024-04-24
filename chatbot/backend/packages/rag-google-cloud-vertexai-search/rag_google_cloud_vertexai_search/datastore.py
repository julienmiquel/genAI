import os
from google.cloud import discoveryengine_v1alpha as discoveryengine


# Get project, data store, and model type from env variables
PROJECT_ID  = os.environ.get("GCP_PROJECT_ID")
REGION      =  os.environ.get("GCP_REGION")

DATA_STORE_ID           = os.environ.get("DATA_STORE_ID")
DATA_STORE_LOCATION_ID  =  os.environ.get("DATA_STORE_LOCATION_ID")
DATA_STORE_MAX_DOC = os.environ.get("DATA_STORE_MAX_DOC", 3)
DATA_STORE_DOCS_GCS = os.environ.get("DATA_STORE_DOCS_GCS", "gs://rag-vertex-1/datastore/*.json")


# Initialize Vertex AI
import vertexai

vertexai.init(project=PROJECT_ID, location=REGION)



def create_data_store(
    project_id: str, location: str, data_store_name: str, data_store_id: str
):
    # Create a client
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)

    # Initialize request argument(s)
    data_store = discoveryengine.DataStore(
        display_name=data_store_name,
        industry_vertical="GENERIC",
        content_config="CONTENT_REQUIRED",
    )

    request = discoveryengine.CreateDataStoreRequest(
        parent=discoveryengine.DataStoreServiceClient.collection_path(
            project_id, location, "default_collection"
        ),
        data_store=data_store,
        data_store_id=data_store_id,
        
    )
    operation = client.create_data_store(request=request)

    # Make the request
    # The try block is necessary to prevent execution from haulting due to an error being thrown when the datastore takes a while to instantiate
    try:
        response = operation.result(timeout=90)
    except:
        print("long-running operation")


from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine

# TODO(developer): Uncomment these variables before running the sample.
# project_id = "YOUR_PROJECT_ID"
# location = "YOUR_LOCATION" # Values: "global"
# data_store_id = "YOUR_DATA_STORE_ID"

# Must specify either `gcs_uri` or (`bigquery_dataset` and `bigquery_table`)
# Format: `gs://bucket/directory/object.json` or `gs://bucket/directory/*.json`
# gcs_uri = "YOUR_GCS_PATH"
# bigquery_dataset = "YOUR_BIGQUERY_DATASET"
# bigquery_table = "YOUR_BIGQUERY_TABLE"


def import_documents_sample(
    project_id: str,
    location: str,
    data_store_id: str,
    gcs_uri: Optional[str] = None,
    bigquery_dataset: Optional[str] = None,
    bigquery_table: Optional[str] = None,
) -> str:
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    # The full resource name of the search engine branch.
    # e.g. projects/{project}/locations/{location}/dataStores/{data_store_id}/branches/{branch}
    parent = client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    )

    if gcs_uri:
        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            gcs_source=discoveryengine.GcsSource(
                input_uris=[gcs_uri], data_schema="custom",
                idField = "id",
                autoGenerateIds = False,
                gcs_timestamp_prefix=True,
            ),
            # Options: `FULL`, `INCREMENTAL`
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        )
    else:
        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            bigquery_source=discoveryengine.BigQuerySource(
                project_id=project_id,
                dataset_id=bigquery_dataset,
                table_id=bigquery_table,
                data_schema="custom",
            ),
            # Options: `FULL`, `INCREMENTAL`
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        )

    # Make the request
    print(request)
    operation = client.import_documents(request=request)

    print(f"Waiting for operation to complete: {operation.operation.name}")
    response = operation.result()

    # Once the operation is complete,
    # get information from operation metadata
    metadata = discoveryengine.ImportDocumentsMetadata(operation.metadata)

    # Handle the response
    print(response)
    print(metadata)

    return operation.operation.name



def delete_documents_sample(
    project_id: str,
    location: str,
    data_store_id: str,
    gcs_uri: Optional[str] = None,
    document_id: Optional[str] = None,
) -> str:
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    # The full resource name of the search engine branch.
    # e.g. projects/{project}/locations/{location}/dataStores/{data_store_id}/branches/{branch}
    parent = client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    )

    if gcs_uri:
        request = discoveryengine.DeleteDocumentRequest(
            parent=parent, name=document_id,
        )
    # else:
    #     request = discoveryengine.ImportDocumentsRequest(
    #         parent=parent,
    #         bigquery_source=discoveryengine.BigQuerySource(
    #             project_id=project_id,
    #             dataset_id=bigquery_dataset,
    #             table_id=bigquery_table,
    #             data_schema="custom",
    #         ),
    #         # Options: `FULL`, `INCREMENTAL`
    #         reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    #     )

    # Make the request
    print(request)
    operation = client.import_documents(request=request)

    print(f"Waiting for operation to complete: {operation.operation.name}")
    response = operation.result()

    # Once the operation is complete,
    # get information from operation metadata
    metadata = discoveryengine.ImportDocumentsMetadata(operation.metadata)

    # Handle the response
    print(response)
    print(metadata)

    return operation.operation.name


def refresh_data_store():
    import_documents_sample(
        project_id=PROJECT_ID,
        location=DATA_STORE_LOCATION_ID,
        data_store_id = DATA_STORE_ID,
        gcs_uri = DATA_STORE_DOCS_GCS)
