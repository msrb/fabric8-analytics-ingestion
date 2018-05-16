FROM registry.devshift.net/fabric8-analytics/f8a-ingestion

ENV LANG=en_US.UTF-8 \
    # place where to download & unpack artifacts
    WORKER_DATA_DIR='/var/lib/f8a_ingestion' \
    # home directory
    HOME='/workdir' \
    # place for alembic migrations
    ALEMBIC_DIR='/alembic'

# Make sure random user has place to store files
RUN mkdir -p ${HOME} ${WORKER_DATA_DIR} ${ALEMBIC_DIR}/alembic/ && \
    chmod 777 ${HOME} ${WORKER_DATA_DIR}
WORKDIR ${HOME}

COPY requirements.txt /tmp/f8a_ingestion/

RUN cd /tmp/f8a_ingestion/ && \
    pip3 install -r requirements.txt

COPY alembic.ini hack/run-db-migrations.sh ${ALEMBIC_DIR}/
COPY alembic/ ${ALEMBIC_DIR}/alembic
