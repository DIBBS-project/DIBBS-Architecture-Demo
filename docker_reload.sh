#!/bin/bash

docker-compose down
docker-compose rm -f
docker-compose pull
docker-compose build
docker-compose up -d

exit 0
