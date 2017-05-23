import boto3

REGION = 'us-east-1'
ITEMS = 'Items'
MOVIES_TABLE = 'movies'
MOVIES_PARTITION_KEY = 'id'
MOVIES_SORT_KEY = 'year'
LIMIT = 1500


def ddb_query(table, response_key):
    response = table.scan(Limit=LIMIT)
    return response[response_key]


def lambda_handler(event, context):
    DDB = boto3.resource('dynamodb', region_name=REGION)
    return sorted(ddb_query(DDB.Table(MOVIES_TABLE),
                            ITEMS))
