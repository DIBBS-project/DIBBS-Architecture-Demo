#!/bin/bash

USER="jpastor"
PROJECT="FG-392"

if [ "$1" == "--run-on-roger" ]; then
    PROJECT="DIBBs"
fi

#bash create_appliances.sh; bash create_os_user.sh ${USER} ${PROJECT}; bash create_lc_operation.sh; cat processinst_example.txt
python create_appliances.py $1; python create_os_user.py ${USER} ${PROJECT} $1; bash create_lc_operation.sh; cat processinst_example.txt

exit 0
