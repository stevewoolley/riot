import boto3
import json
from boto3.dynamodb.conditions import Key

REGION = 'us-east-1'
STATE = 'state'
REPORTED = 'reported'
IOT_PREFIX = 'iotbutton_{}'
TOPIC = 'topic'
REQUEST = 'request'
KEY = 'key'


def lambda_handler(event, context):
    iot_data = boto3.client('iot-data', region_name=REGION)
    # handle special case for IoT Button
    key = None
    if 'serialNumber' in event:
        # interpret the presence of serial number to mean it is an IoT Button
        # calculate thing name via serial number
        key = IOT_PREFIX.format(event['serialNumber'])
        # turn batteryVoltage value into number for graphing / comparison
        if 'batteryVoltage' in event:
            event['batteryVoltage'] = int(event['batteryVoltage'].strip('mV'))
        # set iot shadow state
        payload = {STATE: {REPORTED: event}}
        iot_data.update_thing_shadow(thingName=key, payload=json.dumps(payload))
    # handle types of payload
    if TOPIC in event and REQUEST in event:
        iot_data.publish(topic='{}'.format(event[TOPIC]), qos=0, payload=json.dumps(event[REQUEST]))
    elif TOPIC in event:
        iot_data.publish(topic='{}'.format(event[TOPIC]), qos=0, payload=json.dumps({}))
    elif KEY in event:
        if key is None:
            key = event[KEY]
        ddb = boto3.resource('dynamodb', region_name=REGION)
        table = ddb.Table('triggers')
        record = table.query(KeyConditionExpression=Key(KEY).eq(key))['Items']
        if len(record) > 0:
            if 'actions' in record[0]:
                for act in record[0]['actions']:
                    if TOPIC in act:
                        if REQUEST in act:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps(act[REQUEST]))
                        else:
                            iot_data.publish(topic='{}'.format(act[TOPIC]), qos=0, payload=json.dumps({}))
