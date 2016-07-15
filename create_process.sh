#!/bin/bash

set -x

PROCESS_REGISTRY_URL="http://127.0.0.1:8000"
PROCESS_DISPATCHER_URL="http://127.0.0.1:8001"
MISTER_CLUSTER_URL="http://127.0.0.1:8002"
CALLBACK_URL="http://requestb.in/1mstk8z1"

echo "Testing the streaming architecture"

function extract_token {

    RESULT=$(echo $1 | sed 's/.*"token"://g' | sed 's/,.*//g' | sed 's/"//g' | sed 's/}//g')

    echo "$RESULT"
}

function extract_id {

    RESULT=$(echo $1 | sed 's/.*"id"://g' | sed 's/,.*//g')

    echo "$RESULT"
}

########################################################
# CREATION OF PROCESS
########################################################

read -r -d '' ENVIRONMENT_JSON_VALUE <<- EOM
{
   "ENV1":"env1",
   "ENV2":"2",
   "ENV3":"${env3}"
}
EOM
ENVIRONMENT_JSON_VALUE_ESCAPED=$(echo $ENVIRONMENT_JSON_VALUE | sed 's/"/\\\"/g')

read -r -d '' OUTPUT_PARAMS_JSON_VALUE <<- EOM
{
   "file_path":"output.txt"
}
EOM
OUTPUT_PARAMS_JSON_VALUE_ESCAPED=$(echo $OUTPUT_PARAMS_JSON_VALUE | sed 's/"/\\\"/g')

read -r -d '' ARGV_JSON_VALUE <<- EOM
[
   "@{input_file}",
   "parameter"
]
EOM
ARGV_JSON_VALUE_ESCAPED=$(echo $ARGV_JSON_VALUE | sed 's/"/\\\"/g')

read -r -d '' PROCESS_JSON_VALUE <<- EOM
{
    "name": "line_counter",
    "author": 1,
    "argv": "$ARGV_JSON_VALUE_ESCAPED",
    "output_type":"file",
    "output_parameters": "$OUTPUT_PARAMS_JSON_VALUE_ESCAPED"
}
EOM

echo $PROCESS_JSON_VALUE

PROCESS_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$PROCESS_JSON_VALUE" "$PROCESS_REGISTRY_URL/processdefs/")
PROCESS_ID=$(extract_id $PROCESS_REGISTRATION_OUTPUT)
echo $PROCESS_ID

########################################################
# CREATION OF PROCESS IMPLEMENTATION
########################################################

read -r -d '' PROCESS_IMPL_JSON_VALUE <<- EOM
{
    "name": "line_counter_hadoop",
    "author": 1,
    "appliance": "hadoop",
    "process_definition": $PROCESS_ID,
    "archive_url": "http://dropbox.jonathanpastor.fr/archive.tgz",
    "executable":"bash run_job.sh",
    "cwd":"~",
    "environment": "$ENVIRONMENT_JSON_VALUE_ESCAPED"
}
EOM

echo $PROCESS_IMPL_JSON_VALUE

PROCESS_IMPL_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$PROCESS_IMPL_JSON_VALUE" "$PROCESS_REGISTRY_URL/processimpls/")
PROCESS_IMPL_ID=$(extract_id $PROCESS_IMPL_REGISTRATION_OUTPUT)
echo $PROCESS_IMPL_ID

exit 0
