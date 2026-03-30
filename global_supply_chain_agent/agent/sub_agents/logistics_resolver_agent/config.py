import os
import logging

# GEMINI MODELS - https://ai.google.dev/gemini-api/docs/models

logger = logging.getLogger(__name__)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY",'')
MAPS_GCS_BUCKET = os.getenv("MAPS_GCS_BUCKET","sarthak-test")
MAPS_GCS_FOLDER = "maps"
