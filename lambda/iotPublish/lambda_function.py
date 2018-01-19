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
    topic = parameter_parser(event, TOPIC)
    request = parameter_parser(event, REQUEST)
    key = parameter_parser(event, KEY)
    if topic and request:
        iot_data.publish(topic='{}'.format(topic), qos=0, payload=json.dumps(request))
        return response({'topic': topic, 'request': json.dumps(request)}, 200)
    elif topic:
        iot_data.publish(topic='{}'.format(topic), qos=0, payload=json.dumps({}))
        return response({'topic': topic}, 200)
    elif key:
        ddb = boto3.resource('dynamodb', region_name=REGION)
        table = ddb.Table('triggers')
        record = table.query(KeyConditionExpression=Key(KEY).eq(key))['Items']
        if len(record) > 0:
            if ACTIONS in record[0]:
                for act in record[0][ACTIONS]:
                    if TOPIC in act:
                        if REQUEST in act:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps(act[REQUEST]))
                            return response({'topic': act[TOPIC], 'request': act[REQUEST]}, 200)
                        else:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps({}))
                            return response({'topic': act[TOPIC]}, 200)
