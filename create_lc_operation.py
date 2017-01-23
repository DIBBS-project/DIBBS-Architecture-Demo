#!/usr/bin/env python

import datetime
import json
import sys
import time
import uuid

from dateutil.tz import tzlocal
import requests
from requests.auth import HTTPBasicAuth

RESERVATION_ID = '85f97018-f1a1-423e-81c6-2e71e7488fef'
DIBBS_USER = 'grace'

DIBBS_USER_HEADER = {b'Dibbs-Thing': json.dumps({'user': DIBBS_USER})}


def check_response(response, dumpfile='response-dump.log'):
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("   {}".format(str(e)))
        if dumpfile:
            with open(dumpfile, 'wb') as f:
                print("dumping response to '{}'...".format(dumpfile))
                f.write(r.response)
        raise
    else:
        print("   OK")


if __name__ == "__main__":
    """Create an operation and run it, to demonstrate the architecture"""

    # target_host = "141.142.170.178"
    target_host = "127.0.0.1"

    operation_registry_url = "http://%s:8000" % (target_host)
    operation_manager_url = "http://%s:8001" % (target_host)
    resource_manager_url = "http://%s:8002" % (target_host)

    print("- Building the line_counter example")

    # Creation of an Operation
    operation_dict = {
        "name": "LineCounter",
        "description": "A simple line counter that can be used to demonstrate the complete architecture.",
        "string_parameters": """["env_var", "parameter"]""",
        "logo_url": "https://raw.githubusercontent.com/DIBBS-project/DIBBS-Architecture-Demo/master/misc/dibbs/linecounter.png",
        "file_parameters": """["input_file"]"""
    }
    print(" - creating of the line_counter operation")
    r = requests.post(
        "%s/operations/" % (operation_registry_url),
        json=operation_dict,
        auth=HTTPBasicAuth('admin', 'pass'),
        headers=DIBBS_USER_HEADER,
    )
    operation = r.json()
    operation_id = r.json().get("id", 1)
    check_response(r)

    # Implementing the Operation based on the hadoop appliance.
    implementation_dict = {
        "name": "line_counter_hadoop",
        "appliance": "hadoop",
        "operation": operation_id,
        "cwd": "~",
        "script": r"export ENV_VAR=!{env_var} ; "
                  r"curl https://raw.githubusercontent.com/DIBBS-project/DIBBS-Architecture-Demo/master/misc/archive.tgz > __archive.tar.gz ; "
                  r"tar -xzf __archive.tar.gz ; "
                  r"rm -f __archive.tar.gz ; "
                  r"bash run_job.sh @{input_file} !{parameter} > stdout 2> stderr",
        "output_type": "file",
        "output_parameters": """{"file_path": "output.txt"}"""
    }
    print(" - implementing of the line_counter operation => %s")
    r = requests.post(
        "%s/operationversions/" % (operation_registry_url),
        json=implementation_dict,
        auth=HTTPBasicAuth('admin', 'pass'),
        headers=DIBBS_USER_HEADER,
    )
    implementation = r.json()
    check_response(r)

    # Creating an instance of the Operation
    instance_dict = {
        "name": "line_counter_instance",
        "process_definition_id": operation_id,
        "parameters": """{"env_var": "plop","parameter": "parameter"}""",
        "files": """{"input_file": "https://raw.githubusercontent.com/DIBBS-project/DIBBS-Architecture-Demo/master/misc/input.txt"}"""
    }
    print(" - creating an instance of the line_counter operation")
    r = requests.post(
        "%s/instances/" % (operation_manager_url),
        json=instance_dict,
        auth=HTTPBasicAuth('admin', 'pass'),
        headers=DIBBS_USER_HEADER,
    )
    instance = r.json()
    instance_id = instance.get("id", 1)
    check_response(r)

    if len(sys.argv) > 1 and sys.argv[1] == '--run-on-roger':
        hints = """{"credentials": ["kvm@roger_dibbs"], "lease_id": ""}"""
    else:
        hints = """{{"credentials": ["chi@tacc_fg392"], "lease_id": "{}"}}""".format(RESERVATION_ID)

    # Prepare an execution of the previously created instance
    execution_dict = {
        "operation_instance": instance_id,
        "callback_url": "http://plop.org",
        "force_spawn_cluster": "",
        "hints": hints
    }
    print(" - preparing an execution of the line_counter operation")
    r = requests.post(
        "%s/executions/" % (operation_manager_url),
        json=execution_dict,
        auth=HTTPBasicAuth('admin', 'pass'),
        headers=DIBBS_USER_HEADER,
    )
    execution = r.json()
    execution_id = execution.get("id", 0)
    check_response(r)

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
            now = datetime.datetime.now(tz=tzlocal())
            print(" ({})  => {}".format(now.strftime('%H:%M:%S'), current_status))
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

        print("   => output has been downloaded in %s" % (output_file_path))

    sys.exit(0)
