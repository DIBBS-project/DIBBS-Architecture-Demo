#!/bin/bash

set -x

PROCESS_REGISTRY_URL="http://127.0.0.1:8000"
PROCESS_DISPATCHER_URL="http://127.0.0.1:8001"
MISTER_CLUSTER_URL="http://127.0.0.1:8002"
CALLBACK_URL="http://requestb.in/1mstk8z1"

echo "Testing the architecture"

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

read -r -d '' STRING_PARAMETERS_JSON_VALUE <<- EOM
[
   "env3"
]
EOM
STRING_PARAMETERS_JSON_VALUE_ESCAPED=$(echo $STRING_PARAMETERS_JSON_VALUE | sed 's/"/\\\"/g')

read -r -d '' FILE_PARAMETERS_JSON_VALUE <<- EOM
[
   "input_file"
]
EOM
FILE_PARAMETERS_JSON_VALUE_ESCAPED=$(echo $FILE_PARAMETERS_JSON_VALUE | sed 's/"/\\\"/g')

read -r -d '' PROCESS_JSON_VALUE <<- EOM
{
    "name": "Urbanflow",
    "description": "Operation that runs the comlete UrbanFlow workflow on data extracted from twitter (New York city).",
    "string_parameters": "[]",
    "logo_url": "http://dropbox.jonathanpastor.fr/dibbs/twitterapi.png",
    "file_parameters": "[]"
}
EOM

echo $PROCESS_JSON_VALUE

PROCESS_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$PROCESS_JSON_VALUE" "$PROCESS_REGISTRY_URL/processdefs/")
PROCESS_ID=$(extract_id $PROCESS_REGISTRATION_OUTPUT)
echo $PROCESS_ID

########################################################
# CREATION OF PROCESS IMPLEMENTATION
########################################################

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

read -r -d '' ENVIRONMENT_JSON_VALUE <<- EOM
{
   "ENV1":"env1",
   "ENV2":"2",
   "ENV3":"\${env3}"
}
EOM
ENVIRONMENT_JSON_VALUE_ESCAPED=$(echo $ENVIRONMENT_JSON_VALUE | sed 's/"/\\\"/g')

read -r -d '' PROCESS_IMPL_JSON_VALUE <<- EOM
{
    "name": "urbanflow_impl",
    "appliance": "hadoop_urbanflow",
    "process_definition": $PROCESS_ID,
    "archive_url": "http://dropbox.jonathanpastor.fr/dibbs.tgz",
    "executable":"sudo bash run_pipeline.sh",
    "cwd":"/root/script",
    "environment": "{}",
    "argv": "[]",
    "output_type":"file",
    "output_parameters": "$OUTPUT_PARAMS_JSON_VALUE_ESCAPED"
}
EOM

echo $PROCESS_IMPL_JSON_VALUE

PROCESS_IMPL_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$PROCESS_IMPL_JSON_VALUE" "$PROCESS_REGISTRY_URL/processimpls/")
PROCESS_IMPL_ID=$(extract_id $PROCESS_IMPL_REGISTRATION_OUTPUT)
echo $PROCESS_IMPL_ID

exit 0
