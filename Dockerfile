FROM registry.centos.org/centos/centos:7

ENV LANG=en_US.UTF-8 \
    # place where to download & unpack artifacts
    INGESTION_DIR='/var/lib/f8a_ingestion' \
    # home directory
    HOME='/workdir' \
    # place for alembic migrations
    ALEMBIC_DIR='/alembic'
RUN yum install -y epel-release &&\
    yum install -y gcc git python34-pip python34-requests httpd httpd-devel python34-devel &&\
    yum clean all

RUN pip3 install --upgrade pip>=10.0.0

# Make sure random user has place to store files
RUN mkdir -p ${HOME} ${INGESTION_DIR} ${ALEMBIC_DIR}/alembic/ && \
    chmod 777 ${HOME} ${INGESTION_DIR}
WORKDIR ${HOME}

COPY requirements.txt /tmp/f8a_ingestion/

RUN cd /tmp/f8a_ingestion/ && \
    pip3 install -r requirements.txt

COPY alembic.ini hack/run-db-migrations.sh ${ALEMBIC_DIR}/
COPY alembic/ ${ALEMBIC_DIR}/alembic
