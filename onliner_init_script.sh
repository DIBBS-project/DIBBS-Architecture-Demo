#!/bin/bash

if [ "$1" == "--run-on-roger" ]; then
    INFRASTRUCTURE_DESCRIPTION_FILE="infrastructure_description_roger.json"
else
    INFRASTRUCTURE_DESCRIPTION_FILE="infrastructure_description_chameleon.json"
fi

python create_os_users.py $INFRASTRUCTURE_DESCRIPTION_FILE
python create_appliances.py $INFRASTRUCTURE_DESCRIPTION_FILE
python create_lc_operation.py $1

exit 0
