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
    DDB = boto3.resource('dynamodb', region_name=REGION)
    thing = parameter_parser(event, 'thingId')
    metric = parameter_parser(event, 'metric')
    p_key = Key(SENSORS_PARTITION_KEY).eq(thing)  # query must be partitioned
    ex = {"#pkey": SENSORS_PARTITION_KEY, "#skey": SENSORS_SORT_KEY}
    pe = "#pkey, #skey, {}"
    item = []
    for idx, a in enumerate(PAYLOAD_PREFIX.format(metric).split('.')):
        ex["#n{}".format(idx)] = a
        item.append("#n{}".format(idx))
    resp = DDB.Table(SENSORS_TABLE).query(
        ScanIndexForward=SCAN_INDEX_FORWARD,
        KeyConditionExpression=p_key,
        FilterExpression=Attr(PAYLOAD_PREFIX.format(metric)).exists(),
        ExpressionAttributeNames=ex,
        ProjectionExpression=pe.format('.'.join(item))
    )
    if ITEMS in resp:
        # transform result to extract only interesting json key
        for item in resp[ITEMS]:
            tmp = item
            if PAYLOAD_PREFIX.format(metric) is not None:
                for i in PAYLOAD_PREFIX.format(metric).split('.'):
                    tmp = tmp.get(i)
                item[PAYLOAD_PREFIX.format(metric).split('.')[-1]] = tmp
            del item[SENSORS_PAYLOAD]
        #
        return response(resp[ITEMS], 200)
    else:
        return response(None, 200)
