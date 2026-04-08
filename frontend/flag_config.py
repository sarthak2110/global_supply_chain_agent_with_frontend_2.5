import time
import json
import logging
from collections.abc import Callable
from typing import Any
import os
import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import grpc
from google.auth.exceptions import DefaultCredentialsError
from openfeature import api
from openfeature.contrib.provider.flagd import FlagdProvider
from openfeature.contrib.provider.flagd.config import ResolverType

# Optional: Set logging level to INFO or WARNING to hide debug noise
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _add_x_goog_request_params_header(config_name: str) -> Callable[[Any, Any], Any]:
    """Creates a metadata plugin callback for x-goog-request-params."""
    logger.debug(f"Adding x-goog-request-params header with config_name: {config_name}")
    return lambda context, callback: callback(
        [("x-goog-request-params", f"name={config_name}")], None
    )


def flag_init_provider(provider_id: str, host: str = "saasconfig.googleapis.com") -> FlagdProvider:
    """Initializes a flagd provider configured for SaaS Runtime."""
    try:
        logger.debug(f"Setting up FlagdProvider with provider_id: {provider_id}, host: {host}")
        # 1. Fetch Application Default Credentials
        # credentials, _ = google.auth.default()
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        

        # 2. Setup gRPC composite channel credentials
        request = google.auth.transport.requests.Request()

        configservice_credentials = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(),
            grpc.metadata_call_credentials(
                google.auth.transport.grpc.AuthMetadataPlugin(credentials, request)  # type: ignore
            ),
            grpc.metadata_call_credentials(_add_x_goog_request_params_header(provider_id)),
        )

        logger.debug(f"Credentials loaded. Config ID: {provider_id}")

        # 3. Initialize Flagd Provider with IN_PROCESS resolution
        provider = FlagdProvider(
            resolver_type=ResolverType.IN_PROCESS,
            host=host,
            port=443,
            sync_metadata_disabled=True,
            provider_id=provider_id,
            channel_credentials=configservice_credentials,
        )
        api.set_provider(provider)
        return provider

    except DefaultCredentialsError as e:
        logger.error("Failed to setup OpenFeature credentials.")
        raise RuntimeError(
            "Missing GCP Credentials. Run: gcloud auth application-default login"
        ) from e



def get_saas_flag_value() -> bool:
    """
    Returns True if SAAS_FLAG is 'true' (case-insensitive).
    """
    PROJECT_ID = os.environ.get("PROJECT_ID", "saas-poc-env")
    UNIT_LOCATION = os.environ.get("UNIT_LOCATION", "europe-north1")
    UNIT_NAME = os.environ.get("UNIT_NAME", "super-mtric")
    target_flag_key = os.environ.get("FLAG_KEY", "enhanced-search")
    config_id = f"projects/{PROJECT_ID}/locations/{UNIT_LOCATION}/featureFlagsConfigs/{UNIT_NAME}"
    # Initialize the OpenFeature provider
    flag_init_provider(config_id)
    print("Connecting to GCP and syncing flag configuration...")
    time.sleep(3)  # Wait for 3 seconds
    print("Sync complete. Evaluating flag...")

    # Get the OpenFeature client
    client = api.get_client()

    
    try:
        evaluation_details = client.get_boolean_details(
            flag_key=target_flag_key, 
            default_value=False
        )
        
        details_dict = {
            "flag_key": evaluation_details.flag_key,
            "value": evaluation_details.value,
            "variant": evaluation_details.variant,
            "reason": evaluation_details.reason,
            "error_code": str(evaluation_details.error_code) if evaluation_details.error_code else None,
            "error_message": evaluation_details.error_message,
        }
        
        
        print("\n" + "="*60)
        print(f"SUCCESS: Full JSON evaluation details for '{target_flag_key}':")
        print(json.dumps(details_dict, indent=4))
        logger.debug(json.dumps(details_dict, indent=4))
        print("="*60 + "\n")
        print("Flag Value = ",details_dict.get('value',"Flag value not found"))
        return details_dict.get('value',"Flag value not found")
        
        
    except Exception as e:
        print(f"An error occurred while evaluating the flag: {e}")
        return e










if __name__ == "__main__":
    config_id = "projects/saas-poc-env/locations/europe-north1/featureFlagsConfigs/super-mtric"
    
    # 1. Initialize the OpenFeature provider
    flag_init_provider(config_id)

    # 2. WAIT FOR SYNC: Give Flagd time to download the rules from GCP
    print("Connecting to GCP and syncing flag configuration...")
    time.sleep(3)  # Wait for 3 seconds
    print("Sync complete. Evaluating flag...")

    # 3. Get the OpenFeature client
    client = api.get_client()

    target_flag_key = "enhanced-search"
    
    try:
        evaluation_details = client.get_boolean_details(
            flag_key=target_flag_key, 
            default_value=False
        )
        
        details_dict = {
            "flag_key": evaluation_details.flag_key,
            "value": evaluation_details.value,
            "variant": evaluation_details.variant,
            "reason": evaluation_details.reason,
            "error_code": str(evaluation_details.error_code) if evaluation_details.error_code else None,
            "error_message": evaluation_details.error_message,
        }
        
        import json
        print("\n" + "="*60)
        print(f"SUCCESS: Full JSON evaluation details for '{target_flag_key}':")
        print(json.dumps(details_dict, indent=4))
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"An error occurred while evaluating the flag: {e}")