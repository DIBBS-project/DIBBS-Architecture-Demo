#!/bin/bash

# set -x

PROCESS_REGISTRY_URL="http://127.0.0.1:8000"
PROCESS_DISPATCHER_URL="http://127.0.0.1:8001"
RESOURCE_MANAGER_URL="http://127.0.0.1:8002"
APPLIANCE_REGISTRY_URL="http://127.0.0.1:8003"
CALLBACK_URL="http://requestb.in/1mstk8z1"

IMAGE_NAME="CC-CENTOS-dibbs"

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
# CREATION OF SITES
########################################################

SITE_NAME=KVMatTACC
SITE_URL=https://openstack.tacc.chameleoncloud.org:5000/v2.0

if [ "$1" != "skip" ]; then
  read -r -d '' ACTION_JSON_VALUE <<- EOM
{
  "name": "$SITE_NAME",
  "contact_url": "$SITE_URL"
}
EOM
  ACTION_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$ACTION_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/sites/")



  curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{
    "name": "KVMatTACC",
    "contact_url": "https://openstack.tacc.chameleoncloud.org:5000/v2.0"
  }' 'http://127.0.0.1:8003/sites/'
fi

########################################################
# CREATION OF ACTIONS
########################################################


if [ "$1" != "skip" ]; then
    read -r -d '' ACTION_JSON_VALUE <<- EOM
{
  "name": "configure_node"
}
EOM
    ACTION_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$ACTION_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/actions/")

    read -r -d '' ACTION_JSON_VALUE <<- EOM
{
  "name": "prepare_node"
}
EOM
    ACTION_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$ACTION_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/actions/")

    read -r -d '' ACTION_JSON_VALUE <<- EOM
{
  "name": "update_master_node"
}
EOM
    ACTION_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$ACTION_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/actions/")

    read -r -d '' ACTION_JSON_VALUE <<- EOM
{
  "name": "user_data"
}
EOM
    ACTION_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$ACTION_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/actions/")

    read -r -d '' ACTION_JSON_VALUE <<- EOM
{
  "name": "update_hosts_file"
}
EOM
    ACTION_REGISTRATION_OUTPUT=$(curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$ACTION_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/actions/")
fi


########################################################
# CREATION OF THE APPLIANCES
########################################################

for FOLDER in appliances/*; do
    APPLIANCE_NAME=$(echo $FOLDER | sed 's/.*\///g' | sed 's/\..*//g')

    if [ -f "$FOLDER/description.txt" ]; then
        DESCRIPTION=$(cat $FOLDER/description.txt)
    fi

    if [ -f "$FOLDER/image.txt" ]; then
        IMAGE=$(cat $FOLDER/image.txt)
    fi

    read -r -d '' APPLIANCE_JSON_VALUE <<- EOM
{
  "name": "${APPLIANCE_NAME}",
  "logo_url": "${IMAGE}",
  "description": "${DESCRIPTION}"
}
EOM
    curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$APPLIANCE_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/appliances/"

    APPLIANCE_IMPL_NAME="${APPLIANCE_NAME}_${SITE_NAME}"

    FOO="${APPLIANCE_NAME}_${SITE_NAME}_image.txt"
    echo "trying to read $FOLDER/$FOO"
    echo "trying to read (2) $FOLDER/$FOO"
    if [ -f "$FOLDER/$FOO" ]; then
        APPLIANCE_IMPL_IMG=$(cat "$FOLDER/$FOO")
    fi
    echo "\n-----"
    echo "appliance_impl's logo_url: ${APPLIANCE_IMPL_IMG}"
    echo "-----\n"
    read -r -d '' APPLIANCE_JSON_VALUE <<- EOM
{
  "name": "$APPLIANCE_IMPL_NAME",
  "appliance": "${APPLIANCE_NAME}",
  "image_name": "$IMAGE_NAME",
  "site": "$SITE_NAME",
  "logo_url": "${APPLIANCE_IMPL_IMG}"
}
EOM
    curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$APPLIANCE_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/appliances_impl/"

    for FILE in $FOLDER/*.jinja2; do
        ACTION_NAME=$(echo $FILE | sed 's/.*\///g' | sed 's/\..*//g')
        ESCAPED_CONTENT=$(cat $FILE | sed 's/"/\\\"/g' | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/\\n/g')
        # CONTENT=$(cat $FILE)
        # ESCAPED_CONTENT=$(printf '%q' $CONTENT)

        read -r -d '' SCRIPT_JSON_VALUE <<- EOM
{
  "code": "${ESCAPED_CONTENT}",
  "appliance": "${APPLIANCE_IMPL_NAME}",
  "action": "${ACTION_NAME}"
}
EOM
        echo "============================================"
        echo "$SCRIPT_JSON_VALUE"
        echo "============================================"
        curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$SCRIPT_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/scripts/"
    done

  if [ "$APPLIANCE_NAME" == "hadoop" ]; then

        APPLIANCE_IMPL_NAME="${APPLIANCE_NAME}_BaremetalAtUC"

    FOO="${APPLIANCE_NAME}_${SITE_NAME}_image.txt"
    echo "trying to read $FOLDER/$FOO"
    echo "trying to read (2) $FOLDER/$FOO"
    if [ -f "$FOLDER/$FOO" ]; then
        APPLIANCE_IMPL_IMG=$(cat "$FOLDER/$FOO")
    fi
    echo "\n-----"
    echo "appliance_impl's logo_url: ${APPLIANCE_IMPL_IMG}"
    echo "-----\n"
    read -r -d '' APPLIANCE_JSON_VALUE <<- EOM
{
  "name": "$APPLIANCE_IMPL_NAME",
  "appliance": "${APPLIANCE_NAME}",
  "image_name": "$IMAGE_NAME",
  "site": "$SITE_NAME",
  "logo_url": "${APPLIANCE_IMPL_IMG}"
}
EOM
    curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$APPLIANCE_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/appliances_impl/"

    for FILE in $FOLDER/*.jinja2; do
        ACTION_NAME=$(echo $FILE | sed 's/.*\///g' | sed 's/\..*//g')
        ESCAPED_CONTENT=$(cat $FILE | sed 's/"/\\\"/g' | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/\\n/g')
        # CONTENT=$(cat $FILE)
        # ESCAPED_CONTENT=$(printf '%q' $CONTENT)

        read -r -d '' SCRIPT_JSON_VALUE <<- EOM
{
  "code": "${ESCAPED_CONTENT}",
  "appliance": "${APPLIANCE_IMPL_NAME}",
  "action": "${ACTION_NAME}"
}
EOM
        echo "============================================"
        echo "$SCRIPT_JSON_VALUE"
        echo "============================================"
        curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$SCRIPT_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/scripts/"
    done
  fi

    if [ "$APPLIANCE_NAME" == "hadoop" ]; then

        APPLIANCE_IMPL_NAME="${APPLIANCE_NAME}_BaremetalAtTACC"

    FOO="${APPLIANCE_NAME}_${SITE_NAME}_image.txt"
    echo "trying to read $FOLDER/$FOO"
    echo "trying to read (2) $FOLDER/$FOO"
    if [ -f "$FOLDER/$FOO" ]; then
        APPLIANCE_IMPL_IMG=$(cat "$FOLDER/$FOO")
    fi
    echo "\n-----"
    echo "appliance_impl's logo_url: ${APPLIANCE_IMPL_IMG}"
    echo "-----\n"
    read -r -d '' APPLIANCE_JSON_VALUE <<- EOM
{
  "name": "$APPLIANCE_IMPL_NAME",
  "appliance": "${APPLIANCE_NAME}",
  "image_name": "$IMAGE_NAME",
  "site": "$SITE_NAME",
  "logo_url": "${APPLIANCE_IMPL_IMG}"
}
EOM
    curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$APPLIANCE_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/appliances_impl/"

    for FILE in $FOLDER/*.jinja2; do
        ACTION_NAME=$(echo $FILE | sed 's/.*\///g' | sed 's/\..*//g')
        ESCAPED_CONTENT=$(cat $FILE | sed 's/"/\\\"/g' | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/\\n/g')
        # CONTENT=$(cat $FILE)
        # ESCAPED_CONTENT=$(printf '%q' $CONTENT)

        read -r -d '' SCRIPT_JSON_VALUE <<- EOM
{
  "code": "${ESCAPED_CONTENT}",
  "appliance": "${APPLIANCE_IMPL_NAME}",
  "action": "${ACTION_NAME}"
}
EOM
        echo "============================================"
        echo "$SCRIPT_JSON_VALUE"
        echo "============================================"
        curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$SCRIPT_JSON_VALUE" "$APPLIANCE_REGISTRY_URL/scripts/"
    done
  fi
done

echo ""

exit 0
