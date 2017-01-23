#!/bin/sh
set -e

GIT_BRANCH=${GIT_BRANCH:-master}

cd $(dirname "$0")

gitclone()
{
    REPO=$1
    git clone -b $GIT_BRANCH https://github.com/DIBBS-project/${REPO}.git
}

while read -r REPO
do
    gitclone $REPO
done < repolist.txt
