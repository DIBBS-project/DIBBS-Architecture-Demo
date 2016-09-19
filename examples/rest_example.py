#!/usr/bin/env python
import requests
from requests.auth import HTTPBasicAuth

appliance_registry_url = "http://127.0.0.1:8003"

# Create an API client for Appliances
result = requests.get("%s/appliances" % (appliance_registry_url,),
                      auth=HTTPBasicAuth('admin', 'pass'))

appliances = result.json()
for appliance in appliances:
    print appliance["name"]
