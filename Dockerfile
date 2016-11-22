FROM ubuntu:14.04
MAINTAINER Badock

# Download dependencies
RUN apt-get update
RUN apt-get install -y git python-setuptools python-dev build-essential python-pip
RUN apt-get install -y libffi-dev libssl-dev curl

# Clone projects
#   operation_registry
RUN git clone -b development https://github.com/DIBBS-project/operation_registry.git
#   operation_dispatcher
RUN git clone -b development https://github.com/DIBBS-project/operation_manager.git
#   appliance_registry
RUN git clone -b development https://github.com/DIBBS-project/appliance_registry.git
#   resource_manager
RUN git clone -b development https://github.com/DIBBS-project/resource_manager.git
#   architecture_portal
RUN git clone -b master https://github.com/DIBBS-project/architecture_portal.git
#   central_authentication
RUN git clone -b development https://github.com/DIBBS-project/central_authentication_service.git

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install django==1.8.0 certifi>=14.05.14 six==1.8.0 python_dateutil>=2.5.3 setuptools>=21.0.0 urllib3>=1.15.1 pycrypto==2.6.1 python-novaclient==3.3.0

# Install requirements
RUN pip install -r central_authentication_service/requirements.txt
RUN pip install -r operation_registry/requirements.txt
RUN pip install -r operation_manager/requirements.txt
RUN pip install -r appliance_registry/requirements.txt
RUN pip install -r resource_manager/requirements.txt
RUN pip install -r architecture_portal/requirements.txt

# WORKAROUND TO PUT THE PUBLIC IP IN A CONFIGURATION FILE (if needed)
RUN echo 'PUBLIC_IP=$(curl ipinfo.io/ip); if [[ "$PUBLIC_IP" == 129* ]] || [[ "$PUBLIC_IP" == 141* ]]; then mkdir -p /etc/dibbs/; echo "{\"address\": \"$PUBLIC_IP\"}" > /etc/dibbs/dibbs.json; fi;' > /etc/ip.sh
RUN chmod +x /etc/ip.sh; bash /etc/ip.sh
