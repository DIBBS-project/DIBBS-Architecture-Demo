FROM ubuntu:16.04
MAINTAINER Badock

# Download dependencies
RUN apt-get update
RUN apt-get install -y \
    python-setuptools \
    python-dev \
    build-essential \
    python-pip \
    libffi-dev \
    libssl-dev \
    curl \
    redis-server

RUN systemctl disable redis-server
RUN pip install --upgrade pip

# this should get most of the packages the services want beforehand and cache
# them, so later pip installs are faster (COPY invalidates all later layers)
RUN pip install \
    'celery[redis]' \
    'certifi==2016.8.8' \
    'common-dibbs' \
    'django>=1.8,<1.9' \
    'django-allauth==0.27.0' \
    'django-cas-client==1.2.0' \
    'django-filter' \
    'django-jsonfield' \
    'django-periodically' \
    'django-states' \
    'django-secure' \
    'django-sslserver' \
    'djangorestframework>=3.5,<3.6' \
    'jinja2' \
    'keystoneauth1' \
    'markdown' \
    'paramiko' \
    'pycrypto' \
    'python_dateutil>=2.5.3' \
    'python-heatclient' \
    'python-keystoneclient' \
    # newer novaclients don't work; 401s where this works fine.
    'python-novaclient==3.3.0' \
    'redis' \
    'six>=1.8.0' \
    'setuptools>=21.0.0' \
    'urllib3>=1.15.1'

# Copy projects
COPY repos /sources

# Install requirements
WORKDIR /sources
RUN pip install -r central_authentication_service/requirements.txt
RUN pip install -r operation_registry/requirements.txt
RUN pip install -r operation_manager/requirements.txt
RUN pip install -r appliance_registry/requirements.txt
RUN pip install -r resource_manager/requirements.txt
RUN pip install -r architecture_portal/requirements.txt

# WORKAROUND TO PUT THE PUBLIC IP IN A CONFIGURATION FILE (if needed)
RUN echo 'PUBLIC_IP=$(curl ipinfo.io/ip); if [[ "$PUBLIC_IP" == 129* ]] || [[ "$PUBLIC_IP" == 141* ]]; then mkdir -p /etc/dibbs/; echo "{\"address\": \"$PUBLIC_IP\"}" > /etc/dibbs/dibbs.json; fi;' > /etc/ip.sh
RUN chmod +x /etc/ip.sh; bash /etc/ip.sh
