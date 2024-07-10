



import os



PROJECT_ID = os.environ.get("GCP_PROJECT", "ml-demo-384110")  # Your Google Cloud Project ID
LOCATION = os.environ.get("GCP_REGION", "us-central1")  # Your Google Cloud Project Region

REGION = LOCATION

STT_REGION = "eu"
DATA_STORE_ID = "datastore"
NAME = "jm"

BUCKET = "ml-demo-eu" #os.environ.get("GCP_BUCKET", "ml-demo-eu")  # Your GCS bucket name

GEMINI_MULTIMODAL_MODEL_NAME = "gemini-1.5-flash-001"  # @param {type:"string"}

BQ_REGION  = os.environ.get("REGION", "eu")
