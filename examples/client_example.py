#!/usr/bin/env python
from common_dibbs.clients.ar_client import AppliancesApi
from common_dibbs.misc import configure_basic_authentication

appliance_registry_url = "http://127.0.0.1:8003"

# Create an API client for Appliances
appliances_client = AppliancesApi()
appliances_client.api_client.host = "%s" % (appliance_registry_url,)
configure_basic_authentication(appliances_client, "admin", "pass")

appliances = appliances_client.appliances_get()
for appliance in appliances:
    print appliance.name
