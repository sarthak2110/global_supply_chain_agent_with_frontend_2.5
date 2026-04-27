Frontend 

cd frontend

deployment commands for cloud run:

export _REGION="us-central1"
export _PREFIX=""
export _projectID=""
export _version="v1.00.0"

gcloud artifacts repositories create ${_PREFIX} --repository-format=docker --location=$_REGION --project=${_projectID}
docker build  --tag ${_REGION}-docker.pkg.dev/${_projectID}/${_PREFIX}/${_version}:latest .
docker push ${_REGION}-docker.pkg.dev/${_projectID}/${_PREFIX}/${_version}:latest


variables:
AGENTENGINE_ENGINE_ID='<Agent engine ID>'
AGENTENGINE_LOCATION='<Agent engine location>'
AGENTENGINE_PROJECT_ID='<Agent engine project id>'
GCS_BUCKET='<bucket name>'

