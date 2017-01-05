#!/bin/sh
set -e

cd $(dirname "$0")

gitpull()
{
    REPO=$1
    git -C $REPO pull
}

while read -r REPO
do
    gitpull $REPO
done < repolist.txt
