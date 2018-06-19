FROM registry.centos.org/centos/centos:7

ENV ALEMBIC_DIR='/alembic'
ENV APP_DIR='/f8a_ingestion'

ENTRYPOINT ["/bin/entrypoint.sh"]

WORKDIR ${APP_DIR}

RUN yum install -y epel-release &&\
    yum install -y gcc git python34-pip python34-devel postgresql &&\
    yum clean all &&\
    mkdir -p ${ALEMBIC_DIR} ${APP_DIR}

# Pre-install application dependencies to better utilize caching in Docker
COPY ./requirements.txt /
RUN pip3 install -r /requirements.txt && rm /requirements.txt

# Alembic migrations
COPY alembic.ini scripts/run-db-migrations.sh ${ALEMBIC_DIR}/
COPY alembic/ ${ALEMBIC_DIR}/alembic

COPY scripts/entrypoint.sh /bin/entrypoint.sh
COPY f8a_ingestion/ ${APP_DIR}/f8a_ingestion
