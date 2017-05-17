FROM python:3.6-slim
MAINTAINER Kaleidophon (https://github.com/Kaleidophon)

RUN mkdir -p /data/src/app
WORKDIR /data/src/app

# Copy necessary modules
COPY ./bwg/run_api.py ./bwg/run_api.py
COPY ./bwg/api_config.py ./bwg/api_config.py
COPY ./bwg/neo4j_extensions.py ./bwg/neo4j_extensions.py
COPY ./bwg/helpers.py ./bwg/helpers.py
COPY ./requirements.txt .
COPY ./setup.py .

RUN pip3 install -r ./requirements.txt
RUN python3 setup.py install

WORKDIR /data/src/app/bwg

EXPOSE 5000

CMD ["python3", "./run_api.py"]
