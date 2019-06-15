#!/usr/bin/python3

import os
import sys
import boto3
import json
import datetime

"""
Upload a file to an S3 bucket.
"""

aws = boto3.Session(profile_name="ascheel")
s3 = aws.resource("s3", region_name="us-west-2")


def bucket_exists(name):
    """
    Does the bucket exist?
    :param name: Bucket name
    :returns: boolean True if exists, False if not exists
    """
    buckets = s3.meta.client.list_buckets()
    for bucket in buckets["Buckets"]:
        bucket_name = bucket["Name"]
        if bucket_name == name:
            return True
    return False


def get_target_filename(filename, bucket_name):
    """
    Change the filename so as to prevent overwriting.
    :param filename: Name of the file
    :param bucket_name: Name of the S3 bucket
    :returns: string new filename
    """
    filename = os.path.split(filename)[-1]
    bucket = s3.Bucket(bucket_name)
    base, ext = os.path.splitext(filename)
    target_filename = "{}_{}{}".format(base, datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"), ext)
    return target_filename


def main():
    """
    Our main routine
    """
    bucket_name = "ascheel-upload"
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: {} <filename> [bucket_name]")
        sys.exit(1)
    
    filename = sys.argv[1]

    if len(sys.argv) == 3:
        bucket_name = sys.argv[2]
    
    if not os.path.exists(filename):
        print("Input filename does not exist.")
        sys.exit(2)

    if not bucket_exists(bucket_name):
        print("Bucket does not exist.")
        sys.exit(3)

    target_filename = get_target_filename(filename, bucket_name)
    # target_filename = os.path.split(filename)[-1]

    bucket = s3.Bucket(bucket_name)
    with open(filename, "rb") as f:
        bucket.put_object(
            Body=f,
            Key=target_filename,
            ServerSideEncryption="AES256"
        )


if __name__ == '__main__':
    main()

