#!/bin/bash
set -e

cd $(dirname "$0")

reset_remote_stable()
{
    REPO=$1
    git -C $REPO fetch origin
    git -C $REPO reset --hard origin/stable
}

read -p "Reset all repositories to stable branch? (UNCOMMITTED WORK WILL BE LOST) [y/N]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    while read -r REPO
    do
        reset_remote_stable $REPO
    done < repolist.txt
else
    echo "Aborting."
fi
