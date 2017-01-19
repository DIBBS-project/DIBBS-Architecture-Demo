#!/bin/bash

set -x

# Install the services in containers
docker-compose down
docker-compose rm -f
docker-compose pull
docker-compose build $1
docker-compose up -d
