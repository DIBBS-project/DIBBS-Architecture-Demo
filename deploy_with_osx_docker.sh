#!/bin/bash

if ! which docker-compose > /dev/null; then
  echo "You need to install Docker for Mac first"
  echo "Go to https://docs.docker.com/engine/installation/mac/#/docker-for-mac"
  exit 1
fi

# Install the services in containers
docker-compose down
docker-compose rm -f
docker-compose pull
docker-compose build $1
docker-compose up -d

exit 0
