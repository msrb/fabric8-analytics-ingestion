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

"""Configuration."""

import os
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

SWAGGER_YAML_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../swagger/swagger.yaml')

DEFAULT_PGDATABASE = 'f8a-ingestion'
DEFAULT_PGPORT = '5432'


def get_psql_conn_str(enable_ssl=False):

    conn_str = 'postgresql://{user}:{password}@{host}:{port}/{db}?sslmode={ssl}'.format(
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        host=os.environ.get('PGHOST'),
        port=os.environ.get('PGPORT', DEFAULT_PGPORT),
        db=os.environ.get('PGDATABASE', DEFAULT_PGDATABASE),
        ssl=str(enable_ssl).lower()
    )

    return conn_str


#     def _make_postgres_string(password):
#         """Create postgres connection string.
#
#         It's parametrized, so it's possible to
#         create either quoted or unquoted version of connection string.
#         Note that it's outside of class since there is no simple way how to call it inside the class
#         without class initialization.
#         :param password: password which will be embedded into Postgres connection string
#         :return: fully working postgres connection string
#         """
#         connection = 'postgresql://{user}:{password}@{pgbouncer_host}:{pgbouncer_port}' \
#                      '/{database}?sslmode=disable'. \
#             format(user=environ.get('POSTGRESQL_USER'),
#                    password=environ.get('POSTGRESQL_PASSWORD'),
#                    pgbouncer_host=environ.get('PGBOUNCER_SERVICE_HOST', 'coreapi-postgres'),
#                    pgbouncer_port=environ.get('PGBOUNCER_SERVICE_PORT', '5432'),
#                    database=environ.get('POSTGRESQL_DATABASE'))
#         return connection
#
#     UNQUOTED_POSTGRES_CONNECTION = _make_postgres_string(environ.get('POSTGRESQL_PASSWORD', ''))
#     POSTGRES_CONNECTION = _make_postgres_string(
#         quote(environ.get('POSTGRESQL_PASSWORD', ''), safe=''))
#
#
# configuration = F8AConfiguration()
