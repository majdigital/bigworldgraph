#!/usr/bin/env bash

clear && docker exec -it `docker ps --filter name=backend --format "{{.Names}}"` python3 ./french_wikipedia.py
