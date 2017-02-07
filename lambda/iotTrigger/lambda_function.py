import boto3
import json
from boto3.dynamodb.conditions import Key

REGION = 'us-east-1'
STATE = 'state'
REPORTED = 'reported'


def lambda_handler(event, context):
    iot_data = boto3.client('iot-data', region_name=REGION)
    key = ''
    if 'key' in event:
        key = event['key']
    elif 'serialNumber' in event:
        # interpret the presence of serial number to mean it is an IoT Button
        # calculate thing name via serial number
        key = "iotbutton_{}".format(event['serialNumber'])
        # turn batteryVoltage value into number for graphing / comparison
        if 'batteryVoltage' in event:
            event['batteryVoltage'] = int(event['batteryVoltage'].strip('mV'))
        # set iot shadow state
        payload = {STATE: {REPORTED: event}}
        iot_data.update_thing_shadow(thingName=key, payload=json.dumps(payload))
    # now process any triggers
    ddb = boto3.resource('dynamodb', region_name=REGION)
    table = ddb.Table('triggers')
    record = table.query(KeyConditionExpression=Key('key').eq(key))['Items']
    if len(record) > 0:
        if 'actions' in record[0]:
            for act in record[0]['actions']:
                if 'topic' in act:
                    if 'request' in act:
                        iot_data.publish(topic='{}'.format(act['topic']), qos=0, payload=json.dumps(act['request']))
                    else:
                        iot_data.publish(topic='{}'.format(act['topic']), qos=0, payload=json.dumps({}))
    return record
