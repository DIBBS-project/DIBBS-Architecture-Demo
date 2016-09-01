#!/usr/bin/env python

import sys
import getpass
import json
from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode
import requests
from requests.auth import HTTPBasicAuth

infrastructure_name = "KVMatTACC"

if __name__ == "__main__":
   """Create a user that is able to request Cloud Computing resources"""

   if len(sys.argv) < 3:
        print("python create_os_user.py <username> <project_name>")
        sys.exit(1)

   username = sys.argv[1]
   project_name = sys.argv[2]

   resource_manager_url = "http://127.0.0.1:8002"

   # Creating a new user if needed
   user_dict = {
        "username": username,
        "password": "foo",
        "project": project_name
   }
   r = requests.post("%s/users/" % (resource_manager_url), json=user_dict, auth=HTTPBasicAuth('admin', 'pass'))

   user_id = 1
   # if "id" in r.json():
   #      user_id = r.json()["id"]

   # Get the key of the current user
   r = requests.get("%s/rsa_public_key/%s/" % (resource_manager_url, user_id), auth=HTTPBasicAuth('admin', 'pass'))

   if r.status_code != 200:
      print("could not find the public key for user %s :(" % (user_id,))
      sys.exit(1)

   public_key_str = r.json()["public_key"]
   print("(0) => %s (%s)" % (public_key_str, hash(public_key_str)))
   key = RSA.importKey(public_key_str)

   # Upload new credentials for the new user
   password = getpass.getpass("please provide an OpenStack password for %s:" % (infrastructure_name,))
   credentials = {
        "username": username,
        "password": password,
        "project": project_name
   }
   uncrypted_json_credentials = "%s" % (json.dumps(credentials))

   public_key = RSA.importKey(public_key_str)
   enc_data = public_key.encrypt(uncrypted_json_credentials, 32)

   crypted_json_credentials_b64 = b64encode("%s" % (enc_data))

   # Upload the credentials to the resource_manager
   credentials_dict = {
        "credentials": crypted_json_credentials_b64,
        "site_name": infrastructure_name,
        "user": user_id
   }

   r = requests.post("%s/credentials/" % (resource_manager_url), json=credentials_dict, auth=HTTPBasicAuth('admin', 'pass'))

   print(r.status_code)
   print(r.json())

   sys.exit(0)

