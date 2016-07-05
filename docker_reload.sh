#!/bin/bash

set -x

# Check if superuser is running this script
if [[ $UID != 0 ]]; then
    echo "Please run this script with sudo:"
    echo "sudo $0 $*"
    exit 1
fi

# Check if APT is installed
APT_PATH=$(which apt-get)
if [ "$APT_PATH" == "" ]; then
    echo "Could  not find APT.  Are you running this  script from a  debian like system?"
    exit 1
fi

# Check if docker is installed
DOCKER_PATH=$(which docker)
if [ "$DOCKER_PATH" == "" ]; then
    # Install docker
    curl -fsSL https://test.docker.com/ | sh
fi

# Run docker
sudo service docker start

# Check if docker-compose is installed
DOCKER_COMPOSE_PATH=$(which docker-compose)
if [ "$DOCKER_COMPOSE_PATH" == "" ]; then
    # Install docker-compose
    curl -L https://github.com/docker/compose/releases/download/1.8.0-rc1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install the services in containers
docker-compose down
docker-compose rm -f
docker-compose pull
docker-compose build
docker-compose up -d

exit 0
