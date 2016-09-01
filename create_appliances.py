#!/usr/bin/env python

import sys
import os
import re
import getpass
import json
from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode
import requests
from requests.auth import HTTPBasicAuth

# KVM@TACC
infrastructure_name = "KVMatTACC"
infrastructure_url = "https://openstack.tacc.chameleoncloud.org:5000/v2.0"

for i in range(0, len(argv))
   if argv[i] == "--run-on-roger":
     infrastructure_name = "KVMatRoger"
     infrastructure_url = "http://roger-openstack.ncsa.illinois.edu:5000/v2.0"

appliance_registry_url = "http://127.0.0.1:8003"
resource_manager_url = "http://127.0.0.1:8002"

#image_name = "CC-CENTOS-dibbs"
image_name = "CENTOS-7_HADOOP"

if __name__ == "__main__":
   """Create appliances to demonstrate the architecture"""

   # Creation of site
   site_dict = {
     "name": infrastructure_name,
     "type": "openstack",
     "contact_url": infrastructure_url
   }
   r = requests.post("%s/sites/" % (appliance_registry_url), json=site_dict, auth=HTTPBasicAuth('admin', 'pass'))
   print("- creation of site %s => %s %s" % (infrastructure_name, r.status_code, r.json() if r.status_code >= 400 else ""))

   skip_actions_creation = False
   if len(sys.argv) > 1:
      if sys.argv[1] == "skip":
         skip_actions_creation = True

   # If needed, create actions
   if not skip_actions_creation:
      actions = ["configure_node", "prepare_node", "update_master_node", "user_data", "update_hosts_file"]

      for action in actions:
         # Creating a new action
         action_dict = {
              "name": action
         }
         r = requests.post("%s/actions/" % (appliance_registry_url), json=action_dict, auth=HTTPBasicAuth('admin', 'pass'))
         print("- creation of action %s => %s %s" % (action, r.status_code, r.json() if r.status_code >= 400 else ""))

   # Create appliances
   for dirname, dirnames, filenames in os.walk("appliances"):
      # print path to all subdirectories first.
      for subdirname in dirnames:
         appliance_name = subdirname
         complete_path = os.path.join(dirname, subdirname)
         metadata_keys = ["description", "image", "image_name"]

         # Collect appliance metadata
         appliance_metadata = {
            "description": "",
            "image": "",
            "image_name": ""
         }
         for metadata_key in metadata_keys:
            metdata_file_address = "%s/%s.txt" % (complete_path, metadata_key)
            if os.path.isfile(metdata_file_address):
               with open(metdata_file_address) as f:
                  content = f.read()
                  appliance_metadata[metadata_key] = content

         # Create a new appliance
         appliance_dict = {
            "name": appliance_name,
            "logo_url": appliance_metadata["image"],
            "description": appliance_metadata["description"]
         }
         r = requests.post("%s/appliances/" % (appliance_registry_url), json=appliance_dict, auth=HTTPBasicAuth('admin', 'pass'))
         print("- creation of appliance %s => %s %s" % (appliance_name, r.status_code, r.json() if r.status_code >= 400 else ""))

         # Create an appliance implementation for the given site
         sites = [infrastructure_name]

         # Create an implementation of the appliance for each given site
         for site in sites:
            appliance_impl_name = "%s_%s" % (appliance_name, site) if appliance_name != "common" else "common"
            appliance_impl_logo_address = "%s/%s_image.txt" % (complete_path, appliance_impl_name)
            if os.path.isfile(appliance_impl_logo_address) or appliance_impl_name == "common":
               appliance_impl_dict = {
                  "name": appliance_impl_name,
                  "appliance": appliance_name,
                  "image_name": appliance_metadata["image_name"] if appliance_name != "common" else "n.a.",
                  "site": site,
                  "logo_url": appliance_impl_logo_address
               }
               r = requests.post("%s/appliances_impl/" % (appliance_registry_url), json=appliance_impl_dict, auth=HTTPBasicAuth('admin', 'pass'))
               print("  - creation of appliance_impl %s => %s %s" % (appliance_impl_name, r.status_code, r.json() if r.status_code >= 400 else ""))

               # Create an instance of each script for each appliance implementation
               for script_dirname, script_dirnames, script_filenames in os.walk("%s" % (complete_path)):
                  for script_filename in script_filenames:
                     script_file_address = "%s/%s" % (complete_path, script_filename)
                     if not ".jinja2" in script_file_address:
                        continue
                     with open(script_file_address) as script_f:
                        action_name = re.sub(r'.*/', '', re.sub(r'.jinja2', '', script_file_address))
                        print(action_name)
                        script_content = script_f.read()
                        script_dict = {
                           "code": script_content,
                           "appliance": appliance_impl_name if appliance_name != "common" else appliance_name,
                           "action": action_name
                        }
                        r = requests.post("%s/scripts/" % (appliance_registry_url), json=script_dict, auth=HTTPBasicAuth('admin', 'pass'))
                        print("    - creation of script_impl %s => %s %s" % (action_name, r.status_code, r.json() if r.status_code >= 400 else ""))
   sys.exit(0)

