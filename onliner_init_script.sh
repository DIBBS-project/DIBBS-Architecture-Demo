#!/bin/bash

USER="jpastor"
PROJECT="FG-392"

if [ "$1" == "--run-on-roger" ]; then
    PROJECT="DIBBs"
fi

python create_appliances.py infrastructure_description.json
python create_os_users.py infrastructure_description.json
bash create_lc_operation.sh

cat processinst_example.txt

exit 0
