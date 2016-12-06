from chalice import Chalice
import boto3
import json
from botocore.exceptions import ClientError
from chalice import NotFoundError
from boto3.dynamodb.conditions import Key
import decimal

app = Chalice(app_name='riot')
ddb = boto3.resource('dynamodb', region_name='us-east-1')


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


@app.route('/things', methods=['GET'])
def get_things():
    iot = boto3.client('iot', region_name='us-east-1')
    request = app.current_request
    if request.method == 'GET':
        try:
            response = iot.list_things()
            return response["things"]
        except ClientError as e:
            raise NotFoundError()


@app.route('/things/{thing}', methods=['GET'])
def get_thing(thing):
    iot_data = boto3.client('iot-data', region_name='us-east-1')
    request = app.current_request
    if request.method == 'GET':
        try:
            response = iot_data.get_thing_shadow(thingName=thing)
            body = response["payload"]
            return json.loads(body.read())
        except ClientError as e:
            raise NotFoundError(thing)


@app.route('/introspect')
def introspect():
    return app.current_request.to_dict()


@app.route('/metrics/{thing}', methods=['GET'])
def get_metrics(thing):
    table = ddb.Table('sensors')
    request = app.current_request
    params = app.current_request.query_params
    if request.method == 'GET':
        try:
            if 'gt' in params and 'lt' in params:
                response = table.query(
                    KeyConditionExpression=Key('source').eq(thing) & Key('timestamp').between(params['gt'], params['lt'])
                )
            elif 'gt' in params:
                response = table.query(
                    KeyConditionExpression=Key('source').eq(thing) & Key('timestamp').gte(params['gt'])
                )
            elif 'lt' in params:
                response = table.query(
                    KeyConditionExpression=Key('source').eq(thing) & Key('timestamp').lte(params['lt'])
                )
            else:
                response = table.query(
                    KeyConditionExpression=Key('source').eq(thing)
                )
            return json.dumps(response['Items'], cls=DecimalEncoder)
        except ClientError as e:
            raise NotFoundError()
