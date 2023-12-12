export GCP_PROJECT_ID='ml-demo-384110'  # Change this
export GCP_REGION='europe-west1'             # If you change this, make sure region is supported by Model Garden. 
export DATA_STORE_ID="bq-gsoi-articles-rugby-deb_1701080507649"
export DATA_STORE_LOCATION_ID="global"

export LLM_CHAT_MODEL_VERSION="chat-bison"
export LLM_TEXT_MODEL_VERSION="text-bison@002"

export AR_REPO='demo-repo'  # Change this

#gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
#gcloud auth configure-docker "$GCP_REGION-docker.pkg.dev"


echo ************* build backend *****************

cd backend
export SERVICE_NAME='chat-demo-backend-demo' # backend name
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$AR_REPO/$SERVICE_NAME"


gcloud run deploy "$SERVICE_NAME" \
    --port=8080 \
    --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$AR_REPO/$SERVICE_NAME" \
    --allow-unauthenticated \
    --region=$GCP_REGION \
    --platform=managed  \
    --project=$GCP_PROJECT_ID \
    --set-env-vars=GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$GCP_REGION,DATA_STORE_ID=$DATA_STORE_ID,DATA_STORE_LOCATION_ID=$DATA_STORE_LOCATION_ID,LLM_CHAT_MODEL_VERSION=$LLM_CHAT_MODEL_VERSION,LLM_TEXT_MODEL_VERSION=$LLM_TEXT_MODEL_VERSION
    
cd ..