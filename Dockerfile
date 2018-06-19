FROM registry.centos.org/centos/centos:7

RUN yum install -y epel-release &&\
    yum install -y gcc git python34-pip python34-devel postgresql &&\
    yum clean all

COPY ./requirements.txt /

RUN pip3 install --upgrade pip>=10.0.0 &&\
    pip3 install -r requirements.txt && rm requirements.txt

COPY ./f8a_ingestion /f8a_ingestion
COPY ./alembic /alembic
COPY ./alembic.ini /alembic.ini
COPY ./scripts/run-db-migrations.sh /alembic/run-db-migrations.sh
RUN chmod +x /alembic/run-db-migrations.sh

ADD scripts/entrypoint.sh /bin/entrypoint.sh

RUN chmod 777 /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]
