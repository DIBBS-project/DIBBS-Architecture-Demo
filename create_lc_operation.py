#!/usr/bin/env python

import os
import re
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

# target_host = "129.114.111.75"
target_host = "127.0.0.1"
operation_registry_url = "http://%s:8000" % (target_host)
operation_manager_url = "http://%s:8001" % (target_host)
resource_manager_url = "http://%s:8002" % (target_host)

if __name__ == "__main__":
    """Create appliances to demonstrate the architecture"""

    print("- Building the line_counter example")

    # Creation of an Operation
    operation_dict = {
        "name": "LineCounter",
        "description": "A simple line counter that can be used to demonstrate the complete architecture.",
        "string_parameters": """["env_var", "parameter"]""",
        "logo_url": "http://dropbox.jonathanpastor.fr/dibbs/linecounter.png",
        "file_parameters": """["input_file"]"""
    }
    print(" - creating of the line_counter operation")
    r = requests.post("%s/operations/" % (operation_registry_url), json=operation_dict,
                      auth=HTTPBasicAuth('admin', 'pass'))
    operation = r.json()
    operation_id = r.json().get("id", 1)
    if r.status_code < 300:
        print("   OK")
    else:
        print("   ERROR")

    # Implementing the Operation based on Hadoop
    implementation_dict = {
        "name": "line_counter_hadoop",
        "appliance": "hadoop",
        "operation": operation_id,
        "cwd": "~",
        "script": "export ENV_VAR=!{env_var} ; curl http://dropbox.jonathanpastor.fr/archive.tgz > __archive.tar.gz ; tar -xzf __archive.tar.gz ; rm -f __archive.tar.gz ; bash run_job.sh @{input_file} !{parameter} > stdout 2> stderr",
        "output_type": "file",
        "output_parameters": """{"file_path": "output.txt"}"""
    }
    print(" - implementing of the line_counter operation => %s")
    r = requests.post("%s/operationversions/" % (operation_registry_url), json=implementation_dict,
                      auth=HTTPBasicAuth('admin', 'pass'))
    implementation = r.json()
    if r.status_code < 300:
        print("   OK")
    else:
        print("   ERROR")

    # Creating an instance of the Operation
    instance_dict = {
        "name": "line_counter_instance",
        "process_definition_id": operation_id,
        "parameters": """{"env_var": "plop","parameter": "parameter"}""",
        "files": """{"input_file": "http://dropbox.jonathanpastor.fr/input.txt"}"""
    }
    print(" - creating an instance of the line_counter operation")
    r = requests.post("%s/instances/" % (operation_manager_url), json=instance_dict,
                      auth=HTTPBasicAuth('admin', 'pass'))
    instance = r.json()
    instance_id = instance.get("id", 1)
    if r.status_code < 300:
        print("   OK")
    else:
        print("   ERROR")

    # Get a token from the resource manager
    get_token_dict = {
        "username": "admin",
        "password": "pass"
    }
    r = requests.post("%s/api-token-auth/" % (resource_manager_url), json=get_token_dict,
                      auth=HTTPBasicAuth('admin', 'pass'))
    resource_manager_token = r.json().get("token", "")
    print(" - getting a token from the resource manager => %s" % (r.status_code))
    if r.status_code < 300:
        print("   OK")
    else:
        print("   ERROR")

    # Prepare an execution of the previously created instance
    execution_dict = {
        "operation_instance": instance_id,
        "callback_url": "http://plop.org",
        "force_spawn_cluster": "False",
        "resource_provisioner_token": resource_manager_token ,
        "hints": """{"credentials": ["kvm@roger_dibbs"], "lease_id": ""}"""
    }
    print(" - preparing an execution of the line_counter operation")
    r = requests.post("%s/executions/" % (operation_manager_url), json=execution_dict,
                      auth=HTTPBasicAuth('admin', 'pass'))
    execution = r.json()
    execution_id = execution.get("id", 0)
    if r.status_code < 300:
        print("   OK")
    else:
        print("   ERROR")

    # Launch the execution of the operation instance
    print(" - launching the execution of the line_counter operation => %s" % (r.status_code))
    r = requests.get("%s/exec/%s/run" % (operation_manager_url, execution_id),
                      auth=HTTPBasicAuth('admin', 'pass'))
    if r.status_code < 300:
        print("   OK")
    else:
        print("   ERROR")


    sys.exit(0)
