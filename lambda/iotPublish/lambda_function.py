import boto3
import json
from boto3.dynamodb.conditions import Key

REGION = 'us-east-1'
TOPIC = 'topic'
REQUEST = 'request'
KEY = 'key'
ACTIONS = 'actions'


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
    key = parameter_parser(event, KEY)
    if key:
        ddb = boto3.resource('dynamodb', region_name=REGION)
        table = ddb.Table('triggers')
        record = table.query(KeyConditionExpression=Key(KEY).eq(key))['Items']
        if len(record) > 0:
            if ACTIONS in record[0]:
                for act in record[0][ACTIONS]:
                    if TOPIC in act:
                        if REQUEST in act:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps(act[REQUEST]))
                        else:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps({}))
        return response({'key': key}, 200)

