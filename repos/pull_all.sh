#!/bin/sh
set -e

cd $(dirname "$0")

gitpull()
{
    REPO=$1
    pushd $REPO > /dev/null
    git pull
    popd > /dev/null
}

while read -r REPO
do
    gitpull $REPO
done < repolist.txt
