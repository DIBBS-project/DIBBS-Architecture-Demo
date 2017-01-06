#!/bin/sh
set -e

cd $(dirname "$0")

gitstatus()
{
    REPO=$1

    echo $REPO
    git -C $REPO status
}

while read -r REPO
do
    echo ---
    gitstatus $REPO
done < repolist.txt
