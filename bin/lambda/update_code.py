#!/usr/bin/python3

import boto3
import json
import subprocess
import shlex

"""
Updates the code in the lambda trigger.
"""

# Our resources
aws = boto3.Session(profile_name="ascheel")
lam = aws.client("lambda", region_name="us-west-2")

# Zip and upload our source code
cmd = "/home/arts/adobe/bin/upload"
results = subprocess.run(
    shlex.split(cmd),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
if results.returncode:
    print(results)
    exit(1)

# Submit to Lambda
with open("bin/lambda/lambda.zip", "rb") as f_in:
    results = lam.update_function_code(
        FunctionName="S3Trigger",
        ZipFile=f_in.read(),
        Publish=True
    )
    
