#!/usr/bin/env bash

echo Downloading stanford models files as necessary...
if [ ! -f ./stanford_models/UD_French.gz ]; then wget majconsulting.ch/newsletters/stanford_models_french_100417.zip -P ./stanford_models/; fi
if [ -f ./stanford_models/stanford_models_french_100417.zip ]; then unzip ./stanford_models/stanford_models_french_100417.zip -d ./stanford_models/ && rm ./stanford_models/stanford_models_french_100417.zip; fi

# Check if necessary containers exist
if [[ ! $(docker ps --filter name=backend --format "{{.Names}}") ]]; then
    echo No backend container found. Please execute docker-compose build \&\& dockercompose up first.
    exit 1
fi
if [[ $(docker ps --filter name=stanford --format "{{.Names}}") ]]; then
    docker rm $(docker stop $(docker ps --filter name=stanford --format "{{.Names}}"))
fi

# Build stanford container and run pipeline
cd ./stanford/
docker build -t stanford .
docker run -d --volumes-from $(docker ps --filter name=backend --format "{{.Names}}") -p 6080:9000 --network="bigworldgraph_app-tier" --name stanford stanford
clear && docker exec `docker ps --filter name=backend --format "{{.Names}}"` python3 ./french_wikipedia.py
