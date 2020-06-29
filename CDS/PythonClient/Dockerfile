FROM ubuntu:20.04

ENV APP_HOME /opt/cds_service

RUN  useradd -ms /bin/bash -r -d ${APP_HOME} cds_service

RUN apt-get update \
    && apt-get install -y \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ${APP_HOME}/requirements.txt

RUN pip3 install -r ${APP_HOME}/requirements.txt \
    && rm /${APP_HOME}/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=cds_service:cds_service ./python_client ${APP_HOME}/python_client
COPY --chown=cds_service:cds_service ./main.py ${APP_HOME}

USER cds_service

WORKDIR ${APP_HOME}
ENV PATH=$PATH:${APP_HOME}
ENV PYTHONPATH ${APP_HOME}

CMD ["python3", "main.py"]