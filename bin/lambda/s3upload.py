import json
import boto3

def upload(event, context):
    print("event: {}".format(event))
    print("context: {}".format(context))
    status = {
        "statusCode": 200,
        "body": json.dumps("Hello from Lambda")
    }

if __name__ == '__main__':
    print("This is not the script you are looking for.")
