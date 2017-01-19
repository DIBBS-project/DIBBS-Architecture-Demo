#!/bin/bash

set -x

# Fix an issue with bridge MTU which prevents containers to access internet
#  cf: https://forums.docker.com/t/cannot-wget-curl-git-apt-get-to-internet-from-within-docker-container/19373/4
sudo iptables -I FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

# Check if superuser is running this script
if [[ $UID != 0 ]]; then
    echo "Please run this script with sudo:"
    echo "sudo $0 $*"
    exit 1
fi

# Check if APT or yum are installed
APT_PATH=$(which apt-get)
YUM_PATH=$(which yum)
if [ "${APT_PATH}${YUM_PATH}" == "" ]; then
    echo "Could not find Apt nor Yum.  Are you running this script from a Debian or RHEL-like system?"
    exit 1
fi

# Check if docker is installed
DOCKER_PATH=$(which docker)
if [ "$DOCKER_PATH" == "" ]; then
    # Install docker
    curl -fsSL https://get.docker.com/ | sh
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
