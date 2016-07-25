#!/bin/bash

# set -x

RESOURCE_MANAGER_URL="http://127.0.0.1:8002"
PASSWORD="bar"

########################################################
# CREATION OF A USER FOR OPENSTACK
########################################################

function extract_user_id {

    RESULT=$(echo $1 | sed 's/.*"user_id"://g' | sed 's/,.*//g' | sed 's/}//g')

    echo "$RESULT"
}

function extract_api_token {

    RESULT=$(echo $1 | sed 's/.*"api_token"://g' | sed 's/,.*//g' | sed 's/}//g')

    echo "$RESULT"
}


if [ "$#" -ne 2 ]; then
    if [ "$#" -ne 3 ]; then
        echo "Usage: $0 <username> <project> [<resource manager URL>]"
        exit 1
    fi
fi

USER=$1
PROJECT=$2
if [ "$#" -ne 2 ]; then
    RESOURCE_MANAGER_URL=$3
fi


# Create a new user
echo "Creating user \"$USER\" with project \"$PROJECT\"..."

USER_CREATION_OUTPUT=$(curl -H "Content-Type: application/json" -X POST -d "{\"username\": \"$USER\", \"project\": \"$PROJECT\", \"password\": \"$PASSWORD\"}" $RESOURCE_MANAGER_URL/users/)
USER_ID=$(extract_user_id $USER_CREATION_OUTPUT)
TOKEN=$(extract_api_token $USER_CREATION_OUTPUT)

# Upload openstack password in an encrypted way
USER_GET_OUTPUT=$(curl -H "TOKEN: $TOKEN" -X GET $RESOURCE_MANAGER_URL/users/$USER_ID/)
echo "$USER_GET_OUTPUT" | sed 's/.*"security_certificate":"//g' | sed 's/"}//g' | awk '{gsub(/\\n/,"\n")}1' > certificate.txt

set +x

echo "Please enter your OpenStack Password: "
read -sr OS_PASSWORD_INPUT

#echo "$OS_PASSWORD_INPUT" | openssl rsautl -encrypt -pubin -inkey certificate.txt > cipher.txt
echo "$OS_PASSWORD_INPUT" > password.txt
cat password.txt | openssl rsautl -encrypt -pubin -inkey certificate.txt > cipher.txt
rm -rf password.txt
rm -rf certificate.txt

#echo "=========== encrypted(password) ==========="
#cat cipher.txt
#echo "==========================================="

# set -x

# Send the encrypted password to the webservice
curl -i -H "TOKEN: $TOKEN" -X PATCH -F 'data=@cipher.txt' $RESOURCE_MANAGER_URL/users/$USER_ID/
rm -rf cipher.txt

# echo "MRCLUSTER_TOKEN: $TOKEN"
echo ""

if [ -f "existing_nodes.txt" ]; then
    # Create cluster
    read -r -d '' CLUSTER_JSON_VALUE <<- EOM
{
        "name": "MyHadoopCluster",
        "appliance_impl": "urbanflow_KVM@TACC",
        "common_appliance_impl": "common_KVM@TACC",
        "user_id": 1,
        "appliance": "hadoop_urbanflow",
        "master_node_ip": "129.114.110.233",
        "master_node_ip": "1",
        "hosts_ips": [
            "129.114.110.233"
        ]
}
EOM
    curl -u admin:pass -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$CLUSTER_JSON_VALUE" "$RESOURCE_MANAGER_URL/clusters/"

    # Create nodes
    while read l; do
        IP=$(echo $l | awk '{print $1}')
        NAME=$(echo $l | awk '{print $2}')
        IS_MASTER=$(echo $l | awk '{print $3}')
        if [ "$IS_MASTER" != "" ]; then
            IS_MASTER="true"
        else
            IS_MASTER="false"
        fi
        if [ "$NAME" != "" ]; then
            echo "$IP->$NAME"

            read -r -d '' CLUSTER_JSON_VALUE <<- EOM
{
        "name": "$NAME",
        "cluster_id": 1,
        "action": "nodeploy",
        "instance_ip": "$IP",
        "is_master": $IS_MASTER
}
EOM
            curl -u admin:pass -H "TOKEN: $TOKEN"  -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "$CLUSTER_JSON_VALUE" "$RESOURCE_MANAGER_URL/hosts/"

        fi
    done <existing_nodes.txt
fi

exit 0
