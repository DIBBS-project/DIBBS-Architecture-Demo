#!/bin/bash

# Check if APT or yum are installed
APT_PATH=$(which apt-get)
YUM_PATH=$(which yum)

# Check if screen is installed
SCREEN_PATH=$(which screen)
if [ "$SCREEN_PATH" == "" ]; then
    if [ "${APT_PATH}${YUM_PATH}" == "" ]; then
        echo "Could  not install 'screen' via  APT or yum.  Please install the screen unix tool on this computer!"
        exit 1
    else
        CMD="${APT_PATH}${YUM_PATH} install screen"
        $CMD
    fi
fi

# Check if pip is installed
PIP_PATH=$(which pip)
if [ "$PIP_PATH" == "" ]; then
    if [ "${APT_PATH}${YUM_PATH}" == "" ]; then
        echo "Could  not install 'python-pip' via  APT or yum.  Please install pip on this computer!"
        exit 1
    else
        CMD="${APT_PATH}${YUM_PATH} install python-pip"
        $CMD
    fi
fi

function install_and_configure_agents() {

    # Cleaning project sources
    if [ -d projects ]; then
        rm -rf projects
    fi
    mkdir projects

    pushd projects


    # Cleaning existing screens
    SCREEN_NAME="agents"
    screen -X -S $SCREEN_NAME quit || true

    COMMON_SCREEN_ARGS="-S $SCREEN_NAME -X screen"
    screen -AdmS $SCREEN_NAME

    # Cleaning existing django processes
    ps aux | grep "manage.py runserver" | awk '{print $2}' | xargs kill -9

    ############################################################################
    # Cloning Agents projects and preparing dependencies
    ############################################################################
    git clone -b development https://github.com/DIBBS-project/operation_registry.git
    git clone -b development https://github.com/DIBBS-project/operation_manager.git
    git clone -b development https://github.com/DIBBS-project/appliance_registry.git
    git clone -b development https://github.com/DIBBS-project/resource_manager.git
    git clone -b master https://github.com/DIBBS-project/architecture_portal.git
    git clone -b development https://github.com/DIBBS-project/central_authentication_service.git

    # sudo yum install -y python-pip

    sudo pip install -r central_authentication_service/requirements.txt
    sudo pip install -r operation_registry/requirements.txt
    sudo pip install -r operation_manager/requirements.txt
    sudo pip install -r appliance_registry/requirements.txt
    sudo pip install -r resource_manager/requirements.txt
    sudo pip install -r architecture_portal/requirements.txt

    CURRENT_PATH=$(pwd)
    echo $CURRENT_PATH

    ############################################################################
    # Install Central Authentication Service
    ############################################################################

    pushd central_authentication_service

    cat > configure_webservice.sh <<- EOM
#!/bin/bash

pushd $CURRENT_PATH/central_authentication_service
bash reset.sh
python manage.py runserver 0.0.0.0:7000

EOM

    screen $COMMON_SCREEN_ARGS -t central_authentication_service bash -c "bash $CURRENT_PATH/central_authentication_service/configure_webservice.sh; sleep 300"
    popd

    ############################################################################
    # Install Operation Registry
    ############################################################################

    pushd operation_registry

    cat > configure_webservice.sh <<- EOM
#!/bin/bash

pushd $CURRENT_PATH/operation_registry
bash reset.sh
python manage.py runserver 0.0.0.0:8000

EOM

    screen $COMMON_SCREEN_ARGS -t operation_registry bash $CURRENT_PATH/operation_registry/configure_webservice.sh
    popd

    ############################################################################
    # Install Operation Manager
    ############################################################################

    pushd operation_manager

    cat > configure_webservice.sh <<- EOM
#!/bin/bash

pushd $CURRENT_PATH/operation_manager
bash reset.sh
python manage.py runserver 0.0.0.0:8001

EOM

    screen $COMMON_SCREEN_ARGS -t operation_manager bash $CURRENT_PATH/operation_manager/configure_webservice.sh
    popd

    ############################################################################
    # Install Appliance Registry
    ############################################################################

    pushd appliance_registry

    cat > configure_webservice.sh <<- EOM
#!/bin/bash

pushd $CURRENT_PATH/appliance_registry
bash reset.sh
python manage.py runserver 0.0.0.0:8003

EOM

    screen $COMMON_SCREEN_ARGS -t appliance_registry bash -c "bash $CURRENT_PATH/appliance_registry/configure_webservice.sh; sleep 40"
    popd

    ############################################################################
    # Install Resource manager
    ############################################################################

    pushd resource_manager

    cat > configure_webservice.sh <<- EOM
#!/bin/bash

pushd $CURRENT_PATH/resource_manager
bash reset.sh
python manage.py runserver 0.0.0.0:8002

EOM

    screen $COMMON_SCREEN_ARGS -t resource_manager bash $CURRENT_PATH/resource_manager/configure_webservice.sh
    popd

    ############################################################################
    # Install Architecture Portal
    ############################################################################

    pushd architecture_portal

    cat > configure_webservice.sh <<- EOM
#!/bin/bash

pushd $CURRENT_PATH/architecture_portal
bash reset.sh
python manage.py runserver 0.0.0.0:8005

EOM

    screen $COMMON_SCREEN_ARGS -t architecture_portal bash $CURRENT_PATH/architecture_portal/configure_webservice.sh
    popd

    popd
}

install_and_configure_agents

exit 0
