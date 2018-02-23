import boto3
import json
from boto3.dynamodb.conditions import Key
import logging

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
    elif 'queryStringParameters' in evt and evt['queryStringParameters'] is not None and key in evt[
        'queryStringParameters']:
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
    serial_number = parameter_parser(event, 'serialNumber')
    click_type = parameter_parser(event, 'clickType')
    if key or (serial_number and click_type):
        ddb = boto3.resource('dynamodb', region_name=REGION)
        table = ddb.Table('triggers')
        search_key = ''
        if key:
            search_key = key
        else:
            # format search key for IoT Button
            search_key = '{}_{}'.format(click_type, serial_number)
        record = table.query(KeyConditionExpression=Key(KEY).eq(search_key))['Items']
        if len(record) > 0:
            if ACTIONS in record[0]:
                for act in record[0][ACTIONS]:
                    if TOPIC in act:
                        if REQUEST in act:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps(act[REQUEST]))
                            print('published topic: {}'.format(act[TOPIC]))
                            print('published request: {}'.format(act[REQUEST]))
                        else:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps({}))
                            print('published topic: {}'.format(act[TOPIC]))
                    else:
                        logging.warning('{} not found in triggers table'.format(TOPIC))
                return response({'key': key}, 200)
            else:
                logging.warning('{} not found in trigger record'.format(ACTIONS))
        else:
            logging.warning('{} parameter not found in {}'.format(search_key, event))

    else:
        logging.warning('{} parameter not found in {}'.format(KEY, event))
