import boto3
import time
import calendar
import json
import urllib.parse
import calendar
import time

"""
Trigger code for AWS S3 bucket uploads.  This code lives
in lambda and gets kicked off any time there is a ObjectCreate event.
"""

def get_adobe_topic(sns):
    """
    Retrieves the topic named "AdobeDevopsExerciseTopic".
    In the long term, probably more appropriate to use tags.
    :param sns: Pre-defined SNS Client object from boto3
    :returns: string SNS Topic ARN
    """
    # list_topics() has a limit of 100 per poll, so may need to create a waiter if there are >100 SNS Topics

    topics = sns.meta.client.list_topics()
    for topic in topics["Topics"]:
        arn = topic["TopicArn"]
        t = sns.Topic(arn)
        if t.attributes["DisplayName"] == "AdobeDevopsExerciseTopic":
            return arn


def is_text(content):
    """
    Uses the bytes.decode() method to determine if the file
    is text.  This will handle small files just fine. If files megabytes in size,
    then you'll want to refactor this to iterate over the file instead of reading
    it all into memory.
    :param content: The content of the file that was uploaded.
    :returns: boolean True if text, False if binary
    """
    try:
        content.decode()
        return True
    except:
        return False
    return None


def lambda_function(event, context):
    """
    The actual lambda function that triggers on CreateObject
    :param event: Contains details of the event, including file affected.
    :param context: No idear
    :returns: Nothing
    """

    # Our resources
    s3 = boto3.resource("s3")
    sns = boto3.resource("sns")
    dynamodb = boto3.resource("dynamodb")
    
    ####################################################################
    # This is our S3 section
    ####################################################################
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])

    # Our file object
    obj = s3.Object(bucket_name, key)

    # The file's contents
    content = obj.get()["Body"].read()
    lines = -1
    if is_text(content):
        # It's a text file
        lines = len(content.decode().split("\n"))

    ####################################################################
    # Gather our information
    ####################################################################
    # bucket name = bucket_name
    filename = key
    filesize = obj.content_length
    filelines = lines if is_text(content) else "(binary file)"
    fileepoch = calendar.timegm(time.gmtime())
    one_day = 60 * 60 * 24
    ttl = fileepoch + one_day

    ####################################################################
    # This is our SNS section
    ####################################################################
    message = []
    message.append("A file has been uploaded to Amazon S3.")
    message.append("Bucket:   {}".format(bucket_name))
    message.append("Filename: {}".format(filename))
    message.append("Lines:    {}".format(filelines))
    message.append("Epoch:    {}".format(fileepoch))
    message.append("TTL:      {}".format(ttl))
    
    message_joined = "\n".join(message)
    
    # Send it
    topic = sns.Topic(get_adobe_topic(sns))
    topic.publish(Message=message_joined, Subject="New file upload to {}".format(bucket_name))

    ####################################################################
    # This is our DynamoDB section
    ####################################################################
    # Store it    
    item = {
        "Filename": filename,
        "Bucket": bucket_name,
        "Lines": filelines,
        "Size": filesize,
        "TimeToLive": ttl
    }
    table = dynamodb.Table("Files")
    results = table.put_item(
        Item=item
    )


