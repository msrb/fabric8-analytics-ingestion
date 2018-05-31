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
from f8a_ingestion import defaults
from flask import request
from f8a_ingestion.utils import DatabaseIngestion, validate_request_data, map_enum_backend
from f8a_ingestion.enums import EcosystemBackend


def readiness():
    """Readiness probe."""
    return flask.jsonify({}), 200


def liveness():
    """Liveness probe."""
    return flask.jsonify({}), 200


def ingest():
    """Ingest Data."""
    """
    Endpoint to ingest Ecosystem data.
    Registers new information and
    updates existing Ecosystem information.
    """
    resp_dict = {
        "success": True,
        "summary": ""
    }
    input_json = request.get_json()
    if request.content_type != 'application/json':
        resp_dict["success"] = False
        resp_dict["summary"] = "Set content type to application/json"
        return flask.jsonify(resp_dict), 400

    validated_data = validate_request_data(input_json)
    if not validated_data[0]:
        resp_dict["success"] = False
        resp_dict["summary"] = validated_data[1]
        return flask.jsonify(resp_dict), 404

    try:
        ecosystem_info = DatabaseIngestion.get_info(input_json.get('ecosystem'))
        if ecosystem_info.get('is_valid'):
            DatabaseIngestion.update_data(input_json)
        else:
            try:
                # First time ingestion
                input_json["backend"] = map_enum_backend(input_json.get("backend", None))
                DatabaseIngestion.store_record(input_json)
            except Exception as e:
                resp_dict["success"] = False
                resp_dict["summary"] = "Database Ingestion Failure due to: {}" \
                    .format(e)
                return flask.jsonify(resp_dict), 500
    except Exception as e:
        resp_dict["success"] = False
        resp_dict["summary"] = "Cannot get information about Ecosystem {} " \
                               "due to {}" \
            .format(input_json.get('ecosystem'), e)
        return flask.jsonify(resp_dict), 500
    resp_dict["summary"] = DatabaseIngestion.get_info(input_json.get('ecosystem'))
    return flask.jsonify(resp_dict), 200


app = connexion.FlaskApp(__name__)

app.add_api(defaults.SWAGGER_YAML_PATH)

if __name__ == "__main__":
    app.run()
