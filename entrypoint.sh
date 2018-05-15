#!/usr/bin/bash

# Start API backbone service with time out
gunicorn --pythonpath /src/ -b 0.0.0.0:$INGESTION_API_PORT -t $INGESTION_API_SERVICE_TIMEOUT -k $CLASS_TYPE -w $NUMBER_WORKER_PROCESS rest_api:app
