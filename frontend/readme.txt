gcloud services enable iamcredentials.googleapis.com --project saas-poc-env


gsutil iam ch \
  "serviceAccount:infra-manager-sa@saas-poc-env.iam.gserviceaccount.com:objectViewer" \
  gs://sarthak-test


gcloud auth application-default login \
  --impersonate-service-account="infra-manager-sa@saas-poc-env.iam.gserviceaccount.com"

export GCS_BUCKET="sarthak-test"
export GCS_OBJECT="maps/route_map.html"
export SIGNED_URL_TTL_MIN="30"


chainlit run  gem3-5.py -w --port 8501

cd google-next-26/frontend
source .venv/bin/activate
chainlit run app.py -w --port 8501
chainlit run app2-test.py -w --port 8501

chainlit run app.py -w
or
chainlit run app.py -w --port 8501


deployment:

cloud run:
export _REGION="us-central1"
export _PREFIX="globalsupply-chain-frontend-flag"
export _projectID="saas-poc-env"
export _version="v2.05.0"

gcloud artifacts repositories create ${_PREFIX} --repository-format=docker --location=$_REGION --project=${_projectID}
docker build  --tag ${_REGION}-docker.pkg.dev/${_projectID}/${_PREFIX}/${_version}:latest .
docker push ${_REGION}-docker.pkg.dev/${_projectID}/${_PREFIX}/${_version}:latest

variables:
AGENT_ENGINE_QUERY_URL=https://us-central1-aiplatform.googleapis.com/v1/projects/736134210043/locations/us-central1/reasoningEngines/8954972452421632:query
AGENT_ENGINE_STREAM_URL=https://us-central1-aiplatform.googleapis.com/v1/projects/736134210043/locations/us-central1/reasoningEngines/8954972452421632:streamQuery?alt=sse
GCS_BUCKET=sarthak-test
GCS_OBJECT=maps/route_map.html
SIGNED_URL_TTL_MIN=30
SAAS_FLAG=true



Permissions on Agent engine SA:
BigQuery Admin
Developer Connect Read Token Accessor (Beta)
Developer Connect Read Token Accessor (Beta)
Model Armor Admin
Storage Admin
Vertex AI Reasoning Engine Service Agent
Vertex AI Reasoning Engine Service Agent
Vertex AI User
Vertex AI User





TESTING PROMPTS:

1) do inventory analysis on `saas-poc-env.mcp.inventory_data` and tell me Which products are running low on stock?
2) Show me the top-selling products at US-WEST-2 location `saas-poc-env.mcp.inventory_data`
3) Give me a logistics health check on our inbound freight from Bangalore.
4) We have a critical shipment of raw materials leaving from Mumbai today. Can you check the route status and ensure it gets to our receiving facility?
5) There's a massive localized strike in Chennai disrupting our usual freight lines. We need to reroute our electronics shipment immediately via an expedited emergency carrier, but the quotes I'm seeing are around $14,500. Handle this.
6) Primary supplier for SKU STEEL-A36 is unable to fulfill. Need 300 units delivered to Hyderabad within 10 days. Please evaluate backups using available quotes, recommend the best option, and draft a PO.
