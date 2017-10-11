import boto3

REGION = 'us-east-1'
ITEMS = 'Items'


def lambda_handler(event, context):
    DDB = boto3.resource('dynamodb', region_name=REGION)
    return sorted(DDB.Table('triggers').scan()[ITEMS], key=lambda k: k['idx'])
