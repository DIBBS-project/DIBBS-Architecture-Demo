#!/bin/sh
set -e

cd $(dirname "$0")

gitstatus()
{
    REPO=$1

    echo $REPO
    pushd $REPO > /dev/null
    git status
    popd > /dev/null
}

while read -r REPO
do
    echo ---
    gitstatus $REPO
done < repolist.txt
