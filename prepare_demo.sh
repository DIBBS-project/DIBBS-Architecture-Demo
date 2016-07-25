#!/bon/bash

if [ "$#" -ne 2 ]; then
    if [ "$#" -ne 3 ]; then
        echo "Usage: $0 <username> <project"
        exit 1
    fi
fi

echo "Preparing an environment for the demo"

bash create_appliances.sh
bash create_os_user.sh $1 $2
bash create_lc_operation.sh
bash create_urbanflow_operation.sh

echo "The environment for the demo has been prepared. Good Luck!"

exit 0
