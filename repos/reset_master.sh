#!/bin/bash
set -e

cd $(dirname "$0")

reset_remote_master()
{
    REPO=$1
    pushd $REPO > /dev/null
    git fetch origin
    git reset --hard origin/master
    git checkout master
    popd > /dev/null
}

read -p "Reset all repositories to master branch? (UNCOMMITTED WORK WILL BE LOST) [y/N]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    while read -r REPO
    do
        reset_remote_master $REPO
    done < repolist.txt
else
    echo "Aborting."
fi
