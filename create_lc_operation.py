#!/usr/bin/env python

import sys
import time
import uuid

import requests
from requests.auth import HTTPBasicAuth

if __name__ == "__main__":
    """Create an operation and run it, to demonstrate the architecture"""

    target_host = "141.142.170.178"
    # target_host = "127.0.0.1"

    operation_registry_url = "http://%s:8000" % (target_host)
    operation_manager_url = "http://%s:8001" % (target_host)
    resource_manager_url = "http://%s:8002" % (target_host)

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

    # Implementing the Operation based on the hadoop appliance.
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
        "force_spawn_cluster": "",
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

    # Wait for the execution to finish
    print(" - Waiting for the execution to finish")

    execution_has_finished = False
    current_status = None
    previous_status = ""
    while not execution_has_finished:
        r = requests.get("%s/executions/%s" % (operation_manager_url, execution_id),
                         auth=HTTPBasicAuth('admin', 'pass'))

        data = r.json()
        current_status = data["status"]

        if current_status != previous_status:
            print("   => %s" % (current_status))
            previous_status = current_status

        if current_status == "FINISHED":
            execution_has_finished = True

        if not execution_has_finished:
            time.sleep(2)

    # Download the output of the execution
    print(" - Download the output of the execution")
    r = requests.get("%s/executions/%s" % (operation_manager_url, execution_id),
                     auth=HTTPBasicAuth('admin', 'pass'))

    data = r.json()

    download_url = data["output_location"]
    if download_url is not None:
        r = requests.get(download_url, auth=HTTPBasicAuth('admin', 'pass'))

        # Write the downloaded file in a temporary file
        output_file_path = "/tmp/%s" % (uuid.uuid4())
        with open(output_file_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        print("   => output has been download in %s" % (output_file_path))

    sys.exit(0)
