FROM ubuntu:19.10

ENV APP_HOME /opt/crm_service

RUN  useradd -ms /bin/bash -r -d ${APP_HOME} crm_service

# For MSSQL ODBC driver
#ENV ACCEPT_EULA=Y
#ENV OS_VERSION=19.10

RUN buildDeps='curl software-properties-common' \
    && set -x \
    && apt-get update \
    && apt-get install -y $buildDeps \
#    && apt-get update \
#    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
#    && curl https://packages.microsoft.com/config/ubuntu/${OS_VERSION}/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y \
#        msodbcsql17 \
#        unixodbc-dev \
        python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove $buildDeps

COPY requirements.txt ${APP_HOME}/requirements.txt

RUN pip3 install -r ${APP_HOME}/requirements.txt \
    && rm /${APP_HOME}/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=crm_service:crm_service client ${APP_HOME}/client
COPY --chown=crm_service:crm_service ./main.py ${APP_HOME}

USER crm_service

WORKDIR ${APP_HOME}
ENV PATH=$PATH:${APP_HOME}
ENV PYTHONPATH ${APP_HOME}

CMD ["python3", "main.py"]