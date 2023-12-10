export GCP_PROJECT='ml-demo-384110'  # Change this
export GCP_REGION='europe-west1'             # If you change this, make sure region is supported by Model Garden. 


export AR_REPO='julia-repo'  # Change this

#gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
#gcloud auth configure-docker "$GCP_REGION-docker.pkg.dev"

echo ************* build backend *****************

cd backend
export SERVICE_NAME='chat-demo-backend2' # backend name
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"

echo ************* deploy backend *****************
gcloud run deploy "$SERVICE_NAME" \
    --port=8080 \
    --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
    --allow-unauthenticated \
    --region=$GCP_REGION \
    --platform=managed  \
    --project=$GCP_PROJECT \
    --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION

echo ************* backend good *****************

cd ..
exit

cd ../frontend
export SERVICE_NAME='chat-demo-front' # frontend app name
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"

gcloud run deploy "$SERVICE_NAME" \
    --port=8080 \
    --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
    --allow-unauthenticated \
    --region=$GCP_REGION \
    --platform=managed  \
    --project=$GCP_PROJECT \
    --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION
