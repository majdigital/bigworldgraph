#!/usr/bin/env bash

echo Downloading stanford model files if necessary...
if [ ! -f backend/data/stanford/models/UD_French.gz ]; then wget majconsulting.ch/newsletters/stanford_models_french_100417.zip -P backend/data/stanford/models/; fi
if [ -f backend/data/stanford/models/stanford_models_french_100417.zip ]; then unzip backend/data/stanford/models/stanford_models_french_100417.zip -d backend/data/stanford/models/ && rm backend/data/stanford/models/stanford_models_french_100417.zip; fi

# Check if necessary containers exist
if [[ ! $(docker ps --filter name=backend --format "{{.Names}}") ]]; then
    echo No backend container found. Please execute docker-compose build \&\& dockercompose up first.
    exit 1
fi
if [[ $(docker ps --filter name=stanford --format "{{.Names}}") ]]; then
    echo A stanford container already exists. Please shut it down first.
    exit 1
fi

# Build stanford container and run pipeline
cd backend/data/stanford/
docker build -t stanford .
docker run -d -v `pwd`/models/:/stanford_models/ -p 6080:9000 --name stanford stanford
docker network connect bigworldgraph_app-tier `docker ps --filter name=stanford --format "{{.Names}}"` --alias stanford
clear && docker exec -it `docker ps --filter name=backend --format "{{.Names}}"` python3 ./french_wikipedia.py
echo Stopping stanford container...
#docker rm $(docker stop $(docker ps --filter name=stanford --format "{{.Names}}"))
