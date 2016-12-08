#!/usr/bin/env python

import getpass
import json
import sys
from base64 import b64encode

import requests
from Crypto.PublicKey import RSA
from requests.auth import HTTPBasicAuth

# target_host = "141.142.170.178"
target_host = "127.0.0.1"

resource_manager_url = "http://%s:8002" % (target_host)

if __name__ == "__main__":

    configuration_file_path = None
    if len(sys.argv) > 1:
        configuration_file_path = sys.argv[1]

    if configuration_file_path is None:
        print("No configuration file passed as a parameter :-(")
        sys.exit(1)

    with open(configuration_file_path) as data_file:
        credentials = json.load(data_file)["credentials"]
        for credential in credentials:
            print(credential)

            username = credential["username"]
            project_name = credential["project_name"]
            infrastructure_name = credential["infrastructure"]
            credential_name = credential["name"]

            # Creating a new user if needed
            user_dict = {
                "username": username,
                "password": "foo",
                "project": project_name
            }
            r = requests.post("%s/users/" % (resource_manager_url), json=user_dict, auth=HTTPBasicAuth('admin', 'pass'))

            user_id = 1

            # Get the key of the current user
            r = requests.get("%s/rsa_public_key/%s/" % (resource_manager_url, user_id),
                             auth=HTTPBasicAuth('admin', 'pass'))

            if r.status_code != 200:
                print("could not find the public key for user %s :(" % (user_id,))
                sys.exit(1)

            public_key_str = r.json()["public_key"]
            print("(0) => %s (%s)" % (public_key_str, hash(public_key_str)))
            key = RSA.importKey(public_key_str)

            # Upload new credentials for the new user
            password = getpass.getpass("please provide an OpenStack password for (%s, %s)@%s:" % (
                                        username, project_name, infrastructure_name,))
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
                "name": credential_name,
                "user": user_id
            }

            r = requests.post("%s/credentials/" % (resource_manager_url), json=credentials_dict,
                              auth=HTTPBasicAuth('admin', 'pass'))

            print(r.status_code)
            print(r.json())

    sys.exit(0)
