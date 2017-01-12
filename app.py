from chalice import Chalice
import boto3
import json
from botocore.exceptions import ClientError
from chalice import NotFoundError
from boto3.dynamodb.conditions import Key, Attr

REGION = 'us-east-1'
ITEMS = 'Items'
SENSORS_TABLE = 'sensors'
SENSORS_PARTITION_KEY = 'source'
SENSORS_SORT_KEY = 'timestamp'
SENSORS_PAYLOAD = 'payload'
PAYLOAD_PREFIX = 'payload.state.reported.{}'
ARCHIVE = 'archive.snerted.com'

app = Chalice(app_name='riot')
# app.debug = True

DDB = boto3.resource('dynamodb', region_name=REGION)


def dict_or(d, k1, k2):
    """used for conditional assignment on a dictionary"""
    if k1 in d:
        return d[k1]
    elif k2 in d:
        return d[k2]
    return None


def ddb_query(table, response_key, partition_key, partition_value, sort_key=None, params=None, attribute=None):
    """
        DynamoDb query using partition key, sort key, and attributes.
        Also gt, gte, lt, lte, between, begins_with on sort_key.
    """
    p_key = Key(partition_key).eq(partition_value)  # query must be partitioned
    if params is not None and sort_key is not None:
        if ('gt' in params or 'gte' in params) and ('lt' in params or 'lte' in params):
            p_key = p_key & Key(sort_key).between(dict_or(params, 'gt', 'gte'), dict_or(params, 'lt', 'lte'))
        else:
            if 'gt' in params:
                p_key = p_key & Key(sort_key).gt(params['gt'])
            elif 'gte' in params:
                p_key = p_key & Key(sort_key).gte(params['gte'])
            elif 'lt' in params:
                p_key = p_key & Key(sort_key).lt(params['lt'])
            elif 'lte' in params:
                p_key = p_key & Key(sort_key).lte(params['lte'])
            elif 'eq' in params:
                p_key = p_key & Key(sort_key).eq(params['eq'])
            elif 'bw' in params:
                p_key = p_key & Key(sort_key).begins_with(params['bw'])
    if attribute is not None:
        if sort_key is None:
            ex = {"#pkey": partition_key}
            pe = "#pkey, {}"
        else:
            ex = {"#pkey": partition_key, "#skey": sort_key}
            pe = "#pkey, #skey, {}"
        item = []
        for idx, a in enumerate(attribute.split('.')):
            ex["#n{}".format(idx)] = a
            item.append("#n{}".format(idx))
        response = table.query(
            KeyConditionExpression=p_key,
            FilterExpression=Attr(attribute).exists(),
            ExpressionAttributeNames=ex,
            ProjectionExpression=pe.format('.'.join(item))
        )
    else:
        response = table.query(
            KeyConditionExpression=p_key
        )
    if response_key in response:
        # transform result to extract only interesting json key
        for item in response[response_key]:
            tmp = item
            for i in attribute.split('.'):
                tmp = tmp.get(i)
            item[attribute.split('.')[-1]] = tmp
            del item[SENSORS_PAYLOAD]
        #
        return response[response_key]
    else:
        return []


@app.route('/things', methods=['GET'], api_key_required=True)
def get_things():
    iot = boto3.client('iot', region_name=REGION)
    try:
        response = iot.list_things()
        return response["things"]
    except ClientError as e:
        raise NotFoundError()


@app.route('/things/{thing}', methods=['GET'], api_key_required=True)
def get_thing(thing):
    iot_data = boto3.client('iot-data', region_name=REGION)
    try:
        response = iot_data.get_thing_shadow(thingName=thing)
        body = response[SENSORS_PAYLOAD]
        return json.loads(body.read())
    except ClientError as e:
        raise NotFoundError(thing)


@app.route('/introspect', api_key_required=True)
def introspect():
    return app.current_request.to_dict()


@app.route('/metrics/{thing}/{metric}', methods=['GET'], api_key_required=True)
def get_metrics(thing, metric):
    params = app.current_request.query_params
    try:
        return ddb_query(DDB.Table(SENSORS_TABLE), ITEMS, SENSORS_PARTITION_KEY, thing, SENSORS_SORT_KEY, params,
                         PAYLOAD_PREFIX.format(metric))
    except ClientError as e:
        raise NotFoundError(thing)


@app.route('/publish/{topic}', methods=['PUT'], api_key_required=True)
def publish(topic):
    request = app.current_request
    iot_data = boto3.client('iot-data', region_name=REGION)
    iot_data.publish(topic='/{}'.format(topic.replace('.', '/')), qos=0, payload=json.dumps(request.json_body))


@app.route('/archives/{prefix}', methods=['GET'], api_key_required=True)
def get_archives(prefix):
    s3 = boto3.client('s3')
    try:
        results = []
        for obj in s3.list_objects_v2(Bucket=ARCHIVE, Prefix=prefix)['Contents']:
            obj['url'] = s3.generate_presigned_url('get_object', Params={'Bucket': ARCHIVE, 'Key': obj['Key']})
            results.append(obj)
        return results
    except ClientError as e:
        raise NotFoundError()
