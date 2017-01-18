#!/bin/sh
set -e

cd $(dirname "$0")

gitpush()
{
    REPO=$1
    git -C $REPO push
}

while read -r REPO
do
    gitpush $REPO
done < repolist.txt
