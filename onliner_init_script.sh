#!/bin/bash

USER="jpastor"
PROJECT="FG-392"

#bash create_appliances.sh; bash create_os_user.sh ${USER} ${PROJECT}; bash create_lc_operation.sh; cat processinst_example.txt
python create_appliances.py; python create_os_user.py ${USER} ${PROJECT}; bash create_lc_operation.sh; cat processinst_example.txt

exit 0
