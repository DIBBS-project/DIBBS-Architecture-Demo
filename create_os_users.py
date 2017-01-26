#!/usr/bin/env python

import argparse
import base64
import getpass
import json
import sys

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

import requests
from requests.auth import HTTPBasicAuth

import common_dibbs.auth as dibbs_auth


USERNAME = 'alice'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('configuration_file', type=str)
    parser.add_argument('-H', '--host', type=str, default='127.0.0.1',
        help='Resource manager host')
    parser.add_argument('-p', '--port', type=int, default=8002,
        help='Resource manager port')

    args = parser.parse_args()

    configuration_file_path = args.configuration_file
    target_host = args.host
    resource_manager_url = 'http://{}:{}'.format(target_host, args.port)

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
        #     headers=dibbs_auth.client_auth_headers(USERNAME),
        # )

        # Get the key of the current user
        r = requests.get(
            "{}/rsa_public_key/{}".format(resource_manager_url, USERNAME),
            headers=dibbs_auth.client_auth_headers(USERNAME),
        )

        if r.status_code != 200:
            print("could not retrieve the public key for user %s :(" % (user_id,))
            print('HTTP {}'.format(r.status_code))
            print(r.content[:1000])
            return 1

        public_key_str = r.json()["public_key"]
        print("(0) => %s (%s)" % (public_key_str, hash(public_key_str)))
        public_key = RSA.importKey(public_key_str)

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
                "user": USERNAME,
            },
            headers=dibbs_auth.client_auth_headers(USERNAME),
        )

        print(r.status_code)
        print(r.json())


if __name__ == "__main__":
    sys.exit(main())
