#!/bin/sh
set -e

cd $(dirname "$0")

gitpush()
{
    REPO=$1
    pushd $REPO > /dev/null
    git push
    popd > /dev/null
}

while read -r REPO
do
    gitpush $REPO
done < repolist.txt
