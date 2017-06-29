#!/usr/bin/env bash
python3 -m unittest discover ./tests/
docker kill $(docker ps -q)
docker rm $(docker ps -a -q)