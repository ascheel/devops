#!/usr/bin/env python3
"""
Creates Cloudformation stacks.
How do you use it?  See -h argument on execution
"""

import sys
PY2 = sys.version[0] == '2'
PY3 = sys.version[0] == '3'

if not PY3:
    print('Python3 required.  Exiting.')
    sys.exit(1)

import boto3
import os
import argparse
import copy
import datetime
import json
import time
import configparser
import subprocess
import shlex

stack_status_values = (
    'CREATE_COMPLETE',
    'CREATE_IN_PROGRESS',
    'CREATE_FAILED',
    'DELETE_COMPLETE',
    'DELETE_FAILED',
    'DELETE_IN_PROGRESS',
    'REVIEW_IN_PROGRESS',
    'ROLLBACK_COMPLETE',
    'ROLLBACK_FAILED',
    'ROLLBACK_IN_PROGRESS',
    'UPDATE_COMPLETE',
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
    'UPDATE_IN_PROGRESS',
    'UPDATE_ROLLBACK_COMPLETE',
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
    'UPDATE_ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_IN_PROGRESS'
)

class CloudFormation(object):
    """
    Cloudformation class to handle the goodies.
    """
    def __init__(self, **kwargs):
        self.cf = kwargs.get('cf')

    def get_stacks(self):
        """
        Gives us the Stack names for each cloudformation stack.
        Later on, may need to qualify them based on a tag.  For now, unnecessary.
        """
        results = self.cf.meta.client.describe_stacks()
        for stack in results['Stacks']:
            yield stack['StackName']
    
    def get_stack_output(self, obj, output_id):
        """
        Gets the output value of an output_id
        :param obj: The stack description to pick apart
        :param output_id: The output id you want the output for
        :returns: string output value
        """
        outputs = obj.outputs
        for output in outputs:
            if output['OutputKey'] == output_id:
                return output['OutputValue']
        return None

    def get_private_ip(self, _id):
        """
        Get the private IP of a stack based on stack Name/ID
        :param _id: The Stack's Name/ID
        :returns: string, private IP address
        """
        resource = self.cf.Stack(_id)
        if resource.stack_status == 'CREATE_COMPLETE':
            return self.get_stack_output(resource, 'PrivateIp')
    
    def wait_for_stacks(self):
        """
        Wait for all stacks to come back as completed or failed.
        """
        while True:
            waiting = False
            for _id in self.get_stacks():
                resource = self.cf.Stack(_id)
                if resource.stack_status == 'CREATE_IN_PROGRESS':
                    waiting = True
            if not waiting:
                return
            time.sleep(5)
    
    def get_private_ip(self, _id):
        """
        Get the private IP of a stack based on stack Name/ID
        :param _id: The Stack's Name/ID
        :returns: string, private IP address
        """
        resource = self.cf.Stack(_id)
        return self.get_stack_output(resource, 'PrivateIp')

    def get_all_private_ips(self):
        """
        Retrieves all private IPs for all stacks.  Generator.
        """
        for _id in self.get_stacks():
            resource = self.cf.Stack(_id)
            yield self.get_private_ip(_id)

    def check_statuses(self):
        """
        Check the current status of the stacks being built
        """
        for _id in self.get_stacks():
            resource = self.cf.Stack(_id)
            yield (resource.stack_name, resource.stack_status)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l',
        '--list_ips',
        help='list all IPs in the format: 1.1.1.1 2.2.2.2 3.3.3.3',
        action='store_true'
    )

    args = parser.parse_args()

    aws_region = "us-west-2"
    aws_profile = "ascheel"

    aws = boto3.Session(profile_name=aws_profile)
    cf = aws.resource(
        'cloudformation',
        region_name=aws_region
    )
    c = CloudFormation(cf=cf)

    c.wait_for_stacks()

    if args.list_ips:
        print(' '.join([_ for _ in c.get_all_private_ips()]), end='')
        sys.exit(0)
    for name, status in c.check_statuses():
        print('{} {}'.format(name, status))

if __name__ == '__main__':
    main()
