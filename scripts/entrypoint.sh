#!/bin/bash

set -e

DEFAULT_GUNICORN_ARGS="--worker-class sync --workers 4"

if [ -z "$GUNICORN_ARGS" ]; then
    echo "Using default gunicorn args: ${DEFAULT_GUNICORN_ARGS}"
    GUNICORN_ARGS=${DEFAULT_GUNICORN_ARGS}
fi

set -x
# Start API ingestion service
gunicorn --pythonpath /f8a_ingestion/ \
         --bind 0.0.0.0:${APP_PORT:-5000} \
         ${GUNICORN_ARGS} \
         rest_api:app
