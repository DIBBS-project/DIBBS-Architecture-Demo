FROM ubuntu:14.04
MAINTAINER Badock

# Download dependencies
RUN apt-get update
RUN apt-get install -y git python-setuptools python-dev build-essential python-pip
RUN apt-get install -y libffi-dev libssl-dev

# Clone projects
#   process_registry
RUN git clone -b development https://github.com/chardetm/process_registry.git
#   process_dispatcher
RUN git clone -b development https://github.com/chardetm/process_dispatcher.git
#   appliance_registry
RUN git clone -b development https://github.com/chardetm/appliance_registry.git
#   resource_manager
RUN git clone -b development https://github.com/chardetm/resource_provisioner.git
#   architecture_portal
RUN git clone -b master https://github.com/chardetm/architecture_portal.git

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install django==1.8.0 certifi>=14.05.14 six==1.8.0 python_dateutil>=2.5.3 setuptools>=21.0.0 urllib3>=1.15.1 pycrypto==2.6.1

# Install requirements
RUN pip install -r process_registry/requirements.txt
RUN pip install -r process_dispatcher/requirements.txt
RUN pip install -r appliance_registry/requirements.txt
RUN pip install -r resource_provisioner/requirements.txt
#RUN pip install -r architecture_portal/requirements.txt

