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

"""Utility class."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from f8a_ingestion.models import Ecosystem, create_db_scoped_session
from f8a_ingestion.enums import EcosystemBackend
import logging


logger = logging.getLogger(__name__)


def get_session():
    """Retrieve the database connection session."""
    try:
        session = create_db_scoped_session()
    except Exception as e:
        raise Exception("session could not be loaded due to {}".format(e))
    return session


def validate_request_data(input_json):
    """Validate the data.
    :param input_json: dict, describing data
    :return: boolean, result
    """
    backend_list = list(EcosystemBackend.__members__.keys())
    validate_string = "{} is not valid"
    if 'ecosystem' not in input_json:
        validate_string = validate_string.format("Ecosystem name")
        return False, validate_string
    back_validate = "{} is not valid backend"
    if input_json.get('backend', None) not in backend_list:
        back_validate = back_validate.format("Backend")
        return False, back_validate

    return True, None


def _eco_object_dict(data):
    """Convert the object of type Ecosystem into a dictionary."""
    return_dict = {Ecosystem.name: data["ecosystem"],
                   Ecosystem.url: data["url"],
                   Ecosystem._backend: data["backend"],
                   }
    return return_dict


class DatabaseIngestion:
    """Class to ingest data into Database."""

    @staticmethod
    def update_data(data):
        """Update existing record in the database.
        :param data: dict, describing Ecosystem data
        :return: None
        """
        try:
            session = get_session()
            session.query(Ecosystem). \
                filter(Ecosystem.name == data["ecosystem"]). \
                update(_eco_object_dict(data))
            session.commit()
        except NoResultFound:
            raise Exception("Record trying to update does not exist")
        except SQLAlchemyError:
            session.rollback()
            raise Exception("Error in updating data")

    @classmethod
    def store_record(cls, data):
        """Store new record in the database.
        :param data: dict, describing Ecosystem data
        :return: boolean based on completion of process
        """
        eco_name = data.get("ecosystem", None)
        if eco_name is None:
            logger.info("Ecosystem not found")
            raise Exception("Ecosystem not found")
        try:
            session = get_session()
            entry = Ecosystem(
                name=data['ecosystem'],
                url=data.get('url', 'None'),
                backend=data.get('backend')
            )
            session.add(entry)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise Exception("Error in storing the record in current session")
        except Exception as e:
            raise Exception("Error in storing the record due to {}".format(e))
        return cls.get_info(data["ecosystem"])

    @classmethod
    def get_info(cls, search_key):
        """Get information about github url.
        :param search_key: Ecosystem name to search database
        :return: record from database if exists
        """
        if not search_key:
            return {'error': 'No key found', 'is_valid': False}

        session = get_session()

        try:
            entry = session.query(Ecosystem) \
                .filter(Ecosystem.name == search_key).one()
        except NoResultFound:
            logger.info("No info for search_key '%s' was found", search_key)
            return {'error': 'No information in the records', 'is_valid': False}
        except SQLAlchemyError:
            session.rollback()
            raise Exception("Error in retrieving the record in current session")
        except Exception as e:
            raise {
                'error': 'Error in getting info due to {}'.format(e),
                'is_valid': False
            }

        return {'is_valid': True, 'data': entry.to_dict()}
