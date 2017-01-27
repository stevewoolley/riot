import boto3
import json

REGION = 'us-east-1'


def lambda_handler(event, context):
    iot_data = boto3.client('iot-data', region_name=REGION)
    iot_data.publish(topic='/{}'.format(event['topic'].replace('.', '/')), qos=0, payload=json.dumps(event['request']))
