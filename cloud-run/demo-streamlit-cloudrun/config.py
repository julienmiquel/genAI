



import os



PROJECT_ID = os.environ.get("GCP_PROJECT", "ml-demo-384110")  # Your Google Cloud Project ID
LOCATION = os.environ.get("GCP_REGION", "us-central1")  # Your Google Cloud Project Region

REGION = LOCATION

STT_REGION = "eu"
DATA_STORE_ID = "datastore"

BUCKET = "ml-demo-eu" #os.environ.get("GCP_BUCKET", "ml-demo-eu")  # Your GCS bucket name