#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import base64
import getpass
import json
import sys

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

import requests

# import common_dibbs.auth as dibbs_auth


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser()

    parser.add_argument('configuration_file', type=str)
    parser.add_argument('-H', '--host', type=str, default='127.0.0.1',
        help='Resource manager host')
    parser.add_argument('-P', '--port', type=int, default=8002,
        help='Resource manager port')
    parser.add_argument('-u', '--username', type=str,
        help='DIBBs Username', default='alice')
    parser.add_argument('-p', '--password', type=str,
        help='Password for user. Defaults to uppercased username.')

    args = parser.parse_args(argv[1:])

    configuration_file_path = args.configuration_file
    target_host = args.host
    resource_manager_url = 'http://{}:{}'.format(target_host, args.port)
    cas_url = 'http://{}:7000'.format(target_host)

    dibbs_username = args.username
    dibbs_password = dibbs_username.upper() if args.password is None else args.password

    auth_response = requests.post(
        '{}/auth/tokens'.format(cas_url),
        json={'username': dibbs_username, 'password': dibbs_password},
    )
    if auth_response.status_code != 200:
        print(auth_response.text, file=sys.stderr)
        return -1
    auth_data = auth_response.json()
    headers = {'Dibbs-Authorization': auth_data['token']}

    with open(configuration_file_path) as data_file:
        credentials = json.load(data_file)["credentials"]

    for credential in credentials:
        print(credential)

        username = credential["username"]
        project_name = credential["project_name"]
        infrastructure_name = credential["infrastructure"]
        credential_name = credential["name"]
        password = getpass.getpass(
            "Please provide the OpenStack password for ({}, {})@{}:".format(
                username, project_name, infrastructure_name
        ))

        # Creating a new user if needed
        # user_dict = {
        #     "username": username,
        #     "password": "foo",
        #     "project": project_name
        # }
        # r = requests.post(
        #     url="{}/users/".format(resource_manager_url),
        #     json=user_dict,
        #     headers=dibbs_auth.client_auth_headers(dibbs_username),
        # )

        # Get the key of the current user
        r = requests.get(
            "{}/rsa_public_key/{}".format(resource_manager_url, dibbs_username),
            headers=headers,
        )

        if r.status_code != 200:
            print("could not retrieve the public key for user '{}' :(".format(dibbs_username))
            print('HTTP {}'.format(r.status_code))
            print(r.content[:1000])
            return 1

        public_key_str = r.json()["public_key"]
        public_key = RSA.importKey(public_key_str)

        print("Storing credentials using below key:")
        print(public_key_str)

        # Upload new credentials for the new user
        credentials = {
            "username": username,
            "password": password,
            "project": project_name
        }
        message = json.dumps(credentials).encode('utf-8')
        cipher = PKCS1_OAEP.new(public_key)
        cipher_text = cipher.encrypt(message)

        cipher_text_b64 = base64.b64encode(cipher_text)

        # Upload the credentials to the resource_manager

        r = requests.post(
            "{}/credentials/".format(resource_manager_url),
            json={
                "credentials": cipher_text_b64,
                "site_name": infrastructure_name,
                "name": credential_name,
                "user": dibbs_username,
            },
            headers=headers,
        )

        print(r.status_code)
        print(r.json())


if __name__ == "__main__":
    sys.exit(main())
