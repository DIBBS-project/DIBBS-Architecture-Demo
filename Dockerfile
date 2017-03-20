FROM python:3
MAINTAINER Nimbus Team

# this should get most of the packages the services want beforehand and cache
# them, so later pip installs are faster (COPY usually invalidates all later
# layers)
RUN pip install \
    'celery[redis]==4.0.2' \
    # 'certifi==2016.8.8' \
    'django>=1.11b1,<2.0' \
    # 'django-allauth==0.27.0' \
    # 'django-filter' \
    # 'django-jsonfield' \
    # 'django-states' \
    # 'django-sslserver' \
    'djangorestframework>=3.5,<3.6' \
    # 'jinja2' \
    'keystoneauth1==2.19.0' \
    # 'markdown' \
    # 'paramiko' \
    # 'pycrypto' \
    'pyjwt==1.4.2' \
    # 'python_dateutil>=2.5.3' \
    'python-heatclient==1.8.0' \
    'python-keystoneclient==3.10.0' \
    'python-novaclient==7.1.0' \
    'requests==2.12.5'
    # 'redis' \
    # 'six>=1.8.0' \
    # 'setuptools>=21.0.0' \
    # 'urllib3>=1.15.1'

# Copy projects
COPY repos /sources

# Install requirements
WORKDIR /sources
RUN pip install -e ./common-dibbs/
RUN pip install -r central_authentication_service/requirements.txt
# RUN pip install -r operation_registry/requirements.txt
# RUN pip install -r operation_manager/requirements.txt
RUN pip install -r appliance_registry/requirements.txt
RUN pip install -r resource_manager/requirements.txt
# RUN pip install -r architecture_portal/requirements.txt
