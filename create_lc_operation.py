#!/usr/bin/env python
"""Create an operation and run it, to demonstrate the architecture"""
from __future__ import absolute_import, print_function, unicode_literals

import argparse
import datetime
import json
from pprint import pprint
import sys
import time
import uuid

from dateutil.tz import tzlocal
import requests
from requests.auth import HTTPBasicAuth

import common_dibbs.auth as dibbs_auth


RESERVATION_ID = '975beddb-d577-4151-ba0b-548a8cca3253'


def check_response(response, dumpfile='response-dump.log'):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("   {}".format(str(e)))
        if dumpfile:
            with open(dumpfile, 'wb') as f:
                print("dumping response to '{}'...".format(dumpfile))
                f.write(response.content)
        raise
    else:
        print("   OK")


def create_operation(or_url, headers):
    # Creation of an Operation
    operation_dict = {
        "name": "LineCounter",
        "description": "A simple line counter that can be used to demonstrate the complete architecture.",
        "string_parameters": json.dumps(
            ["env_var", "parameter"]
        ),
        "logo_url": "https://raw.githubusercontent.com/DIBBS-project/DIBBS-Architecture-Demo/master/misc/dibbs/linecounter.png",
        "file_parameters": json.dumps(
            ["input_file"]
        ),
    }
    print(" - Creating the line_counter operation...", end="")
    r = requests.post(
        "{}/operations/".format(or_url),
        json=operation_dict,
        headers=headers,
    )
    print(r.status_code)
    check_response(r)
    operation = r.json()

    return operation


def create_implementation(or_url, headers, operation_id):
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
        "output_parameters": json.dumps(
            {"file_path": "output.txt"}
        ),
    }
    print(" - implementing of the line_counter operation... ", end="")
    r = requests.post(
        "{}/operationversions/".format(or_url),
        json=implementation_dict,
        headers=headers,
    )
    print(r.status_code)
    check_response(r)
    implementation = r.json()
    return implementation


def create_instance(om_url, headers, operation_id):
    # Creating an instance of the Operation
    instance_dict = {
        "name": "line_counter_instance",
        "process_definition_id": operation_id,
        "parameters": json.dumps({
            "env_var": "plop",
            "parameter": "parameter",
        }),
        "files": json.dumps({
            "input_file": "https://raw.githubusercontent.com/DIBBS-project/DIBBS-Architecture-Demo/master/misc/input.txt",
        }),
    }
    print(" - Creating an instance of the line_counter operation... ", end="")
    r = requests.post(
        "%s/instances/" % (om_url),
        json=instance_dict,
        headers=headers,
    )
    print(r.status_code)
    check_response(r)

    instance = r.json()
    return instance


def prepare_execution(om_url, headers, instance_id, hints):
    execution_dict = {
        "operation_instance": instance_id,
        "callback_url": "http://plop.org",
        "force_spawn_cluster": "",
        "hints": hints,
    }
    print(" - Preparing an execution of the line_counter operation")
    r = requests.post(
        "%s/executions/" % (om_url),
        json=execution_dict,
        headers=headers,
    )
    check_response(r)

    execution = r.json()
    return execution


def wait_for_execution(om_url, headers, execution_id):
    print(" - Waiting for the execution to finish")

    current_status = None
    previous_status = ""
    while True:
        r = requests.get(
            url="{}/executions/{}/".format(om_url, execution_id),
            headers=headers,
        )

        data = r.json()
        current_status = data["status"]

        if current_status != previous_status:
            now = datetime.datetime.now(tz=tzlocal())
            print(" ({})  => {}".format(now.strftime('%H:%M:%S'), current_status))
            previous_status = current_status

        if current_status == "FINISHED":
            return

        time.sleep(5)


def download_output(om_url, headers, execution_id):
    print(" - Download the output of the execution")
    r = requests.get(
        url="{}/executions/{}/".format(om_url, execution_id),
        headers=headers,
    )

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('action', choices=['deploy', 'run', 'both'])
    parser.add_argument('--run-on-roger',
        action='store_true', help='Run on Roger, rather than Chameleon')
    parser.add_argument('-H', '--host', type=str,
        help='DIBBs host address', default='127.0.0.1')
    parser.add_argument('-u', '--username', type=str,
        help='DIBBs username', default='alice')
    parser.add_argument('-p', '--password', type=str,
        help='Password for user. Defaults to uppercased username.')
    parser.add_argument('-i', '--instance-id', type=int,
        help='instance_id to use (needed if run-only)')

    args = parser.parse_args()

    cas_url = "http://%s:7000" % (args.host)
    or_url = "http://%s:8000" % (args.host)
    om_url = "http://%s:8001" % (args.host)
    # rm_url = "http://%s:8002" % (args.host)

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

    if args.run_on_roger:
        hints = """{"credentials": ["kvm@roger_dibbs"], "lease_id": ""}"""
    else:
        hints = """{{"credentials": ["chi@tacc_fg392"], "lease_id": "{}"}}""".format(RESERVATION_ID)

    do_deploy = args.action in {'both', 'deploy'}
    do_run = args.action in {'both', 'run'}

    if do_deploy:
        operation = create_operation(or_url, headers)
        implementation = create_implementation(or_url, headers, operation['id'])
        instance = create_instance(om_url, headers, operation['id'])

        print(' - Created instance:')
        pprint(instance) # so the user can call it later

    else:
        if args.instance_id is None:
            print("Must provide instance id", file=sys.stderr)
            return -1
        instance = {'id': args.instance_id}

    if do_run:
        execution = prepare_execution(om_url, headers, instance['id'], hints)

        # Wait for the execution to finish
        wait_for_execution(om_url, headers, execution['id'])

        # Download the output of the execution
        download_output(om_url, headers, execution['id'])


if __name__ == "__main__":
    sys.exit(main())
