import boto3
from boto3.dynamodb.conditions import Key, Attr

REGION = 'us-east-1'
ITEMS = 'Items'


def lambda_handler(event, context):
    DDB = boto3.resource('dynamodb', region_name=REGION)
    return DDB.Table('actions').scan()[ITEMS]
