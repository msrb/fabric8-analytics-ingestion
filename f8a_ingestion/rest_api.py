# Copyright © 2018 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Geetika Batra <gbatra@redhat.com>
#

"""Class to define routes."""

import connexion
import flask
import defaults
from flask import Flask, request
from flask_cors import CORS


def readiness():
    """Readiness probe."""
    return flask.jsonify({}), 200


def liveness():
    """Liveness probe."""
    return flask.jsonify({}), 200


def ingest():
    """Liveness probe."""
    return flask.jsonify({}), 200

app = connexion.FlaskApp(__name__)

app.add_api(defaults.SWAGGER_YAML_PATH)

if __name__ == "__main__":
    app.run()
