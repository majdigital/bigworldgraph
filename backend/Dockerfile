FROM python:3.6
MAINTAINER Kaleidophon (https://github.com/Kaleidophon)

RUN echo password container $NEO4J_PASSWORD

RUN mkdir -p /data/src/app
WORKDIR /data/src/app

# Copy necessary modules
COPY ./bwg/ ./bwg/
COPY ./tests/ ./tests/
COPY ./requirements.txt .
COPY ./setup.py .

RUN pip3 install -r ./requirements.txt

EXPOSE 5000
CMD python3 ./bwg/run_api.py
