#!/usr/bin/env bash

cd backend/data/stanford/
docker build -t stanford .
docker run -d -v `pwd`/models/:/stanford_models/ -p 6080:9000 --name stanford stanford

docker exec -i -t `docker ps --filter name=stanford --format "{{.Names}}"` /bin/bash
echo test >> /stanford_models/test.txt
touch /stanford_models/test.txt

#clear && docker exec -it `docker ps --filter name=backend --format "{{.Names}}"` python3 ./french_wikipedia.py
