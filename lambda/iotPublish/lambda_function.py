import boto3
import json
from boto3.dynamodb.conditions import Key

REGION = 'us-east-1'


def lambda_handler(event, context):
    iot_data = boto3.client('iot-data', region_name=REGION)
    if 'topic' in event and 'request' in event:
        iot_data.publish(topic='{}'.format(event['topic']), qos=0, payload=json.dumps(event['request']))
    elif 'topic' in event:
        iot_data.publish(topic='{}'.format(event['topic']), qos=0, payload=json.dumps({}))
    elif 'id' in event:
        DDB = boto3.resource('dynamodb', region_name=REGION)
        table = DDB.Table('actions')
        record = table.query(KeyConditionExpression=Key('uuid').eq(event['id']))['Items']
        if len(record) == 1:
            if 'request' in record[0]:
                iot_data.publish(topic='{}'.format(record[0]['topic']), qos=0, payload=json.dumps(record[0]['request']))
            else:
                iot_data.publish(topic='{}'.format(record[0]['topic']), qos=0, payload=json.dumps({}))

