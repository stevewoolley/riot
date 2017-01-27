import boto3

REGION = 'us-east-1'


def lambda_handler(event, context):
    iot = boto3.client('iot', region_name=REGION)
    response = iot.list_things()
    return response["things"]
