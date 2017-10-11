import boto3
from boto3.dynamodb.conditions import Key, Attr

REGION = 'us-east-1'
ITEMS = 'Items'
SENSORS_TABLE = 'sensors'
SENSORS_PARTITION_KEY = 'source'
SENSORS_SORT_KEY = 'timestamp'
SENSORS_PAYLOAD = 'payload'
PAYLOAD_PREFIX = 'payload.state.reported.{}'
SCAN_INDEX_FORWARD = False


def lambda_handler(event, context):
    DDB = boto3.resource('dynamodb', region_name=REGION)
    p_key = Key(SENSORS_PARTITION_KEY).eq(event['thing'])  # query must be partitioned
    ex = {"#pkey": SENSORS_PARTITION_KEY, "#skey": SENSORS_SORT_KEY}
    pe = "#pkey, #skey, {}"
    item = []
    for idx, a in enumerate(PAYLOAD_PREFIX.format(event['metric']).split('.')):
        ex["#n{}".format(idx)] = a
        item.append("#n{}".format(idx))
    response = DDB.Table(SENSORS_TABLE).query(
        ScanIndexForward=SCAN_INDEX_FORWARD,
        KeyConditionExpression=p_key,
        FilterExpression=Attr(PAYLOAD_PREFIX.format(event['metric'])).exists(),
        ExpressionAttributeNames=ex,
        ProjectionExpression=pe.format('.'.join(item))
    )
    if ITEMS in response:
        # transform result to extract only interesting json key
        for item in response[ITEMS]:
            tmp = item
            if PAYLOAD_PREFIX.format(event['metric']) is not None:
                for i in PAYLOAD_PREFIX.format(event['metric']).split('.'):
                    tmp = tmp.get(i)
                item[PAYLOAD_PREFIX.format(event['metric']).split('.')[-1]] = tmp
            del item[SENSORS_PAYLOAD]
        #
        return sorted(response[ITEMS],
                      key=lambda k: k['timestamp'])
    else:
        return []
