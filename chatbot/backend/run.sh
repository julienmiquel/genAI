
export PROJECT_ID=rag-vertex
export REGION=europe-west1
export GCP_PROJECT_ID=$PROJECT_ID
export GCP_REGION=$REGION 

export DATA_STORE_ID=test-no-content-1-id



#bq-gsoi-articles-rugby-deb_1701080507649
export DATA_STORE_LOCATION_ID=eu
export DATA_STORE_MAX_DOC=10

export LLM_CHAT_MODEL_VERSION=chat-bison@002
export LLM_TEXT_MODEL_VERSION=text-bison@002

poetry run start