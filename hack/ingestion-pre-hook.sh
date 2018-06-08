#!/usr/bin/bash
# This script is run as a pre-hook only once per deployment

set -e

alembic upgrade head
