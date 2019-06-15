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
import builtins

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


def print(*args, **kwargs):
    """Custom print"""
    if 'color' in kwargs:
        _color = kwargs['color']
        del kwargs['color']
        if is_color_term() and _color:
            new_args = []
            for arg in args:
                new_args.append('{}{}{}'.format(color(_color), args[0], color('default')))
            args = tuple(new_args)
    return builtins.print(*args, **kwargs)


def color(c):
    """
    Returns ANSI color codes based on an input color name
    :param c: string color name
    :returns: string ANSI color code
    """
    c = c.lower()
    ansi = {
        'black': '\033[0;30m',
        'darkred': '\033[0;31m',
        'darkgreen': '\033[0;32m',
        'darkyellow': '\033[0;33m',
        'darkblue': '\033[0;34m',
        'darkmagenta': '\033[0;35m',
        'darkcyan': '\033[0;36m',
        'gray': '\033[0;37m',

        'darkgray': '\033[1;30m',
        'red': '\033[1;31m',
        'green': '\033[1;32m',
        'yellow': '\033[1;33m',
        'blue': '\033[1;34m',
        'magenta': '\033[1;35m',
        'cyan': '\033[1;36m',
        'white': '\033[1;37m',

        'blackbg': '\033[40m',
        'redbg': '\033[41m',
        'greenbg': '\033[42m',
        'yellowbg': '\033[43m',
        'bluebg': '\033[44m',
        'magentabg': '\033[45m',
        'cyanbg': '\033[46m',
        'whitebg': '\033[47m',

        'reset': '\033[0;0m',
        'bold': '\033[1m',
        'reverse': '\033[2m',
        'underline': '\033[4m',

        'clear': '\033[2J',
    #   'clearline': '\033[K',
        'clearline': '\033[2K',
    #   'save': '\033[s',
    #   'restore': '\033[u',
        'save': '\0337',
        'restore': '\0338',
        'linewrap': '\033[7h',
        'nolinewrap': '\033[7l',

        'up': '\033[1A',
        'down': '\033[1B',
        'right': '\033[1C',
        'left': '\033[1D',

        'default': '\033[0;0m',
    }
    if c.lower() == 'list':
        return ansi
    if c not in ansi:
        return ansi["default"]
    return ansi[c]


def is_color_term():
    """
    Checks if currnet TERM environment variable is allows color
    :returns: boolean True if color-allowed, otherwise False
    """
    terms = ('xterm', 'vt100', 'screen')
    TERM = os.environ.get('TERM', None)
    if not TERM:
        return False
    for term in terms:
        if TERM.startswith(term):
            return True
    return False


class CloudFormation(object):
    """
    Cloudformation class to handle the goodies.
    """
    def __init__(self, **kwargs):
        """
        Our constructor
        :param profile_name: string AWS Profile to use
        :param cf: CloudFormation resource object
        :param quiet: boolean No visible printout
        :param region_name: string AWS region name
        """
        self.profile_name = kwargs.get('profile_name', 'default')
        self.cf = kwargs.get('cf')
        self.quiet = kwargs.get('quiet')
        self.region_name = kwargs.get('region_name')

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

    def check_statuses(self):
        """
        Check the current status of the stacks being built
        """
        for _id in self.get_stacks():
            resource = self.cf.Stack(_id)
            yield (resource.stack_name, resource.stack_status)

    def stack_exists(self, name):
        """
        Checks if a stack exists.
        :param name: Stack name to check for
        :returns: boolean True if exists
        """
        for _name, _status in self.check_statuses():
            if _name == name:
                return True
        return False

    def create_stack(self, **kwargs):
        """
        Creates Cloudformation stack using the details provided.
        """
        stack_name = kwargs.get('stack_name')
        template_file = kwargs.get('template_file')
        if not self.quiet:
            print('Creating stack: ', end='')
            print('{}'.format(stack_name), color='green')
        shell_statement = 'aws --profile {} --region {} cloudformation create-stack --stack-name {} --template-body file://{} --capabilities=CAPABILITY_IAM'.format(self.profile_name, self.region_name, stack_name, template_file)
        if self.stack_exists(stack_name):
            print('Stack with the name {} already exists.  Current stacks:'.format(stack_name), color='red')
            for _name, _status in self.check_statuses():
                if _status == 'CREATE_COMPLETE':
                    color='green'
                else:
                    color='yellow'
                print('{:<25} {}'.format(_name, _status), color=color)
            sys.exit(1)

        try:
            results = subprocess.check_output(
                shlex.split(shell_statement),
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            print('An error ({}) occurred:'.format(e.returncode), color='red')
            print(e.output.decode())
            sys.exit(1)


def main():
    """
    Let's get ready to rumbllllllllllllllllllle!
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-t',
        '--stack_template',
        help='Create a cloudformation stack based on the provided template.'
    )
    parser.add_argument(
        '-n',
        '--stack_name',
        help='The name of the stack to create.  Must be unique.',
        action='append'
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

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config_file)

    root_dir = '/'.join(os.path.abspath(args.config_file).split('/')[:-2])

    aws_profile = config['main']['aws_profile']
    aws_region = config['main']['aws_region']

    aws = boto3.Session(profile_name=aws_profile)
    cf = aws.resource(
        'cloudformation',
        region_name=aws_region
    )
    c = CloudFormation(
        cf=cf,
        profile_name=aws_profile,
        region_name=aws_region
    )

    if args.stack_name:
        if not args.stack_template:
            print('Stack creation requires a template be specified.  (See --stack_template)', color='red')
            sys.exit(1)
        for stack_name in args.stack_name:
            c.create_stack(
                stack_name=stack_name,
                template_file=args.stack_template
            )


if __name__ == '__main__':
    main()
