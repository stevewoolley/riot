import boto3
import json

REGION = 'us-east-1'


def response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
    }


def lambda_handler(event, context):
    iot = boto3.client('iot', region_name=REGION)
    return response(iot.list_things()["things"], 200)
