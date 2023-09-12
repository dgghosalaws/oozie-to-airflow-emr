# -*- coding: utf-8 -*-
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3
import requests
import requests
import os

def detect_running_region():
    """Dynamically determine the region from a running MWAA Setup ."""
    easy_checks = [
        # check if set through ENV vars
        os.environ.get('AWS_REGION'),
        os.environ.get('AWS_DEFAULT_REGION'),
        # else check if set in config or in boto already
        boto3.DEFAULT_SESSION.region_name if boto3.DEFAULT_SESSION else None,
        boto3.Session().region_name,
    ]
    for region in easy_checks:
        if region:
            return region
    # else Assuming Airflow is running in an EC2 environment
    # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html
    r = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document")
    response_json = r.json()
    return response_json.get('region')

def get_region():
    return 'us-west-2'

def client(region_name):
    global ec2
    ec2 = boto3.client('ec2', region_name=region_name)

"""
 Identification process for a private subnet
    1. If no RouteTables - Its a public subnet with no Explicit subnet associations.
    2. If RouteTables present
        a. If NatGatewayId present , then its private Subnet
        b. If GatewayId contains "igw...", its public Subnet.
    Improve the detection as appropriate
"""
def validate_private_subnet(subnet_id):
    isPrivateSubnet: bool = True
    response = ec2.describe_route_tables(
        Filters=[
            {
                'Name': 'association.subnet-id',
                'Values': [
                    subnet_id,
                ]
            },
        ],
    )
    if not response["RouteTables"]:
        isPrivateSubnet = False
    else:
        for details in response["RouteTables"]:
            for attribute, value in details.items():
                if attribute=="Routes":
                    routes = value
            for entry in routes:
                for attribute, value in entry.items():
                    if attribute=="GatewayId":
                        if value.__contains__('igw'):
                            isPrivateSubnet=False
    return isPrivateSubnet
def main():
    print("Hello World!")
    region = detect_running_region()
    print(region)
    client(region_name=region)
    #pretty_json = json.dumps(config, indent=4)
    print(validate_private_subnet('subnet-0e58e167'))

if __name__ == "__main__":
    main()
