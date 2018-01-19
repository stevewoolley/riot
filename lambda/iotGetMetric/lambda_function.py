import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
from decimal import Decimal

REGION = 'us-east-1'
ITEMS = 'Items'
SENSORS_TABLE = 'sensors'
SENSORS_PARTITION_KEY = 'source'
SENSORS_SORT_KEY = 'timestamp'
SENSORS_PAYLOAD = 'payload'
PAYLOAD_PREFIX = 'payload.state.reported.{}'
SCAN_INDEX_FORWARD = False


class FakeFloat(float):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return str(self._value)


def default_encode(o):
    if isinstance(o, Decimal):
        # Subclass float with custom repr?
        return FakeFloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")


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
        'body': json.dumps(message, default=default_encode),
        'headers': {
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
    }


def lambda_handler(event, context):
    iot_data = boto3.client('iot-data', region_name=REGION)
    thing = parameter_parser(event, 'thingId')
    metric = parameter_parser(event, 'metric')
    resp = iot_data.get_thing_shadow(thingName=parameter_parser(event, 'thingId'))
    body = resp['payload']
    j = json.loads(body.read())
    if 'state' in j:
        if 'reported' in j['state']:
            if metric in j['state']['reported']:
                return response(j['state']['reported'][metric], 200)
    return response(None, 200)
