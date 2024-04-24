# Imports
# Env var
import os
from ast import literal_eval
from dotenv import load_dotenv, find_dotenv

# Env variables
_ = load_dotenv(find_dotenv())

# GCP
PROJECT_ID = os.environ['PROJECT_ID']
REGION = os.environ['REGION']

# GCP datastore
DATA_STORE_ID = os.environ['DATA_STORE_ID']
DATA_STORE_LOCATION_ID = os.environ['DATA_STORE_LOCATION_ID']
DATA_STORE_MAX_DOC = os.environ['DATA_STORE_MAX_DOC']


# LLM Streaming default
STREAMING_MODE = False
