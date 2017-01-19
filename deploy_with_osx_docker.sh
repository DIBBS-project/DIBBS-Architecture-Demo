#!/bin/bash

if ! which docker-compose > /dev/null; then
  echo "You need to install Docker for Mac first"
  echo "Go to https://docs.docker.com/engine/installation/mac/#/docker-for-mac"
  exit 1
fi

./run_with_docker.sh
