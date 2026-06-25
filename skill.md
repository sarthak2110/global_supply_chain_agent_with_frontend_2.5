## Overview
name: deploy-antigravity-agent description: > Use this skill to deploy the hello-world-agent. It handles git code pushes and provisions Google Cloud SaaS runtime units and operations.
## Deploy Antigravity Agent
### When to use
Trigger this skill when a user requests to deploy an agent, push code, or provision SaaS runtime infrastructure.
### Required Parameters
If these are missing, prompt the user for them before executing:
* PROJECT_ID: The target Google Cloud Project ID.
* TENANT_NAME: The SaaS tenant identifier.
* SAAS_OFFERING_ID: The ID of the SaaS offering to create and use.
* LOCATION: The region for the deployment (e.g., `us-central1`).
* SPACE_NAME: The workspace for the application template (e.g., `default-space`).
* TEMPLATE_NAME: The application template name (e.g., `antigravity`).
* UNIT_NAME: The base name for the unit.
* UNIT_OPERATIONS: The base name for the operations.
* COUNT: The 2-digit index (e.g., `01`).
### Guardrails
* Stop if any command returns a non-zero exit code.
* Do not proceed with Unit Operation creation if the Unit creation fails.
* Verify input variables are correctly formatted as a JSON string before running gcloud.
## Execution Workflow
### 1. Push Code

cd global_supply_chain_agent
git add .
git commit -m "Auto-deploying agent via Antigravity skill"
git push
cd ..
### 2. Create SaaS Offering

Create the SaaS offering using the application template before retrieving metadata.

gcloud beta app-lifecycle-manager saas create "${SAAS_OFFERING_ID}" \
    --project="${PROJECT_ID}" \
    --location="${LOCATION}" \
    --locations=name="${LOCATION}" \
    --application-template="projects/${PROJECT_ID}/locations/${LOCATION}/spaces/${SPACE_NAME}/applicationTemplates/${TEMPLATE_NAME}"
### 3. Retrieve Unit Kind and Release Metadata
Run the following commands to get the required `UNIT_KIND` and `RELEASE_PATH` necessary for provisioning in the subsequent steps.


# Get the Unit Kind
gcloud beta app-lifecycle-manager unit-kinds list \
    --project="${PROJECT_ID}" \
    --location="${LOCATION}" \
    --saas="${SAAS_OFFERING_ID}"

# Get the Release path
gcloud beta app-lifecycle-manager releases list \
    --project="${PROJECT_ID}" \
    --location="${LOCATION}" \
    --saas="${SAAS_OFFERING_ID}"
### 4. Provision Unit
Note: Ensure the `UNIT_KIND` parameter uses the output retrieved from Step 3.


# Define parameters
UNIT_FULL_NAME="${UNIT_NAME}${COUNT}"
# Provide the unit kind from the list command above
FETCHED_UNIT_KIND="<INSERT_UNIT_KIND_FROM_STEP_3>"

gcloud alpha saas-runtime units create "${UNIT_FULL_NAME}" \
    --location="${LOCATION}" \
    --tenant="${TENANT_NAME}" \
    --unit-kind="${FETCHED_UNIT_KIND}"
### 5. Provision Operation
Note: Ensure the `RELEASE_PATH` uses the correct release output retrieved from Step 3.


# Define parameters
OPERATION_NAME="${UNIT_OPERATIONS}${COUNT}-uo-01"
UNIT_FULL_NAME="${UNIT_NAME}${COUNT}"
# Provide the release path from the list command above
RELEASE_PATH="projects/${PROJECT_ID}/locations/${LOCATION}/releases/<INSERT_RELEASE_ID_FROM_STEP_3>"

gcloud alpha saas-runtime unit-operations create "${OPERATION_NAME}" \
    --location="${LOCATION}" \
    --unit="projects/${PROJECT_ID}/locations/${LOCATION}/units/${UNIT_FULL_NAME}" \
    --provision-release="${RELEASE_PATH}" \
    --provision-input-variables='[
        {"variable": "agent-engine-1_display_name", "value": "gtm-hts-agent-avathon-'"${COUNT}"'", "type": "string"},
        {"variable": "cloud-run-1_service_name", "value": "gtm-hts-frontend-avathon-'"${COUNT}"'", "type": "string"},
        {"variable": "tenant_project_id", "value": "avathon-app-core-sandbox", "type": "string"},
        {"variable": "lb-frontend-1_name", "value": "gtm-hts-agent-frontend-'"${COUNT}"'", "type": "string"},
        {"variable": "lb-backend-1_name", "value": "gtm-hts-agent-backend-'"${COUNT}"'", "type": "string"},
        {"variable": "tenant_project_number", "value": 680769728237, "type": "string"},
        {"variable": "actuation_sa", "value": "gtm-demo-app-us-c1@avathon-app-core-sandbox.iam.gserviceaccount.com", "type": "string"}
    ]'
### 6. Post-Deployment Verification


gcloud alpha saas-runtime units describe "${UNIT_NAME}${COUNT}" --location="${LOCATION}"
## Completion

Summarize the actions:
* Confirm Git push status.
* Report the SaaS offering creation.
* Report the Unit name created.
* Report the Operation name created.
* Provide the result of the verification command.


