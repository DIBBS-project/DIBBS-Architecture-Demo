#!/bin/sh
set -e

cd $(dirname "$0")

gitclone()
{
    REPO=$1
    git clone -b master https://github.com/DIBBS-project/${REPO}.git
}

while read -r REPO
do
    gitclone $REPO
done < repolist.txt
