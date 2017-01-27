import boto3
import json

REGION = 'us-east-1'
SENSORS_PAYLOAD = 'payload'


def lambda_handler(event, context):
    iot_data = boto3.client('iot-data', region_name=REGION)
    response = iot_data.get_thing_shadow(thingName=event['thing'])
    body = response[SENSORS_PAYLOAD]
    return json.loads(body.read())
