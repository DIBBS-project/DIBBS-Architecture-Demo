#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import json
import os
import re
import sys

import requests

# target_host = "141.142.170.178"
target_host = "127.0.0.1"

appliance_registry_url = "http://%s:8003" % (target_host)
resource_manager_url = "http://%s:8002" % (target_host)
cas_url = "http://%s:7000" % (target_host)

image_name = "CENTOS-7_HADOOP"

def main(argv=None):
    """Create appliances to demonstrate the architecture"""
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('config_file', type=str)
    parser.add_argument('-u', '--username', type=str,
        help='DIBBs Username', default='alice')
    parser.add_argument('-p', '--password', type=str,
        help='Password for user. Defaults to uppercased username.')

    args = parser.parse_args(argv[1:])

    with open(args.config_file) as data_file:
        infrastructures = json.load(data_file)["infrastructures"]

    username = args.username
    password = username.upper() if args.password is None else args.password

    auth_response = requests.post(
        '{}/auth/tokens'.format(cas_url),
        json={'username': username, 'password': password},
    )
    if auth_response.status_code != 200:
        print(auth_response.text, file=sys.stderr)
        return -1
    auth_data = auth_response.json()
    headers = {'Dibbs-Authorization': auth_data['token']}

    for infrastructure in infrastructures:
        infrastructure_name = infrastructure["name"]
        infrastructure_url = infrastructure["contact_url"]
        infrastructure_type = infrastructure["type"]

        # Creation of site
        site_dict = {
            "name": infrastructure_name,
            "type": infrastructure_type,
            "contact_url": infrastructure_url
        }
        r = requests.post(
            "{}/sites/".format(appliance_registry_url),
            json=site_dict,
            headers=headers,
        )
        print(
            "- creation of site %s => %s %s" % (
                infrastructure_name, r.status_code, r.json() if r.status_code >= 400 else ""))

        skip_actions_creation = False
        if len(argv) > 1:
            if argv[1] == "skip":
                skip_actions_creation = True

        # If needed, create actions
        if not skip_actions_creation:
            actions = ["configure_node", "prepare_node", "update_master_node", "user_data", "update_hosts_file", "heat_template"]

            for action in actions:
                # Creating a new action
                action_dict = {
                    "name": action
                }
                r = requests.post(
                    "{}/actions/".format(appliance_registry_url),
                    json=action_dict,
                    headers=headers,
                )
                print(
                    "- creation of action %s => %s %s" % (
                        action, r.status_code, r.json() if r.status_code >= 400 else ""))

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

                r = requests.post(
                    "{}/appliances/".format(appliance_registry_url),
                    json=appliance_dict,
                    headers=headers,
                )
                print("- creation of appliance %s => %s %s" % (
                    appliance_name, r.status_code, r.json() if r.status_code >= 400 else ""))

                # Create an appliance implementation for the given site
                sites = [infrastructure_name]

                # Create an implementation of the appliance for each given site
                for site in sites:
                    appliance_impl_name = "%s_%s" % (
                        appliance_name, site) if appliance_name != "common" else "common"
                    appliance_impl_logo_address = "%s/%s_image.txt" % (complete_path, appliance_impl_name)
                    # if os.path.isfile(appliance_impl_logo_address) or appliance_impl_name == "common":
                    appliance_impl_dict = {
                        "name": appliance_impl_name,
                        "appliance": appliance_name,
                        "image_name": appliance_metadata["image_name"] if appliance_name != "common" else "n.a.",
                        "site": site,
                        "logo_url": appliance_impl_logo_address
                    }
                    r = requests.post(
                        "{}/appliances_impl/".format(appliance_registry_url),
                        json=appliance_impl_dict,
                        headers=headers,
                    )
                    print("  - creation of appliance_impl %s => %s %s" % (
                        appliance_impl_name, r.status_code, r.json() if r.status_code >= 400 else ""))

                    # Create an instance of each script for each appliance implementation
                    for script_dirname, script_dirnames, script_filenames in os.walk("%s" % (complete_path)):
                        for script_filename in script_filenames:
                            script_file_address = "%s/%s" % (complete_path, script_filename)
                            if not "heat_template.jinja2" in script_file_address:
                                continue
                            with open(script_file_address) as script_f:
                                script_content = script_f.read()
                            action_name = re.sub(r'.*/', '', re.sub(r'.jinja2', '', script_file_address))
                            print(action_name)
                            script_dict = {
                                "code": script_content,
                                "appliance": appliance_impl_name if appliance_name != "common" else appliance_name,
                                "action": action_name
                            }
                            r = requests.post(
                                "{}/scripts/".format(appliance_registry_url),
                                json=script_dict,
                                headers=headers,
                            )
                            print("    - creation of script_impl %s => %s %s" % (
                                action_name, r.status_code, r.json() if r.status_code >= 400 else ""))
    return 0

if __name__ == "__main__":
    sys.exit(main())
