#!/usr/bin/bash

# Start API backbone service with time out
gunicorn --pythonpath f8a_ingestion/ -b 0.0.0.0:$INGESTION_API_SERVICE_PORT -t $INGESTION_API_SERVICE_TIMEOUT rest_api:app
