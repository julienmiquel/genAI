export GCP_PROJECT='ml-demo-384110'  # Change this
export GCP_REGION='us-central1'             # If you change this, make sure region is supported by Model Garden. When in 


export AR_REPO='julia-repo'  # Change this
export SERVICE_NAME='chat-streamlit-app' # This is the name of our Application and Cloud Run service. Change it if you'd like. 
gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
gcloud auth configure-docker "$GCP_REGION-docker.pkg.dev"
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"

gcloud run deploy "$SERVICE_NAME" \
    --port=8080 \
    --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
    --allow-unauthenticated \
    --region=$GCP_REGION \
    --platform=managed  \
    --project=$GCP_PROJECT \
    --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION
