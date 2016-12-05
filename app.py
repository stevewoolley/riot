from chalice import Chalice
import boto3
import json
from botocore.exceptions import ClientError
from chalice import NotFoundError
from boto3.dynamodb.conditions import Key

app = Chalice(app_name='riot')

ddb = boto3.resource('dynamodb', region_name='us-east-1')


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

@app.route('/metrics/{thing}', methods=['GET'])
def get_metrics(thing):
    table = ddb.Table('sensors')
    response = table.query(
        KeyConditionExpression=Key('source').eq(thing)
    )
    return response['Items']
