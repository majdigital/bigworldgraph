FROM python:3.6-slim
MAINTAINER Kaleidophon (https://github.com/Kaleidophon)

RUN mkdir -p /data/src/app
WORKDIR /data/src/app
COPY ./bwg/run.py ./bwg/run.py
COPY ./bwg/settings.py ./bwg/settings.py
COPY ./bwg/neo4j_extensions.py ./bwg/neo4j_extensions.py
COPY ./bwg/helpers.py ./bwg/helpers.py
COPY ./requirements.txt .
COPY ./setup.py .
RUN ls -lah
RUN ls -lah ./bwg

EXPOSE 5000

RUN pip3 install -r ./requirements.txt
RUN python3 setup.py install

WORKDIR /data/src/app/bwg

CMD ["python3", "./run.py"]
