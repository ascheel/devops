#!/usr/bin/env python3
"""
Deletes Cloudformation stacks.
How do you use it?  See -h argument on execution
"""

import sys
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
        self.region_name = kwargs.get('aws_region')
        self.aws_profile = kwargs.get('aws_profile')
        self.cf = kwargs.get('cf')
        self.quiet = kwargs.get('quiet')

    def delete_stack(self, stack_name, force):
        """
        Deletes Cloudformation stacks by name
        :param stack_name: String containing the stack's name
        :param force: boolean Removes prompts and just deletes.
        """
        if not force:
            print('Are you SURE you want to delete the stack named "{}"?'.format(stack_name))
            print('This is not a reversible process.  THIS CANNOT BE UNDONE.')
            answer = input('\nAre you sure? y/[N]: ')
            print()
            if answer.lower() != 'y':
                print('Cancelled.')
                sys.exit(1)
        self.cf.Stack(stack_name).delete()
        print('Done!')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-n',
        '--stack_name',
        help='The name of the stack to create.  Must be unique.',
        action='append',
        required=True
    )
    parser.add_argument(
        '-c',
        '--config_file',
        help='Configuration file to read from.',
        required=True
    )
    parser.add_argument(
        '-q',
        '--quiet',
        help='No output except errors.'
    )
    parser.add_argument(
        '-f',
        '--force',
        help='Suppress "Are you sure?" messages and assumes "Yes".  Use with caution.',
        action='store_true'
    )

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config_file)

    root_dir = '/'.join(os.path.abspath(args.config_file).split('/')[:-2])

    aws_region = config['main']['aws_region']
    aws_profile = config['main']['aws_profile']

    aws = boto3.Session(profile_name=aws_profile)
    cf = aws.resource('cloudformation',region_name=aws_region)
    c = CloudFormation(cf=cf)

    if args.stack_name:
        for stack_name in args.stack_name:
            c.delete_stack(stack_name, force=args.force)


if __name__ == '__main__':
    main()
