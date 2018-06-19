#!/bin/bash

# fail if smth fails
# the whole env will be running if test suite fails so you can debug
set -e

# for debugging this script, b/c I sometimes get
# unable to prepare context: The Dockerfile (Dockerfile.tests) must be within the build context (.)
set -x

here=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

TIMESTAMP="$(date +%F-%H-%M-%S)"

POSTGRES_IMAGE_NAME="registry.centos.org/centos/postgresql-94-centos7:latest"

TESTDB_CONTAINER_NAME="ingestion-tests-db-${TIMESTAMP}"
DOCKER_NETWORK="F8aIngestionTest"

gc() {
  retval=$?
  # FIXME: make this configurable
  echo "Stopping test containers"
  docker stop ${CONTAINER_NAME} ${TESTDB_CONTAINER_NAME} || :
  echo "Removing test containers"
  docker rm -v ${CONTAINER_NAME} || :
  echo "Removing network ${DOCKER_NETWORK}"
  docker network rm ${DOCKER_NETWORK} || :
  deactivate
  rm -rf venv/
  exit $retval
}

trap gc EXIT SIGINT

function prepare_venv() {
    VIRTUALENV=`which virtualenv`
    if [ $? -eq 1 ]
    then
        # python34 which is in CentOS does not have virtualenv binary
        VIRTUALENV=`which virtualenv-3`
    fi

    ${VIRTUALENV} -p python3 venv && source venv/bin/activate
    if [ $? -ne 0 ]
    then
        printf "${RED}Python virtual environment can't be initialized${NORMAL}"
        exit 1
    fi
}

prepare_venv
pip3 install -r tests/requirements.txt

echo "Creating network ${DOCKER_NETWORK}"
docker network create ${DOCKER_NETWORK}

echo "Starting/creating containers:"
# first start the database under different name, so that we don't overwrite a non-testing db
# NOTE: we omit pgbouncer while running tests
docker run -d \
    --env-file tests/postgres.env \
    --network ${DOCKER_NETWORK} \
    -p 5432:5432 \
    --name ${TESTDB_CONTAINER_NAME} ${POSTGRES_IMAGE_NAME}
DB_CONTAINER_IP=$(docker inspect --format "{{.NetworkSettings.Networks.${DOCKER_NETWORK}.IPAddress}}" ${TESTDB_CONTAINER_NAME})
DB_CONTAINER_IP="0.0.0.0"
# TODO: this is duplicating code with server's runtest, we should refactor
echo "Waiting for postgres to fully initialize"
set +x
for i in {1..10}; do
  retcode=`curl http://${DB_CONTAINER_IP}:5432 &>/dev/null || echo $?`
  if test "$retcode" == "52"; then
    break
  fi;
  sleep 1
done;
set -x

export POSTGRESQL_USER=coreapi
export POSTGRESQL_PASSWORD=coreapi
export POSTGRESQL_DATABASE=coreapi

python3 `which pytest` --cov=f8a_ingestion/ --cov-report term-missing -vv tests

echo "Test suite passed \\o/"
