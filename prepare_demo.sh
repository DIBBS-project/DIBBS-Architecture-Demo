#!/bin/bash

echo "Preparing an environment for the demo"

bash create_appliances.sh
bash create_lc_operation.sh
bash create_urbanflow_operation.sh

echo "The environment for the demo has been prepared. Good Luck!"

exit 0
