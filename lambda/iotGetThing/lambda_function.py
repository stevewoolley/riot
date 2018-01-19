import boto3
import json

REGION = 'us-east-1'


def parameter_parser(evt, key):
    if key in evt:
        return evt[key]
    elif 'pathParameters' in evt and key in evt['pathParameters']:
        return evt['pathParameters'][key]
    elif 'queryStringParameters' in evt and key in evt['queryStringParameters']:
        return evt['queryStringParameters'][key]
    return None


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
    iot_data = boto3.client('iot-data', region_name=REGION)
    resp = iot_data.get_thing_shadow(thingName=parameter_parser(event, 'thingId'))
    body = resp['payload']
    j = json.loads(body.read())
    return response(j, 200)
